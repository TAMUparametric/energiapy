from typing import TypeAlias, Union

from ...components.analytical.player import Player
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
from ...components.scope.network import Network
from ...components.scope.horizon import Horizon
from ...components.temporal.scale import Scale
from ...model.scenario import Scenario

# *Analytical
IsScenario: TypeAlias = Scenario
IsPlayer: TypeAlias = Player
IsAnalytical: TypeAlias = Union[IsScenario, IsPlayer]

# *Temporal
IsHorizon: TypeAlias = Horizon
IsScale: TypeAlias = Scale
IsTemporal: TypeAlias = Union[IsHorizon, IsScale]

# *Spatial
IsLinkage: TypeAlias = Linkage
IsLocation: TypeAlias = Location
IsNetwork: TypeAlias = Network
IsSpatial: TypeAlias = Union[IsLinkage, IsLocation, IsNetwork]

# * Commodity
# Assets
IsCash: TypeAlias = Cash
IsLand = Land
IsAsset: TypeAlias = Union[IsCash, IsLand]
# Impact
IsEmission: TypeAlias = Emission
IsImpact: TypeAlias = Union[IsEmission]
# Traded
IsMaterial: TypeAlias = Material
IsResource: TypeAlias = Resource
IsTraded: TypeAlias = Union[IsMaterial, IsResource]
# All
IsCommodity: TypeAlias = Union[IsAsset, IsImpact, IsTraded]


# *Operation
IsProcess: TypeAlias = Process
IsStorage: TypeAlias = Storage
IsTransit: TypeAlias = Transit
IsOperational: TypeAlias = Union[IsProcess, IsStorage, IsTransit]


IsScopeComponent: TypeAlias = Union[IsHorizon, IsNetwork]

# *Component
IsComponent: TypeAlias = Union[
    IsAnalytical, IsTemporal, IsSpatial, IsCommodity, IsOperational
]
