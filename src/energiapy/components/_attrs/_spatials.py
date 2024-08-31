"""Balance input attributes for Components
"""

from dataclasses import dataclass, field

from ..scope.spatial.linkage import Linkage
from ..scope.spatial.location import Location


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
