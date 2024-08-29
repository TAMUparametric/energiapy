"""Bound input attributes for Components
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.aliases.is_input import IsBoundInput


@dataclass
class StgBirthing:
    """Bounds for Processes birthed in Storage"""

    capacity_in: IsBoundInput = field(default=None)
    capacity_out: IsBoundInput = field(default=None)
