"""Functions to make component input values in a consistent format

This has been written in a very spread out manner for clarity

spt - spatial disposition
tmp - temporal disposition
x - operational mode

use is_not to compare dummy to existing Components (Scale, Location)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from operator import is_, is_not
from typing import TYPE_CHECKING
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
        # set network to a dummy _Dummy.N key for now
        if not isinstance(value, dict):
            value_upd = {_Dummy.N: value}
        else:
            # if already dictionary
            # check if the spatial disposition is given
            value_upd = {}
            for spt, tmp_val in value.items():
                # check if a spatial component is already given
                if isinstance(spt, _Spatial, Network):
                    # if yes, stick with it
                    value_upd[spt] = tmp_val
                else:
                    # else, we need to do some quick math
                    # the value can apply to:
                    # 1. an Exact input such as cost, emissions, etc.
                    # if exact, then the value is assumed to apply
                    # across all spatial dispositions
                    # 2. a Bound input such as buy, sell, etc.
                    # if bound, the network limit can be independent of locations
                    # infact, the locations values will sum up to the network value
                    # but we bothere will that later in ...
                    # for now
                    if _Dummy.N in value_upd:
                        value_upd = {
                            **value_upd[_Dummy.N],
                            **{spt: tmp_val},
                        }
                    else:
                        value_upd[_Dummy.N] = tmp_val
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

    def fix_scale(self, value: IsInput, attr: str, ok_inconsistent: bool) -> dict:
        """checks whether a dataframe is given.
        if df, then sets to a matching scale or gives warning
        if not df, sets to parent scale

        Args:
            value (IsInput): any Input
            attr (str): attr for which input is being passed
            fix_bool (bool): whether to fix dispositions or just warn.

        Returns:
            dict: Always {Spatial: {Temporal: {Mode: value}}} but with Temporal reflecting the True disposition
        """
        value_upd = self.upd_dict(value, 'spttmpx')

        for spt, tmp_x_val in value.items():
            for tmp, x_val in tmp_x_val.items():
                for x, val in x_val.items():
                    # if value is a DataFrame, check if the scale is consistent
                    if isinstance(val, DataFrame):
                        scale_upd = self.system.horizon.match_scale(val, self, attr)
                        if is_not(scale_upd, tmp):
                            # if not consistent
                            if is_not(tmp, _Dummy.T):

                                if ok_inconsistent:
                                    warn(
                                        InconsistencyWarning(
                                            self, attr, spt, tmp, scale_upd
                                        )
                                    )
                                else:
                                    raise InconsistencyError(
                                        self, attr, spt, tmp, scale_upd
                                    )

                            # update the scale
                            value_upd[spt][scale_upd] = x_val
                            # delete the old entry
                            del value_upd[spt][tmp]
                        else:
                            # if consistent, keep as is
                            value_upd[spt][tmp][x] = val
                    # if dummy set to root scale of Horizon
                    elif is_(tmp, _Dummy.T):
                        value_upd[spt][self.system.horizon.scales[0]] = x_val
                    else:
                        # if value is not a DataFrame, keep as is
                        value_upd[spt][tmp][x] = val

        return value_upd

    def fix_true(self, value: IsInput) -> dict:
        """checks whether the input value is True
        if True, makes a list [True]

        Args:
            value (IsInput): any Input
            attr (str): attr for which input is being passed

        Returns:
            dict: Always {Spatial: {Temporal: {Mode: value}}}, this however makes True to [True]
        """
        value_upd = self.upd_dict(value, 'spttmpx')
        for spt, tmp_x_val in value.items():
            for tmp, x_val in tmp_x_val.items():
                for x, val in x_val.items():
                    if val is True:
                        value_upd[spt][tmp][x] = [val]
                    else:
                        value_upd[spt][tmp][x] = val

        return value_upd

    def fix_bound_scales(
        self, value: IsInput, attr: str, ok_inconsistent: bool
    ) -> dict:
        """checks whether some inputs are bounds
        if bounds, sets to the lowest matching scale

        Args:
            value (IsInput): any Input
            attr (str): attr for which input is being passed
            fix_bool (bool): whether to fix dispositions or just warn.
        Returns:
            dict: Always {Spatial: {Temporal: {Mode: value}}}, this however checks lists [LB, UB]
        """
        value_upd = self.upd_dict(value, 'spttmpx')

        # note that you cant have True (Big M) inside bounds
        for spt, tmp_x_val in value.items():
            for tmp, x_val in tmp_x_val.items():
                for x, val in x_val.items():
                    # if list of , tuple of bounds. Check if both scales are same
                    if isinstance(val, (list, tuple)):
                        # if DataFrame and numeric, bring DataFrame to front
                        # determine the longer scale
                        scale_upd = sorted(
                            [
                                self.system.horizon.match_scale(m, self, attr)
                                for m in val
                            ],
                        )[-1]

                        if is_not(scale_upd, tmp) and not all(
                            isinstance(m, (float, int, str)) for m in val
                        ):
                            # only update the scale if there is a mix of DataFrame and Numeric or str (small M)
                            if ok_inconsistent:
                                warn(
                                    InconsistencyWarning(
                                        self, attr, spt, tmp, scale_upd
                                    )
                                )
                            else:
                                raise InconsistencyError(
                                    self, attr, spt, tmp, scale_upd
                                )

                            value_upd[spt][scale_upd] = x_val
                            del value_upd[spt][tmp]
                        else:
                            value_upd[spt][tmp][x] = val
                    else:
                        value_upd[spt][tmp][x] = val

        return value_upd

    def clean_up(self, value: IsInput) -> dict:
        """Cleans up the input, removes temporary _Dummy.T and _Dummy.X keys

        Args:
            value (IsInput): any Input

        Returns:
            dict: Always {Spatial: {Temporal: {Mode: value}}} but without _Dummy.T and _Dummy.X dummy keys
        """

        value_upd = self.upd_dict(value, 'spttmpx')

        for spt, tmp_x_val in value.items():
            for tmp, x_val in tmp_x_val.items():
                for x in x_val:
                    if is_(x, _Dummy.X):
                        value_upd[spt][tmp] = value[spt][tmp][x]
                    else:
                        value_upd[spt][tmp][x] = value[spt][tmp][x]
                if is_(tmp, _Dummy.T):
                    del value_upd[spt][tmp]

        return value_upd

    def make_spttmpdict(
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
        value = self.make_spatial(value)
        value = self.make_temporal(value)
        value = self.make_modes(value, attr)
        value = self.fix_scale(value, attr, ok_inconsistent)
        value = self.fix_true(value)
        value = self.fix_bound_scales(value, attr, ok_inconsistent)
        value = self.clean_up(value)

        return value


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
            self, attr, self.make_spttmpdict(getattr(self, attr), attr, ok_inconsistent)
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
                self.system.cash: self.make_spttmpdict(
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
                self.system.land: self.make_spttmpdict(
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
                i: self.make_spttmpdict(j, attr, ok_inconsistent)
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
                i: {self.system.cash: self.make_spttmpdict(j, attr, ok_inconsistent)}
                for i, j in getattr(self, attr).items()
            },
        )
