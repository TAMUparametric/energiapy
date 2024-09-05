"""Time Periods that constitute a scale 
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass, field
from ...core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from .scale import Scale


@dataclass
class Period(_Dunders):
    """Time Period in a Scale"""

    scale: Scale = field(default=None)
    period: tuple = field(default=None)

    def __post_init__(self):
        self.name = f'{self.scale.name}{self.period}'
