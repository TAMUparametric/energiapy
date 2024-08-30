"""Aliases for Components
"""

from ...components.analytical.player import Player
from ...components.commodity.cash import Cash
from ...components.commodity.emission import Emission
from ...components.commodity.land import Land
from ...components.commodity.material import Material
from ...components.commodity.resource import Resource
from ...components.operational.process import Process
from ...components.operational.storage import Storage
from ...components.operational.transit import Transit
from ...components.scope.horizon import Horizon
from ...components.scope.network import Network
from ...components.spatial.linkage import Linkage
from ...components.spatial.location import Location
from ...components.temporal.scale import Scale
from ...components.temporal.mode import X


# Analytical
type IsAnalytical = Player

# SpatioTemporal
# These halp set the scope of the problem
# Scales provide the discretization of the Temporal Horizon
# Linkages provide the spatial connections between Locations
type IsScope = Horizon | Network
type IsTemporal = Horizon | Scale | X
type IsSpatial = Network| Linkage | Location
type IsSptTmp = IsSpatial | IsTemporal

# Commodities
type IsImpact = Emission
type IsTraded= Material | Resource
type IsUsed = Material | Land
type IsAsset = Cash | Land
type IsCommodity = Emission| Material| Resource | Cash | Land

# Operational
type IsOperational = Process| Storage| Transit

# Have only one instance
type IsLonely = IsScope | IsAsset

# These have multiple instances
# constraints are generated based on the data provided to these components
type IsDefined = IsAnalytical| IsCommodity| IsOperational

type IsCmp =  IsAnalytical| IsCommodity| IsImpact| IsOperational| IsScope| IsSpatial| IsTemporal|

type IsIndex = tuple[IsCmp]

