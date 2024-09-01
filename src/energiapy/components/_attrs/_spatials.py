"""Balance input attributes for Components
"""

from dataclasses import dataclass, field

from ..spatial.linkage import Linkage
from ..spatial.location import Location


@dataclass
class _LocCollection:
    """Collection of Locations"""

    locations: list[Location] = field(default_factory=list)

    @staticmethod
    def _spatials():
        """Spatials"""
        return 'locations'


@dataclass
class _LnkCollection:
    """Collection of Linkages"""

    linkages: list[Linkage] = field(default_factory=list)

    @staticmethod
    def _spatials():
        """Spatials"""
        return 'linkages'
