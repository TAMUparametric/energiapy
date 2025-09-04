"""Bound Parameter Input"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...core.name import Name

if TYPE_CHECKING:
    from ...components.temporal.period import Period


@dataclass
class Value(Name):
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
    period: Period = None

    def __post_init__(self):
        if isinstance(self.value, (float, int)):
            self.name = f'{self.value}/{self.period}'
        else:
            self.name = f'Φ/{self.period}'
