"""Temporal Lag"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from operator import is_
from typing import TYPE_CHECKING, Self

from ..._core._name import _Name

if TYPE_CHECKING:
    from gana import I as Idx

    from ...modeling.indices.domain import Domain
    from .periods import Periods


@dataclass
class Lag(_Name):
    """
    A number of temporal Periods.

    :ivar label: Label of the component, used for plotting. Defaults to None.
    :vartype label: str
    :ivar of: Periods to lag. Defaults to None.
    :vartype of: Periods
    :ivar periods: Number of periods to lag. Defaults to 1.
    :vartype periods: int | float
    :ivar name: Name of the component, generated based on the number of periods.
    :vartype name: str
    :ivar domains: List of Domains the lag features belong to. Defaults to [].
    :vartype domains: list[Domain]

    .. note::
        - Name is generated post init.
        - Domains are set as the program is built.
    """

    of: Periods = None
    periods: int | float = 1

    def __post_init__(self):
        self.name = f"-{self.periods}{self.of}"
        self.domains: list[Domain] = []
        self.constraints: list[str] = []

    @cached_property
    def I(self) -> Idx:
        """Index set of periods - periods
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
