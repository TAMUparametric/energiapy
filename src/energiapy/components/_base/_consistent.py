"""Functions to make component input values in a consistent format"""

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
    """Functions to make the input into a SpatioTemporalDict"""

    @property
    @abstractmethod
    def _horizon(self):
        """The Horizon of the Component"""

    @property
    @abstractmethod
    def _network(self):
        """The Network of the Component"""

    def make_consistent_spatial(self, value: IsInput) -> dict:
        """adds spatial dispostion to input data if not there already
        defaults to Network

        Args:
            value (IsInput): any input

        Returns:
            dict: ammended input dict
        """

        if not isinstance(value, dict):
            value_upd = {self._network: value}

        else:
            value_upd = {}
            for spt, tmp_val in value.items():
                if not isinstance(spt, (_Spatial, Network)):
                    if self._network in value_upd:
                        value_upd[self._network] = {
                            **value_upd[self._network],
                            **{spt: tmp_val},
                        }
                    else:
                        value_upd[self._network] = {spt: tmp_val}
                else:
                    value_upd[spt] = tmp_val

        return value_upd

    def make_consistent_temporal(self, value: IsInput) -> dict:
        """adds temporal dispostion to input data if not there already
        puts a 't' temporarily

        Args:
            value (IsInput): any input

        Returns:
            dict: ammended input dict
        """
        value_upd = {spt: {} for spt in value.keys()}

        for spt, tmp_val in value.items():
            if not isinstance(tmp_val, dict):
                value_upd[spt]['t'] = tmp_val

            else:
                for tmp, val in tmp_val.items():
                    if not isinstance(tmp, Scale):
                        value_upd[spt]['t'] = val
                    else:
                        value_upd[spt][tmp] = val
        return value_upd

    def make_consistent_len(self, value: IsInput, attr: str) -> dict:
        """checks whether a dataframe is given.
        if df, then sets to a matching scale or gives warning
        if not df, sets to parent scale

        Args:
            value (IsInput): any Input
            attr (str): attr for which input is being passed

        Returns:
            dict: ammended input dict
        """
        value_upd = {
            spt: {tmp: {} for tmp in tmp_val.keys()} for spt, tmp_val in value.items()
        }
        for spt, tmp_val in value.items():
            for tmp, val in tmp_val.items():
                if isinstance(val, DataFrame):
                    scale_upd = self._horizon.match_scale(val)
                    if is_not(scale_upd, tmp):
                        if is_not(tmp, 't'):
                            warn(
                                f'{self}.{attr}:Inconsistent temporal scale for {spt} at {tmp}. Updating to {scale_upd}',
                            )
                        value_upd[spt][scale_upd] = val
                        del value_upd[spt][tmp]
                    else:
                        value_upd[spt][tmp] = val
                elif is_(tmp, 't'):
                    value_upd[spt][self._horizon.scales[0]] = val
                    del value_upd[spt][tmp]
                else:
                    value_upd[spt][tmp] = val

        return value_upd

    def make_consistent_bounds(self, value: IsInput, attr: str) -> dict:
        """checks whether some inputs are bounds
        if bounds, sets to the lowest matching scale

        Args:
            value (IsInput): any Input
            attr (str): attr for which input is being passed

        Returns:
            dict: ammended dict
        """
        value_upd = {
            spt: {tmp: {} for tmp, val in tmp_val.items()}
            for spt, tmp_val in value.items()
        }

        for spt, tmp_val in value.items():
            for tmp, val in tmp_val.items():

                if isinstance(val, (list, tuple)):
                    scale_upd = sorted(
                        [self._horizon.match_scale(m) for m in val],
                    )[-1]

                    if is_not(scale_upd, tmp) and not all(
                        isinstance(m, (float, int)) for m in val
                    ):  # only update the scale if there is no float or int in the list
                        warn(
                            f'{self}.{attr}:Inconsistent temporal scale for {spt} at {tmp}. Updating to {scale_upd}',
                        )
                        value_upd[spt][scale_upd] = val
                        del value_upd[spt][tmp]
                    else:
                        value_upd[spt][tmp] = val

                else:
                    value_upd[spt][tmp] = val
        return value_upd

    def make_consistent_modes(self, value: IsInput, attr: str) -> dict:
        """Recognizes and creates modes

        Args:
            value (IsInput): any input
            attr (str): attr for which input is being passed

        Returns:
            dict: ammended input dict

        """
        value_upd = {i: {k: {} for k in j.keys()} for i, j in value.items()}

        for i, j in value.items():
            for k, l in j.items():
                if isinstance(l, dict) and all(isinstance(x, X) for x in l):
                    value_upd[i][k] = {
                        a.personalize(opn=self, attr=attr): b for a, b in value.items()
                    }
                else:
                    value_upd = value
        return value_upd

    def make_spttmpdict(self, value: IsInput, attr: str) -> IsSptTmpInput:
        """Uses all the above functions to make a consistent input

        Args:
            value (IsInput): any Input
            attr (str): attr for which input is being passed

        Returns:
            IsSptTmpInput: {Spatial: {Temporal: value}}
        """
        if value is not None:
            spt_val = self.make_consistent_spatial(value)
            spttmp_val = self.make_consistent_temporal(spt_val)
            spttmpx_val = self.make_consistent_modes(spttmp_val, attr)

            for spt, tmp in spttmp_done.items():

                value = self.make_consistent_len(value, attr)
                value = self.make_consistent_bounds(value, attr)

        return value
