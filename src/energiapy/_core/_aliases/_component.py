
from typing import Union

from ...components.analytical.player import Player
from ...components.analytical.scenario import Scenario
from ...components.commodity.cash import Cash
from ...components.commodity.emission import Emission
from ...components.commodity.land import Land
from ...components.commodity.material import Material
from ...components.commodity.resource import Resource
from ...components.operational.process import Process
from ...components.operational.storage import Storage
from ...components.operational.transit import Transit
from ...components.spatial.linkage import Linkage
from ...components.spatial.location import Location
from ...components.spatial.network import Network
from ...components.temporal.horizon import Horizon
from ...components.temporal.scale import Scale

# *Analytical
IsScenario = Scenario
IsPlayer = Player
IsAnalytical = Union[IsScenario, IsPlayer]

# *Temporal
IsHorizon = Horizon
IsScale = Scale
IsTemporal = Union[IsHorizon, IsScale]

# *Spatial
IsLinkage = Linkage
IsLocation = Location
IsNetwork = Network
IsSpatial = Union[IsLinkage, IsLocation, IsNetwork]

# * Commodity
# Assets
IsCash = Cash
IsLand = Land
IsAsset = Union[IsCash, IsLand]
# Impact
IsEmission = Emission
IsImpact = Union[IsEmission]
# Traded
IsMaterial = Material
IsResource = Resource
IsTraded = Union[IsMaterial, IsResource]
# All
IsCommodity = Union[IsAsset, IsImpact, IsTraded]


# *Operation
IsProcess = Process
IsStorage = Storage
IsTransit = Transit
IsOperational = Union[IsProcess, IsStorage, IsTransit]


IsScopeComponent = Union[IsHorizon, IsNetwork]

# *Component
IsComponent = Union[IsAnalytical, IsTemporal,
                    IsSpatial, IsCommodity, IsOperational]
