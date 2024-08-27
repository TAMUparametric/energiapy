"""Balance input attributes for Components
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..core.aliases.is_component import IsLinkage, IsLocation


@dataclass
class LocCollection:
    """Collection of Locations"""

    locations: List[IsLocation] = field(default_factory=list)


@dataclass
class LnkCollection:
    """Collection of Linkages"""

    linkages: List[IsLinkage] = field(default_factory=list)
