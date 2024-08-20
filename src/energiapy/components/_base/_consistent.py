"""Functions to make component input values in a consistent format

This has been written in a very spread out manner for clarity

spt - spatial disposition
tmp - temporal disposition
x - operational mode
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from operator import is_, is_not
from typing import TYPE_CHECKING
from warnings import warn

from pandas import DataFrame

from ...parameters.designators.mode import X
from ..scope.network import Network
from ..spatial._spatial import _Spatial
from ..temporal.scale import Scale

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsInput, IsSptTmpInput


class _Consistent(ABC):
    """Functions to make the input into a Consistent dictionary
    to be used to make _SptTmpDict

    """

    @property
    @abstractmethod
    def system(self):
        """The System of the Component"""

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

        Returns:
            dict: Always {Spatial (Location, Linkage, Network): Something}
        """

        if not isinstance(value, dict):
            value_upd = {self.system.network: value}
        else:
            value_upd = {}
            for spt, tmp_val in value.items():
                if not isinstance(spt, (_Spatial, Network)):
                    if self.system.network in value_upd:
                        value_upd[self.system.network] = {
                            **value_upd[self.system.network],
                            **{spt: tmp_val},
                        }
                    else:
                        value_upd[self.system.network] = {spt: tmp_val}
                else:
                    value_upd[spt] = tmp_val

        return value_upd

    def make_temporal(self, value: IsInput) -> dict:
        """adds temporal disposition to input data if not there already
        puts a 't' temporarily

        Args:
            value (IsInput): any input

        Returns:
            dict: Always {Spatial: {Temporal (Scale): Something}}
        """

        value_upd = self.upd_dict(value, 'spt')

        for spt, tmpx_val in value.items():
            if not isinstance(tmpx_val, dict):
                # The 't' is temporary, replaced by root scale of Horizon later
                value_upd[spt]['t'] = tmpx_val
            else:
                for tmpx, val in tmpx_val.items():
                    if isinstance(tmpx, Scale):
                        value_upd[spt][tmpx] = val
                    elif isinstance(tmpx, X):
                        value_upd[spt]['t'] = tmpx_val
                    else:
                        value_upd[spt]['t'] = val

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
                        'x': value[spt][tmp]
                    }  # put a dummy mode temporarily

        return value_upd

    def fix_scale(self, value: IsInput, attr: str) -> dict:
        """checks whether a dataframe is given.
        if df, then sets to a matching scale or gives warning
        if not df, sets to parent scale

        Args:
            value (IsInput): any Input
            attr (str): attr for which input is being passed

        Returns:
            dict: Always {Spatial: {Temporal: {Mode: value}}} but with Temporal reflecting the True disposition
        """
        value_upd = self.upd_dict(value, 'spttmpx')

        for spt, tmp_x_val in value.items():
            for tmp, x_val in tmp_x_val.items():
                for x, val in x_val.items():
                    if isinstance(val, DataFrame):
                        scale_upd = self.system.horizon.match_scale(val)
                        if is_not(scale_upd, tmp):
                            if is_not(tmp, 't'):
                                warn(
                                    f'{self}.{attr}:Inconsistent temporal scale for {spt} at {tmp}. Updating to {scale_upd}',
                                )
                            value_upd[spt][scale_upd] = x_val
                            del value_upd[spt][tmp]
                        else:
                            value_upd[spt][tmp][x] = val
                    elif is_(tmp, 't'):
                        value_upd[spt][self.system.horizon.scales[0]] = x_val
                    else:
                        value_upd[spt][tmp][x] = val

        return value_upd

    def fix_bound_scales(self, value: IsInput, attr: str) -> dict:
        """checks whether some inputs are bounds
        if bounds, sets to the lowest matching scale

        Args:
            value (IsInput): any Input
            attr (str): attr for which input is being passed

        Returns:
            dict: Always {Spatial: {Temporal: {Mode: value}}}, this however checks lists [LB, UB]
        """
        value_upd = self.upd_dict(value, 'spttmpx')

        for spt, tmp_x_val in value.items():
            for tmp, x_val in tmp_x_val.items():
                for x, val in x_val.items():
                    if isinstance(val, (list, tuple)):
                        scale_upd = sorted(
                            [self.system.horizon.match_scale(m) for m in val],
                        )[-1]

                        if is_not(scale_upd, tmp) and not all(
                            isinstance(m, (float, int)) for m in val
                        ):  # only update the scale if there is no float or int in the list
                            warn(
                                f'{self}.{attr}:Inconsistent temporal scale for {spt} at {tmp}. Updating to {scale_upd}',
                            )
                            value_upd[spt][scale_upd] = x_val
                            del value_upd[spt][tmp]
                        else:
                            value_upd[spt][tmp][x] = val
                    else:
                        value_upd[spt][tmp][x] = val

        return value_upd

    def clean_up(self, value: IsInput) -> dict:
        """Cleans up the input, removes temporary 't' and 'x' keys

        Args:
            value (IsInput): any Input

        Returns:
            dict: Always {Spatial: {Temporal: {Mode: value}}} but without 't' and 'x' dummy keys
        """

        value_upd = self.upd_dict(value, 'spttmpx')

        for spt, tmp_x_val in value.items():
            for tmp, x_val in tmp_x_val.items():
                for x in x_val:
                    if is_(x, 'x'):
                        value_upd[spt][tmp] = value[spt][tmp][x]
                    else:
                        value_upd[spt][tmp][x] = value[spt][tmp][x]
                if is_(tmp, 't'):
                    del value_upd[spt][tmp]

        return value_upd

    def make_spttmpdict(self, value: IsInput, attr: str) -> IsSptTmpInput:
        """Uses all the above functions to make a consistent input

        Args:
            value (IsInput): any Input
            attr (str): attr for which input is being passed

        Returns:
            IsSptTmpInput: {Spatial: {Temporal: {Mode: value}}} Always!!
        """
        value = self.make_spatial(value)
        value = self.make_temporal(value)
        value = self.make_modes(value, attr)
        value = self.fix_scale(value, attr)
        value = self.fix_bound_scales(value, attr)
        value = self.clean_up(value)

        return value


class _ConsistentBnd(_Consistent):
    def make_bounds_consistent(self, attr: str):
        """Makes the input of bounds attributes consistent"""
        setattr(self, attr, self.make_spttmpdict(getattr(self, attr), attr))


class _ConsistentCsh(_Consistent):
    def make_csh_consistent(self, attr: str):
        """Makes the input of cash attributes consistent"""
        # adds cash as the main key
        setattr(
            self,
            attr,
            {self.system.cash: self.make_spttmpdict(getattr(self, attr), attr)},
        )


class _ConsistentLnd(_Consistent):
    def make_lnd_consistent(self, attr: str):
        """Makes the input of land attributes consistent"""
        # adds land as the main key

        setattr(
            self,
            attr,
            {self.system.land: self.make_spttmpdict(getattr(self, attr), attr)},
        )


class _ConsistentNstd(_Consistent):
    def make_nstd_consistent(self, attr: str):
        """Makes the input of nested attributes consistent"""
        # for inputs with multiple components, such as use and emission
        setattr(
            self,
            attr,
            {i: self.make_spttmpdict(j, attr) for i, j in getattr(self, attr).items()},
        )


class _ConsistentNstdCsh(_Consistent):
    def make_nstd_csh_consistent(self, attr: str):
        """Makes the input of nested cash attributes consistent"""
        # for expense inputs, where cash needs to be added to different components
        setattr(
            self,
            attr,
            {
                i: {self.system.cash: self.make_spttmpdict(j, attr)}
                for i, j in getattr(self, attr).items()
            },
        )
