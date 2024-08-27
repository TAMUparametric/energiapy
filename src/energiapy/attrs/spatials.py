"""Balance input attributes for Components
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..core.aliases.is_component import IsLinkage, IsLocation


class Spatials:
    """Spatial Components where Component can be located"""

    @classmethod
    def _spatials(cls):
        """Spatials"""
        return fields(cls)


@dataclass
class LocCollection(Spatials):
    """Collection of Locations"""

    locations: List[IsLocation] = field(default_factory=list)


@dataclass
class LnkCollection(Spatials):
    """Collection of Linkages"""

    linkages: List[IsLinkage] = field(default_factory=list)
