"""Aliases for Spatio Temporal (Scope) Components
"""

from typing import TypeAlias

from ....components.spatial.linkage import Linkage
from ....components.spatial.location import Location
from ....environ.network import Network
from ....environ.horizon import Horizon
from ....components.abstract.mode import X
from ....components.temporal.period import Scale

# SpatioTemporal
# These halp set the scope of the problem
# Scales provide the discretization of the Temporal Horizon
# Linkages provide the spatial connections between Locations
IsScp: TypeAlias = Horizon | Network
IsTmp: TypeAlias = Horizon | Scale
IsSpt: TypeAlias = Network | Linkage | Location
IsAbs: TypeAlias = X
IsSptTmp: TypeAlias = IsSpt | IsTmp
