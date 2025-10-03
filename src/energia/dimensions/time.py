"""Time"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING
from warnings import warn

from .._core._dimension import _Dimension
from ..components.temporal.modes import Modes
from ..components.temporal.periods import Periods

if TYPE_CHECKING:
    from gana.block.program import Prg


@dataclass
class Time(_Dimension):
    """
    Temporal representation of a system.

    All time periods are attached to this object.

    :param model: Model to which the representation belongs.
    :type model: Model

    :ivar name: Name of the dimension, generated based on the class and model name.
    :vartype name: str
    :ivar periods: List of time periods. Defaults to [].
    :vartype periods: list[Periods]
    :ivar modes: List of modes. Defaults to [].
    :vartype modes: list[Modes]

    .. note::
    - name is generated based on the Class and Model name
    - periods are populated as the program is built.
    - _indexed is made the first time Time is indexed.
    """

    def __post_init__(self):
        self.periods: list[Periods] = []
        self.modes: list[Modes] = []
        _Dimension.__post_init__(self)

    @cached_property
    def program(self) -> Prg:
        """Mathematical program"""
        return self.model.program

    # -----------------------------------------------------
    #                    Helpers
    # -----------------------------------------------------

    @property
    def tree(self) -> list[Periods]:
        """Return the tree of periods"""
        hrz = self.horizon

        return {int(hrz.howmany(prd)): prd for prd in self.periods}

    @property
    def sorted_periods(self) -> list[Periods]:
        """Sorted periods from densest to sparsest"""
        return sorted(self.periods)

    def find(self, size: int | float) -> Periods:
        """Find the period that has the length"""

        if size not in self.tree:
            # if no math make a default period
            warn(
                f"{size} does not match the size of any data set passed, generating 't{size}'.)",
            )
            _ = self.model.default_period(size=size)

        return self.tree[size]

    def split(self, period: Periods) -> tuple[list[Periods], list[Periods]]:
        """Gives a list of periods which are denser and sparser than period"""

        periods = self.sorted_periods
        index = periods.index(period)
        return periods[:index], periods[index + 1 :]

    # -----------------------------------------------------
    #                    Superlatives
    # -----------------------------------------------------

    @property
    def horizon(self) -> Periods:
        """The sparsest scale is treated as the horizon"""
        if self.periods:
            return self.sparsest
        # if nothing found, make a default period
        return self.model.default_period()

    @property
    def densest(self) -> Periods:
        """The densest period"""
        if self.periods:
            return min(self.periods, key=lambda x: x.periods)
        return self.horizon

    @property
    def sparsest(self) -> Periods:
        """The sparsest period"""
        if self.periods:
            return max(self.periods, key=lambda x: x.periods)
        return self.horizon
