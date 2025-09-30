"""Bound Parameter Input"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..._core._name import _Name

if TYPE_CHECKING:
    from ...components.temporal.periods import Periods


@dataclass
class Value(_Name):
    """Input Value"""

    value: (
        float
        | int
        | list[float]
        | list[int]
        | tuple[float]
        | tuple[int]
        | tuple[list[int | float]]
    ) = None
    period: Periods = None

    def __post_init__(self):
        if isinstance(self.value, (float, int)):
            self.name = f'{self.value}/{self.period}'
        else:
            self.name = f'Φ/{self.period}'
