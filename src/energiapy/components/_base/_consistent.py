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
from warnings import warn
from typing import TYPE_CHECKING
from pandas import DataFrame

from ...core.isalias.inps.isinp import IsBndInp, IsExtInp, IsInp, IsSptTmp
from ...core.nirop.errors import InconsistencyError, check_attr
from ...core.nirop.warnings import InconsistencyWarning
from ..spatial._spatial import _Spatial
from ..spatial.network import Network
from ..temporal.mode import X
from ..temporal.scale import Scale
from ._dummy import _Dummy

if TYPE_CHECKING:
    from ...environ.engines.taskmaster import Chanakya
    from ...environ.blocks.system import System


class _Consistent(ABC):
    """Functions to make user data input into Datum

    Datum stores data in a consistent format
        {Spatial Disposition: {Temporal Disposition: {*Mode: value}}}

    Commodity data proivided at Operational Components are in the form:
        {Commodity: {Spatial Disposition: {Temporal Disposition: {*Mode: value}}}}

    *optional

    """

    @property
    @abstractmethod
    def system(self) -> System:
        """The System of the Component"""

    @property
    @abstractmethod
    def taskmaster(self) -> Chanakya:
        """Chanakya of the Scenario"""

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

    def boundbounds(self):
        """BoundBounds attributes"""
        return sorted(set(self.inputs()) & set(self.taskmaster.boundbounds()))

    @property
    def consistent(self):
        """Checks if the inputs have been made consistent"""
        return self._consistent

    @consistent.setter
    def consistent(self, value):
        self._consistent = value

    def upd_dict(self, value: IsInp, level: str) -> dict:
        """Returns an empty dict with the same keys as the input

        Args:
            value (IsInp): any input

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

    def make_spatial(self, value: IsInp) -> dict:
        """adds spatial disposition to input data if not there already
        defaults to Network

        Args:
            value (IsInp): any input
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

        return value_upd

    def make_temporal(self, value: IsInp) -> dict:
        """adds temporal disposition to input data if not there already
        puts a _Dummy.T temporarily

        Args:
            value (IsInp): any input

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

        return value_upd

    def make_modes(self, value: IsInp, attr: str) -> dict:
        """Recognizes and creates modes

        Args:
            value (IsInp): any input
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

        return value_upd

    def match_scale(
        self,
        val: IsExtInp | IsBndInp,
        tmp: Scale | _Dummy,
        attr: str,
    ) -> Scale:
        """checks whether a dataframe is given.
        if df, then sets to a matching scale or gives warning
        if not df, sets to parent scale

        Args:
            val (Any): Any incoming value
            tmp (Scale, _Dummy]): Temporal disposition
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
        self, spttmpmdeval: dict[dict, dict], attr: str, ok_inconsistent: bool
    ) -> dict:
        """Fixes the temporal disposition of the input

        Args:
            spttmpmdeval (dict): {Spatial: {Temporal: {Mode: value}}}
            attr (str): attr for which input is being passed
            ok_inconsistent (bool): whether to fix indices or just warn.

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

        return value_upd

    def spatialize(self, spttmpmdeval: dict, attr: str) -> dict:
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
        # across all spatial indices
        # 2. a Bound input such as buy, sell, etc.
        # if bound, the network limit can be independent of locations
        # infact, the locations values will sum up to the network value
        value_upd = {}
        for spt in spttmpmdeval.keys():
            if spt == _Dummy.N:
                if attr in self.bounds() + self.boundbounds():
                    value_upd[self.system.network] = spttmpmdeval[spt]
                else:

                    for loc in self.system.locations:
                        value_upd[loc] = spttmpmdeval[spt]
            else:
                value_upd[spt] = spttmpmdeval[spt]

        return value_upd

    def temporalize(self, spttmpmdeval: dict) -> dict:
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
                    value_upd[spt][self.system.horizon.root] = spttmpmdeval[spt][tmp]
                    del value_upd[spt][_Dummy.T]
                else:
                    value_upd[spt][tmp] = spttmpmdeval[spt][tmp]

        return value_upd

    def modize(self, spttmpmdeval: dict[dict, dict]) -> dict:
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

        return value_upd

    def make_spttmpmde(
        self, value: IsInp, attr: str, ok_inconsistent: bool
    ) -> IsSptTmp:
        """Uses all the above functions to make a consistent input

        Args:
            value (IsInp): any Input
            attr (str): attr for which input is being passed
            fix_bool (bool): whether to fix indices or just warn.
        Returns:
            IsSptTmpDict: {Spatial: {Temporal: {Mode: value}}} Always!!
        """

        # This makes it consistently in the format:
        # {Spatial: {Temporal: {Mode: value}}}
        # Spatial - Location, Linkage, Network, _Dummy.N
        # Temporal - Scale, _Dummy.T
        # Mode - X (Mode), _Dummy.X

        spttmpmdeval = self.make_modes(
            value=self.make_temporal(self.make_spatial(value)), attr=attr
        )
        # Then we fix the temporal disposition and warn if inconsistent
        spttmpmdeval = self.fix_temporal(spttmpmdeval, attr, ok_inconsistent)

        # The dummy values are replaced with actual values
        spttmpmdeval = self.modize(
            self.temporalize(self.spatialize(spttmpmdeval, attr))
        )

        return spttmpmdeval

    def cashify(self, attr: str, value: IsInp) -> dict:
        """If exact transaction input is given add Cash Component.

        Args:
            attr (str): attribute being passed
            value (IsInp): user input

        Returns:
            dict: {Cash: value}
        """
        if attr in self.taskmaster.transactions():
            value = {self.system.cash: value}

        return value

    def make_consistent(self, ok_inconsistent: bool):
        """Makes and sets input attributes consistent as SptTmpDict

        Args:
            ok_inconsistent (bool): whether to fix indices with warning or error out
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
                value = self.cashify(attr, value)
                return make_exact_consistent(value, attr, ok_inconsistent)

            if attr in self.bounds() + self.boundbounds():
                return make_bound_consistent(value, attr, ok_inconsistent)

        for attr in self.inputs():

            # This throws a CacodcarError if the attribute is not defined for the Component
            check_attr(component=self, attr=attr)

            value = getattr(self, attr)

            if value is None:
                continue

            setattr(self, attr, make_any_consistent(value, attr, ok_inconsistent))

            # if any(
            #     isinstance(self, cmp) for cmp in getattr(self.taskmaster, attr).other
            # ):
            #     # if the root of attribute is another Component
            #     # Then we need to iterate over the Components
            #     setattr(
            #         self,
            #         attr,
            #         {
            #             cmd: make_any_consistent(val, attr, ok_inconsistent)
            #             for cmd, val in value.items()
            #         },
            #     )
            # else:
            #     # else just set i

        setattr(self, 'consistent', True)
