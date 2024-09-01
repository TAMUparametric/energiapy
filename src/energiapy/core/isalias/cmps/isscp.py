"""Aliases for Spatio Temporal (Scope) Components
"""

from typing import TypeAlias

from ....components.spatial.linkage import Linkage
from ....components.spatial.location import Location
from ....components.spatial.network import Network
from ....components.temporal.horizon import Horizon
from ....components.temporal.incidental import I
from ....components.temporal.mode import X
from ....components.temporal.scale import Scale

# SpatioTemporal
# These halp set the scope of the problem
# Scales provide the discretization of the Temporal Horizon
# Linkages provide the spatial connections between Locations
IsScp: TypeAlias = Horizon | Network
IsTmp: TypeAlias = Horizon | Scale | X | I
IsSpt: TypeAlias = Network | Linkage | Location
IsSptTmp: TypeAlias = IsSpt | IsTmp
