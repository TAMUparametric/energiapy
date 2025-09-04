"""Time"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..components.temporal.period import Period
from ..core.dimension import Dimension

if TYPE_CHECKING:
    from gana.block.program import Prg
    from gana.sets.index import I


@dataclass
class Time(Dimension):
    """Temporal representation of a system

    All time periods are attached to this object

    Attributes:
        model (Model): Model to which the representation belongs.
        name (str): Name of the model. Defaults to None.
        _indexed (I): The index set of Horizon. For easy call. Defaults to None.
        periods (list[Period]): List of time periods. Defaults to []

    Note:
        - name is generated based on the Class and Model name
        - periods are populated as the program is built.
        - _indexed is made the first time Time is indexed.
    """

    def __post_init__(self):
        self._indexed: I = None
        self.periods: list[Period] = []
        Dimension.__post_init__(self)

    @property
    def program(self) -> Prg:
        """Mathematical program"""
        return self.model.program

    @property
    def I(self) -> I:
        """gana index set (I)"""

        # time is indexed a little differently
        # instead of just being indexed at the set level,
        # an ordered index set is created
        if not self._indexed:
            _indexed = I(self.name, mutable=True, tag=f'Horizon of {self.model}')
            _indexed.name = self.name
            self._indexed = _indexed
        return self._indexed

    # -----------------------------------------------------
    #                    Helpers
    # -----------------------------------------------------

    @property
    def tree(self) -> list[Period]:
        """Return the tree of periods"""
        hrz = self.horizon

        return {int(hrz.howmany(prd)): prd for prd in self.periods}

    @property
    def sorted_periods(self) -> list[Period]:
        """Sorted periods from densest to sparsest"""
        return sorted(self.periods)

    def find(self, size: int | float) -> Period:
        """Find the period that has the length"""

        if not size in self.tree:
            # if no math make a default period
            _ = self.model.default_period(size=size)
        return self.tree[size]

    def split(self, period: Period) -> tuple[list[Period], list[Period]]:
        """Gives a list of periods which are denser and sparser than period"""

        periods = self.sorted_periods
        index = periods.index(period)
        return periods[:index], periods[index + 1 :]

    # -----------------------------------------------------
    #                    Superlatives
    # -----------------------------------------------------

    @property
    def horizon(self) -> Period:
        """The sparsest scale is treated as the horizon"""
        if self.periods:
            return self.sparsest
        # if nothing found, make a default period
        return self.model.default_period()

    @property
    def densest(self) -> Period:
        """The densest period"""
        if self.periods:
            return min(self.periods, key=lambda x: x.periods)

    @property
    def sparsest(self) -> Period:
        """The sparsest period"""
        if self.periods:
            return max(self.periods, key=lambda x: x.periods)

        # if not periods, make a default period
