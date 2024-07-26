from __future__ import annotations

from dataclasses import dataclass, field

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..type.alias import IsEmission, IsEmissionCap


@dataclass
class Impact:
    """Enivronmental impact of Commodities and Operations
    """
    gwp: IsEmission = field(default=None)
    odp: IsEmission = field(default=None)
    acid: IsEmission = field(default=None)
    eutt: IsEmission = field(default=None)
    eutf: IsEmission = field(default=None)
    eutm: IsEmission = field(default=None)


@dataclass
class ImpactCap:
    """Environmental impact caps (upper bounds) for Spaces 
    """
    gwp: IsEmissionCap = field(default=None)
    odp: IsEmissionCap = field(default=None)
    acid: IsEmissionCap = field(default=None)
    eutt: IsEmissionCap = field(default=None)
    eutf: IsEmissionCap = field(default=None)
    eutm: IsEmissionCap = field(default=None)
