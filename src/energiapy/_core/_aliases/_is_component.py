from typing import TypeAlias, Union

from ...components.analytical.player import Player
from ...components.commodity.cash import Cash
from ...components.commodity.land import Land
from ...components.commodity.material import Material
from ...components.commodity.resource import Resource
from ...components.impact.emission import Emission
from ...components.operational.process import Process
from ...components.operational.storage import Storage
from ...components.operational.transit import Transit
from ...components.scope.horizon import Horizon
from ...components.scope.network import Network
from ...components.spatial.linkage import Linkage
from ...components.spatial.location import Location
from ...components.temporal.scale import Scale

# Scope
IsHorizon: TypeAlias = Horizon
IsNetwork: TypeAlias = Network
IsScope: TypeAlias = Union[IsHorizon, IsNetwork]

# Temporal
IsScale: TypeAlias = Scale
IsTemporal: TypeAlias = Union[IsScale]

# Spatial
IsLinkage: TypeAlias = Linkage
IsLocation: TypeAlias = Location
IsSpatial: TypeAlias = Union[IsLinkage, IsLocation]

# SpatioTemporal
IsSpatioTemporal: TypeAlias = Union[IsScope, IsSpatial, IsTemporal]

# Analytical
IsPlayer: TypeAlias = Player
IsAnalytical: TypeAlias = Union[IsPlayer]


# Assets
IsCash: TypeAlias = Cash
IsLand = Land
IsAsset: TypeAlias = Union[IsCash, IsLand]

# Impact
IsEmission: TypeAlias = Emission
IsImpact: TypeAlias = Union[IsEmission]

# Commodity

IsMaterial: TypeAlias = Material
IsResource: TypeAlias = Resource
IsCommodity: TypeAlias = Union[IsMaterial, IsResource]

# Operation
IsProcess: TypeAlias = Process
IsStorage: TypeAlias = Storage
IsTransit: TypeAlias = Transit
IsOperational: TypeAlias = Union[IsProcess, IsStorage, IsTransit]

# Component
IsComponent: TypeAlias = Union[
    IsAnalytical,
    IsAsset,
    IsCommodity,
    IsImpact,
    IsOperational,
    IsScope,
    IsSpatial,
    IsTemporal,
]
