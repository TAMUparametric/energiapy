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
from ...core.nirop.errors import InconsistencyError
from ...core.nirop.warnings import InconsistencyWarning
from ...parameters.designators.mode import X
from ..scope.network import Network
from ..spatial._spatial import _Spatial
from ..temporal.scale import Scale

if TYPE_CHECKING:
    from ...core.aliases.is_input import IsInput, IsSptTmpInp


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
    def attr(self):
        """The Attributes of the Component"""

    @staticmethod
    @abstractmethod
    def bounds():
        """Bound attr of the Component"""

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
                    value_upd[_Dummy.N] = {key: val}

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
                if attr in self.attr.bounds():
                    value_upd[self.system.network] = spttmpmdeval[spt]
                else:
                    for loc in self.system.locations:
                        value_upd[loc] = spttmpmdeval[spt]
            else:
                value_upd[spt] = spttmpmdeval[spt]

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
        spttmpmdeval = self.make_modes(
            value=self.make_temporal(self.make_spatial(value)), attr=attr
        )
        # Then we fix the temporal disposition and warn if inconsistent
        spttmpmdeval = self.fix_temporal(spttmpmdeval, attr, ok_inconsistent)

        # The dummy values are replaced with actual values
        spttmpmdeval = self.replace_dummy_x(
            self.replace_dummy_t(self.replace_dummy_n(spttmpmdeval, attr))
        )

        return spttmpmdeval


class _ConsistentBnd(_Consistent):
    def make_bounds_consistent(self, attr: str, ok_inconsistent: bool):
        """Makes the input of bounds attributes consistent

        Args:
            attr (str): attribute for which input is being passed
            ok_inconsistent (bool): whether to fix dispositions or just warn.
        """
        # For bounds, if True (Big M) is given, it is converted to a list
        # i.e. it is set to be the upperbound
        setattr(
            self, attr, self.make_spttmpmde(getattr(self, attr), attr, ok_inconsistent)
        )


class _ConsistentCsh(_Consistent):
    def make_csh_consistent(self, attr: str, ok_inconsistent: bool):
        """Makes the input of cash attributes consistent

        Args:
            attr (str): attribute for which input is being passed
            ok_inconsistent (bool): whether to fix dispositions or just warn.

        """
        # adds cash as the main key
        setattr(
            self,
            attr,
            {
                self.system.cash: self.make_spttmpmde(
                    getattr(self, attr), attr, ok_inconsistent
                )
            },
        )


class _ConsistentLnd(_Consistent):
    def make_lnd_consistent(self, attr: str, ok_inconsistent: bool):
        """Makes the input of land attributes consistent

        Args:
            attr (str): attribute for which input is being passed
            ok_inconsistent (bool): whether to fix dispositions or just warn.
        """
        # adds land as the main key

        setattr(
            self,
            attr,
            {
                self.system.land: self.make_spttmpmde(
                    getattr(self, attr), attr, ok_inconsistent
                )
            },
        )


class _ConsistentNstd(_Consistent):
    def make_nstd_consistent(self, attr: str, ok_inconsistent: bool):
        """Makes the input of nested attributes consistent

        Args:
            attr (str): attribute for which input is being passed
            ok_inconsistent (bool): whether to fix dispositions or just warn.
        """
        # for inputs with multiple components, such as use and emission
        setattr(
            self,
            attr,
            {
                i: self.make_spttmpmde(j, attr, ok_inconsistent)
                for i, j in getattr(self, attr).items()
            },
        )


class _ConsistentNstdCsh(_Consistent):
    def make_nstd_csh_consistent(self, attr: str, ok_inconsistent: bool):
        """Makes the input of nested cash attributes consistent

        Args:
            attr (str): attribute for which input is being passed
            ok_inconsistent (bool): whether to fix dispositions or just warn.
        """
        # for expense inputs, where cash needs to be added to different components
        setattr(
            self,
            attr,
            {
                i: {self.system.cash: self.make_spttmpmde(j, attr, ok_inconsistent)}
                for i, j in getattr(self, attr).items()
            },
        )
