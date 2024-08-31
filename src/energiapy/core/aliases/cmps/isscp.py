"""Aliases for Spatio Temporal (Scope) Components
"""

from typing import TypeAlias

from ....components.scope.spatial.linkage import Linkage
from ....components.scope.spatial.location import Location
from ....components.scope.spatial.network import Network
from ....components.scope.temporal.horizon import Horizon
from ....components.scope.temporal.incidental import I
from ....components.scope.temporal.mode import X
from ....components.scope.temporal.scale import Scale

# SpatioTemporal
# These halp set the scope of the problem
# Scales provide the discretization of the Temporal Horizon
# Linkages provide the spatial connections between Locations
IsScp: TypeAlias = Horizon | Network
IsTmp: TypeAlias = Horizon | Scale | X | I
IsSpt: TypeAlias = Network | Linkage | Location
IsSptTmp: TypeAlias = IsSpt | IsTmp
