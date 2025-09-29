"""Temporal Lag"""

from __future__ import annotations

from dataclasses import dataclass
from operator import is_
from typing import TYPE_CHECKING, Self

from ...core.name import Name

if TYPE_CHECKING:
    from gana.sets.index import I

    from ...modeling.indices.domain import Domain
    from .periods import Periods


@dataclass
class Lag(Name):
    """A number of temporal Periods

    Attributes:
        label (str): Label of the component, used for plotting. Defaults to None.
        of (Periods): Periods to lag. Defaults to None.
        periods (int | float): Number of periods to lag. Defaults to 1.
        name (str): generated based on the number of periods
        domains (list[Domain]): List of Domains, lag features in. Defaults to [].

    Note:
        - name is generated post init
        - domains are set as the program is built
    """

    of: Periods = None
    periods: int | float = 1

    def __post_init__(self):
        self.name = f'-{self.periods}{self.of}'
        self.domains: list[Domain] = []
        self.constraints: list[str] = []

    @property
    def I(self) -> I:
        """Index set of period - period
        Basically,
        if t is set of hours and lag is 5
        this returns the set of t - 5
        i.e. an offset of 5 hours
        """
        return self.of.I - self.periods

    @property
    def horizon(self) -> Periods:
        """Horizon of the lag"""
        return self.of.horizon

    def __eq__(self, other: Self | Periods) -> bool:
        """Check if two lags are equal"""
        if isinstance(other, Lag):
            return is_(self.of, other.of) and self.periods == other.periods
        return is_(self.of, other)
