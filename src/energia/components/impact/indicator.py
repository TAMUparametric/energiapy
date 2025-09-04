"""Impact Indicator"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...core.component import Component

if TYPE_CHECKING:
    from ...dimensions.consequence import Consequence


@dataclass
class Indicator(Component):
    """Impact Indicator"""

    def __post_init__(self):
        Component.__post_init__(self)

    @property
    def impact(self) -> Consequence:
        """Impact object"""
        return self.model.impact
