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


# Impact Commodity
IsEmission: TypeAlias = Emission
IsImpact: TypeAlias = Union[IsEmission]


# Asset Commodity
IsCash: TypeAlias = Cash
IsLand = Land

# Traded Commodity
IsMaterial: TypeAlias = Material
IsResource: TypeAlias = Resource

IsTraded: TypeAlias = Union[IsMaterial, IsResource]
IsUsed: TypeAlias = Union[IsMaterial, IsLand]
IsAsset: TypeAlias = Union[IsCash, IsLand]

# Commodity
IsCommodity: TypeAlias = Union[IsMaterial, IsResource, IsEmission, IsCash, IsLand]


# Operational
IsProcess: TypeAlias = Process
IsStorage: TypeAlias = Storage
IsTransit: TypeAlias = Transit
IsOperational: TypeAlias = Union[IsProcess, IsStorage, IsTransit]

# Components with only one instance
IsLonely: TypeAlias = Union[IsScope, IsAsset]

# Components with multiple instances and generate constraints
IsDefined: TypeAlias = Union[IsAnalytical, IsCommodity, IsOperational]

# Components with whcich do not generate constraints and add scale to the Scope
IsScopeScale: TypeAlias = Union[IsSpatial, IsTemporal]

# Component
IsComponent: TypeAlias = Union[
    IsAnalytical,
    IsCommodity,
    IsImpact,
    IsOperational,
    IsScope,
    IsSpatial,
    IsTemporal,
]
