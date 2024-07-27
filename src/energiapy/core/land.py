from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..type.alias import IsCashFlow, IsLandCap, IsLandUse


@dataclass
class OpnLand:
    """Land use of Operation Component
    """
    land_use: IsLandUse = field(default=None)


@dataclass
class SptLand(OpnLand):
    """Land use cap (upper bound) for Spatial Component 
    """
    land_cap: IsLandCap = field(default=None)
    land_cost: IsCashFlow = field(default=None)
