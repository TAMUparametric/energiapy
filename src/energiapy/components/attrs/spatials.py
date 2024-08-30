"""Balance input attributes for Components
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...components.spatial.location import Location
    from ...components.spatial.linkage import Linkage


@dataclass
class LocCollection:
    """Collection of Locations"""

    locations: list[Location] = field(default_factory=list)

    @staticmethod
    def _spatials():
        """Spatials"""
        return 'locations'


@dataclass
class LnkCollection:
    """Collection of Linkages"""

    linkages: list[Linkage] = field(default_factory=list)

    @staticmethod
    def _spatials():
        """Spatials"""
        return 'linkages'
