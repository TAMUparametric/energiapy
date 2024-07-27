from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..type.alias import IsLimit


@dataclass
class ResLimit:
    """Resource Limits
    """
    discharge: IsLimit = field(default=None)
    consume: IsLimit = field(default=None)


@dataclass
class OpnLimit:
    """Operation Limits
    """
    capacity: IsLimit
