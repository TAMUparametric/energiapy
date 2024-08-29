"""Functions to make component input values in a consistent format

This has been written in a very spread out manner for clarity

spt - spatial disposition
tmp - temporal disposition
x - operational mode

use is_not to compare dummy to existing Components (Scale, Location)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from operator import is_not
from typing import TYPE_CHECKING, Any, Union
from warnings import warn

from pandas import DataFrame

from ...core._handy._enums import _Dummy
from ...core.nirop.errors import InconsistencyError, check_attr
from ...core.nirop.warnings import InconsistencyWarning
from ...parameters.designators.mode import X
from ..scope.network import Network
from ..spatial._spatial import _Spatial
from ..temporal.scale import Scale

if TYPE_CHECKING:
    from ...core.aliases.is_input import IsInput, IsSptTmpInp

# set to True if you want the output printed at every step
TESTING = False


def pr_op(op: str, wh: str):
    """prints output if TESTING is True

    Args:
        t (bool): TESTING flag
        op (str): output
        wh (str): what is being printed
    """
    if TESTING:
        print()
        print(f'{wh}: {op}')


class _Consistent(ABC):
    """Functions to make the input into a Consistent dictionary
    to be used to make _SptTmpDict
    """

    @property
    @abstractmethod
    def system(self):
        """The System of the Component"""

    @property
    @abstractmethod
    def taskmaster(self):
        """TaskMaster of the Scenario"""

    @staticmethod
    @abstractmethod
    def inputs():
        """Input attrs of the Component"""

    def exacts(self):
        """Exact attributes"""
        return sorted(set(self.inputs()) & set(self.taskmaster.exacts()))

    def bounds(self):
        """Bounds attributes"""
        return sorted(set(self.inputs()) & set(self.taskmaster.bounds()))

    @property
    def consistent(self):
        """Checks if the inputs have been made consistent"""
        return self._consistent

    @consistent.setter
    def consistent(self, value):
        self._consistent = value

    def upd_dict(self, value: IsInput, level: str) -> dict:
        """Returns an empty dict with the same keys as the input

        Args:
            value (IsInput): any input

        Returns:
            dict: empty dict with same keys as input
        """
        if level == 'spt':
            return {spt: {} for spt in value}

        if level == 'spttmp':
            return {spt: {tmp: {} for tmp in tmp_val} for spt, tmp_val in value.items()}

        if level == 'spttmpx':
            return {
                spt: {tmp: {x: {} for x in x_val} for tmp, x_val in tmp_x_val.items()}
                for spt, tmp_x_val in value.items()
            }

    def make_spatial(self, value: IsInput) -> dict:
        """adds spatial disposition to input data if not there already
        defaults to Network

        Args:
            value (IsInput): any input
            attr (str): attr for which input is being passed

        Returns:
            dict: Always {Spatial (Location, Linkage, Network): Something}
        """
        # There has to be a spatial disposition
        # if not, then the network is assumed
        # set network to a dummy 'n' key for now
        if not isinstance(value, dict):
            value_upd = {_Dummy.N: value}
        else:
            # if already dictionary
            # check if the spatial disposition is given
            value_upd = {}
            for key, val in value.items():
                # check if a spatial component is already given
                if isinstance(key, (_Spatial, Network)):
                    # if yes, stick with it
                    value_upd[key] = val
                else:
                    # else, add a _Dummy.N for now
                    value_upd[_Dummy.N] = val

        pr_op(value_upd, 'make_spatial')

        return value_upd

    def make_temporal(self, value: IsInput) -> dict:
        """adds temporal disposition to input data if not there already
        puts a _Dummy.T temporarily

        Args:
            value (IsInput): any input

        Returns:
            dict: Always {Spatial: {Temporal (Scale): Something}}
        """

        value_upd = self.upd_dict(value, 'spt')

        for spt, tmpx_val in value.items():
            if not isinstance(tmpx_val, dict):
                # The _Dummy.T is temporary, replaced by root scale of Horizon later
                value_upd[spt][_Dummy.T] = tmpx_val
            else:
                for tmpx, val in tmpx_val.items():
                    if isinstance(tmpx, Scale):
                        value_upd[spt][tmpx] = val
                    elif isinstance(tmpx, X):
                        value_upd[spt][_Dummy.T] = tmpx_val
                    else:
                        value_upd[spt][_Dummy.T] = val

        pr_op(value_upd, 'make_temporal')

        return value_upd

    def make_modes(self, value: IsInput, attr: str) -> dict:
        """Recognizes and creates modes

        Args:
            value (IsInput): any input
            attr (str): attr for which input is being passed

        Returns:
            dict: Always {Spatial: {Temporal: {Mode (X): value}}}

        """
        value_upd = self.upd_dict(value, 'spttmp')

        for spt, tmp_val in value.items():
            for tmp, val in tmp_val.items():
                if isinstance(val, dict) and all(isinstance(x, X) for x in val):
                    value_upd[spt][tmp] = {
                        a.personalize(opn=self, attr=attr): b for a, b in val.items()
                    }
                else:
                    value_upd[spt][tmp] = {
                        _Dummy.X: value[spt][tmp]
                    }  # put a dummy mode temporarily

        pr_op(value_upd, 'make_modes')

        return value_upd

    def match_scale(
        self,
        val: Any,
        tmp: Union[Scale, _Dummy],
        attr: str,
    ) -> Scale:
        """checks whether a dataframe is given.
        if df, then sets to a matching scale or gives warning
        if not df, sets to parent scale

        Args:
            val (Any): Any incoming value
            tmp (Union[Scale, _Dummy]): Temporal disposition
            attr (str): attr for which input is being passed
        Returns:
            Scale: Updated scale
        """

        # if value is a DataFrame, check if the scale is consistent
        if isinstance(val, DataFrame):
            return self.system.horizon.match_scale(val, self, attr)
        elif isinstance(val, (list, tuple)) and any(
            isinstance(v, DataFrame) for v in val
        ):
            return sorted(self.match_scale(v, self, attr) for v in val)[-1]
        else:
            return tmp

    def fix_temporal(
        self, spttmpmdeval: dict, attr: str, ok_inconsistent: bool
    ) -> dict:
        """Fixes the temporal disposition of the input

        Args:
            spttmpmdeval (dict): {Spatial: {Temporal: {Mode: value}}}
            attr (str): attr for which input is being passed
            ok_inconsistent (bool): whether to fix dispositions or just warn.

        Returns:
            dict: {Spatial: {Temporal: {Mode: value}}} but with scales checked

        """

        value_upd = self.upd_dict(spttmpmdeval, 'spttmpx')
        for spt, tmpmdeval in spttmpmdeval.items():
            for tmp, mdeval in tmpmdeval.items():
                for val in mdeval.values():
                    scl_upd = self.match_scale(val, tmp, attr)
                    if is_not(scl_upd, tmp):
                        if ok_inconsistent:
                            if not isinstance(tmp, _Dummy):
                                warn(
                                    InconsistencyWarning(self, attr, spt, tmp, scl_upd)
                                )
                        else:
                            raise InconsistencyError(self, attr, spt, tmp, scl_upd)
                        value_upd[spt][scl_upd] = spttmpmdeval[spt][tmp]
                        del value_upd[spt][tmp]
                    else:
                        value_upd[spt][tmp] = spttmpmdeval[spt][tmp]

        pr_op(value_upd, 'fix_temporal')

        return value_upd

    def replace_dummy_n(self, spttmpmdeval: dict, attr: str) -> dict:
        """Replaces the dummy N in the input

        Args:
            spttmpmdeval (dict): {Spatial: {Temporal: {Mode: value}}}
            attr (str): attr for which input is being passed

        Returns:
            dict: {Spatial: {Temporal: {Mode: value}}}
        """

        # The rules are as follows:
        # 1. an Exact input such as cost, emissions, etc.
        # if exact, then the value is assumed to apply
        # across all spatial dispositions
        # 2. a Bound input such as buy, sell, etc.
        # if bound, the network limit can be independent of locations
        # infact, the locations values will sum up to the network value
        value_upd = {}
        for spt in spttmpmdeval.keys():
            if spt == _Dummy.N:
                if attr in self.taskmaster.bounds():
                    value_upd[self.system.network] = spttmpmdeval[spt]
                else:
                    for loc in self.system.locations:
                        value_upd[loc] = spttmpmdeval[spt]
            else:
                value_upd[spt] = spttmpmdeval[spt]

        pr_op(value_upd, 'replace_dummy_n')

        return value_upd

    def replace_dummy_t(self, spttmpmdeval: dict) -> dict:
        """Replaces the dummy T in the input

        Args:
            spttmpmdeval (dict): {Spatial: {Temporal: {Mode: value}}}

        Returns:
            dict: {Spatial: {Temporal: {Mode: value}}}
        """

        value_upd = self.upd_dict(spttmpmdeval, 'spttmp')
        for spt, tmpmdeval in spttmpmdeval.items():
            for tmp in tmpmdeval.keys():
                if tmp == _Dummy.T:
                    value_upd[spt][self.system.scales[0]] = spttmpmdeval[spt][tmp]
                    del value_upd[spt][_Dummy.T]
                else:
                    value_upd[spt][tmp] = spttmpmdeval[spt][tmp]

        pr_op(value_upd, 'replace_dummy_t')

        return value_upd

    def replace_dummy_x(self, spttmpmdeval: dict) -> dict:
        """Replaces the dummy X in the input

        Args:
            spttmpmdeval (dict): {Spatial: {Temporal: {Mode: value}}}

        Returns:
            dict: {Spatial: {Temporal: {Mode: value}}} or {Spatial: {Temporal: value}}
        """

        value_upd = self.upd_dict(spttmpmdeval, 'spttmpx')
        for spt, tmpx_val in spttmpmdeval.items():
            for tmp, x_val in tmpx_val.items():
                for x in x_val.keys():
                    if x == _Dummy.X:
                        # {Spatial: {Temporal: value}}
                        value_upd[spt][tmp] = spttmpmdeval[spt][tmp][x]
                    else:
                        # {Spatial: {Temporal: {Mode: value}}}
                        value_upd[spt][tmp][x] = spttmpmdeval[spt][tmp][x]

        pr_op(value_upd, 'replace_dummy_x')

        return value_upd

    def make_spttmpmde(
        self, value: IsInput, attr: str, ok_inconsistent: bool
    ) -> IsSptTmpInp:
        """Uses all the above functions to make a consistent input

        Args:
            value (IsInput): any Input
            attr (str): attr for which input is being passed
            fix_bool (bool): whether to fix dispositions or just warn.
        Returns:
            IsSptTmpInp: {Spatial: {Temporal: {Mode: value}}} Always!!
        """

        # This makes it consistently in the format:
        # {Spatial: {Temporal: {Mode: value}}}
        # Spatial - Location, Linkage, Network, _Dummy.N
        # Temporal - Scale, _Dummy.T
        # Mode - X (Mode), _Dummy.X

        pr_op(value, 'make_spatial')

        spttmpmdeval = self.make_modes(
            value=self.make_temporal(self.make_spatial(value)), attr=attr
        )
        # Then we fix the temporal disposition and warn if inconsistent
        spttmpmdeval = self.fix_temporal(spttmpmdeval, attr, ok_inconsistent)

        # The dummy values are replaced with actual values
        spttmpmdeval = self.replace_dummy_x(
            self.replace_dummy_t(self.replace_dummy_n(spttmpmdeval, attr))
        )

        pr_op(spttmpmdeval, 'make_spttmpmde')

        return spttmpmdeval

    def make_commodity(self, attr: str, value: IsInput) -> dict:
        """If exact input is given, checks if commodity is given.

        If not sets one for Cash and Land

        Args:
            attr (str): attribute being passed
            value (IsInput): user input

        Returns:
            dict: {Commodity: value}
        """

        if attr in self.taskmaster.expenses():
            value = {self.system.cash: value}

        if attr == 'use_land':
            value = {self.system.land: value}

        pr_op(value, 'make_commodity')

        return value

    def make_consistent(self, ok_inconsistent: bool):
        """Makes the inputs consistent as SptTmpInput

        Args:
            ok_inconsistent (bool): whether to fix dispositions with warning or error out
        """

        def make_exact_consistent(value: dict, attr: str, ok_inconsistent: bool):
            """Makes Exact inputs consistent"""

            # Exact inputs always have some commodity as the first key
            # Thus,  we iterate over the commodities (cmd)
            return {
                cmd: self.make_spttmpmde(val, attr, ok_inconsistent)
                for cmd, val in value.items()
            }

        def make_bound_consistent(value: dict, attr: str, ok_inconsistent: bool):
            """Makes Bound inputs consistent"""
            # Bounds are defined for the Component itself
            # or can be declared at other components

            return self.make_spttmpmde(value, attr, ok_inconsistent)

        def make_any_consistent(value: dict, attr: str, ok_inconsistent: bool):
            """Make either exact or bound consistent"""

            if attr in self.exacts():
                # for Cash and Land, these are added, Resources, Materials, Emissions need to be specified
                value = self.make_commodity(attr, value)
                pr_op(value, 'make_exact_consistent')
                return make_exact_consistent(value, attr, ok_inconsistent)

            if attr in self.bounds():
                pr_op(value, 'make_bound_consistent')
                return make_bound_consistent(value, attr, ok_inconsistent)

        for attr in self.inputs():

            # This throws a CacodcarError if the attribute is not defined for the Component
            check_attr(component=self, attr=attr)

            value = getattr(self, attr)

            if value is None:
                continue

            if any(
                isinstance(self, cmp) for cmp in getattr(self.taskmaster, attr).other
            ):
                # if this is an attribute of another Component
                # Then we need to iterate over the Components
                setattr(
                    self,
                    attr,
                    {
                        cmd: make_any_consistent(val, attr, ok_inconsistent)
                        for cmd, val in value.items()
                    },
                )
            else:
                # else just set i
                setattr(self, attr, make_any_consistent(value, attr, ok_inconsistent))

            pr_op(value, 'make_consistent')

        setattr(self, 'consistent', True)

        # if type(self) in getattr(self.taskmaster, attr).other:
