from __future__ import annotations

from dataclasses import dataclass, field

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..type.alias import IsLandUse, IsLandCap, IsCashFlow


@dataclass
class OpnLand:
    """Land use of Operation 
    """
    land_use: IsLandUse = field(default=None)


@dataclass
class SpcLand:
    """Land use cap (upper bound) for Space
    """
    land_cap: IsLandCap = field(default=None)
    land_cost: IsCashFlow = field(default=None)
