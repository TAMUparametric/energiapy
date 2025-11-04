"""Bound Parameter Input"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..._core._name import _Name

if TYPE_CHECKING:
    from ...components.temporal.periods import Periods


class Value(_Name):
    """Input Value"""

    def __init__(
        self,
        value: (
            float
            | int
            | list[float]
            | list[int]
            | tuple[float]
            | tuple[int]
            | tuple[list[int | float]]
            | None
        ) = None,
        periods: Periods | None = None,
    ):
        self.value = value
        self.periods = periods
        _Name.__init__(self, label="")
        if isinstance(self.value, (float, int)):
            self.name = f"{self.value}/{self.periods}"
        else:
            self.name = f"Φ/{self.periods}"
