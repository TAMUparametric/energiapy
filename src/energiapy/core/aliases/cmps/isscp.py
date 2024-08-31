"""Aliases for Spatio Temporal (Scope) Components
"""

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
type IsScp = Horizon | Network
type IsTmp = Horizon | Scale | X | I
type IsSpt = Network | Linkage | Location
type IsSptTmp = IsSpt | IsTmp
