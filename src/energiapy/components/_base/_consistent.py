"""Functions to make component input values in a consistent format"""

from __future__ import annotations

from operator import is_, is_not
from typing import TYPE_CHECKING
from warnings import warn

from pandas import DataFrame

from ..scope.network import Network
from ..temporal.scale import Scale
from ._spttmp import _Spatial

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsInput, IsSptTmpInput


class _Consistent:
    """Functions to make the input into a SpatioTemporalDict"""

    def make_consistent_spatial(self, value: IsInput) -> dict:
        """adds spatial dispostion to input data if not there already
        defaults to Network

        Args:
            value (IsInput): any input

        Returns:
            dict: ammended input dict
        """
        if not isinstance(value, dict):
            value_upd = {getattr(self, '_network'): value}

        else:
            value_upd = {}
            for i, j in value.items():
                if not isinstance(i, (_Spatial, Network)):
                    value_upd[getattr(self, '_network')] = {i: j}
                else:
                    value_upd[i] = j

        return value_upd

    def make_consistent_temporal(self, value: IsInput) -> dict:
        """adds temporal dispostion to input data if not there already
        puts a 't' temporarily

        Args:
            value (IsInput): any input

        Returns:
            dict: ammended input dict
        """
        value_upd = {i: {} for i in value.keys()}

        for i, j in value.items():
            if not isinstance(j, dict):
                value_upd[i]['t'] = j

            else:
                for k, l in j.items():
                    if not isinstance(k, Scale):
                        value_upd[i]['t'] = l
                    else:
                        value_upd[i][k] = l
        return value_upd

    def make_consistent_len(self, value: IsInput) -> dict:
        """checks whether a dataframe is given.
        if df, then sets to a matching scale or gives warning
        if not df, sets to parent scale

        Args:
            value (IsInput): any Input

        Returns:
            dict: ammended input dict
        """
        value_upd = {i: {k: {} for k in j.keys()} for i, j in value.items()}

        for i, j in value.items():
            for k, l in j.items():
                if isinstance(l, DataFrame):
                    scale_upd = getattr(self, '_horizon').match_scale(l)
                    if is_not(scale_upd, k):
                        if is_not(k, 't'):
                            warn(
                                f'{self}:Inconsistent temporal scale for {i} at {k}. Updating to {scale_upd}'
                            )
                        value_upd[i][scale_upd] = l
                        del value_upd[i][k]
                    else:
                        value_upd[i][k] = l
                else:
                    if is_(k, 't'):
                        value_upd[i][getattr(self, '_horizon').scales[0]] = l
                        del value_upd[i][k]
                    else:
                        value_upd[i][k] = l

        return value_upd

    def make_consistent_bounds(self, value: IsInput) -> dict:
        """checks whether some inputs are bounds
        if bounds, sets to the lowest matching scale

        Args:
            value (IsInput): any Input

        Returns:
            dict: ammended dict
        """
        value_upd = {i: {k: {} for k, l in j.items()} for i, j in value.items()}

        for i, j in value.items():
            for k, l in j.items():
                if isinstance(l, (list, tuple)):
                    scale_upd = sorted(
                        [getattr(self, '_horizon').match_scale(m) for m in l]
                    )[-1]

                    if is_not(scale_upd, k):
                        warn(
                            f'{self}:Inconsistent temporal scale for {i} at {k}. Updating to {scale_upd}'
                        )
                        value_upd[i][scale_upd] = l
                        del value_upd[i][k]
                    else:
                        value_upd[i][k] = l

                else:
                    value_upd[i][k] = l
        return value_upd

    def make_spttmpdict(self, value: IsInput) -> IsSptTmpInput:
        """Uses all the above functions to make a consistent input

        Args:
            value (IsInput): any Input

        Returns:
            IsSptTmpInput: {Spatial: {Temporal: value}}
        """
        if value:
            value = self.make_consistent_spatial(value)
            value = self.make_consistent_temporal(value)
            value = self.make_consistent_len(value)
            value = self.make_consistent_bounds(value)
        return value
