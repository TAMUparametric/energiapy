from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..type.alias import IsLimit


@dataclass
class RscLimit:
    """Resource Limits
    """
    discharge: IsLimit = field(default=None)
    consume: IsLimit = field(default=None)


@dataclass
class PrcLimit(RscLimit):
    """Operation Limits
    """
    capacity: IsLimit = field(default=None)
