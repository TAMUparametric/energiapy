"""Base for any Commodity Component
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .._base._defined import _Defined

if TYPE_CHECKING:
    from ..spatial.linkage import Linkage
    from ..spatial.location import Location


@dataclass
class _Commodity(_Defined):
    """Commodities"""

    def __post_init__(self):
        _Defined.__post_init__(self)
        # where a commodity spatial exists
        # these are defined depending on how operations are located
        self.locations: list[Location] = []
        self.linkages: list[Linkage] = []

    @property
    def spatials(self):
        """Spatial Components"""
        return self.locations + self.linkages
