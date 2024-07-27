"""Aliases are used to streamline the type hinting across energiapy
alias should only be called if TYPE_CHECKING is True, to avoid circular imports
"""
from typing import Dict, List, Tuple, Union

from pandas import DataFrame

from ..components.commodity.cash import Cash
from ..components.commodity.emission import Emission
from ..components.commodity.land import Land
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.operation.process import Process
from ..components.operation.storage import Storage
from ..components.operation.transport import Transit
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.spatial.network import Network
from ..components.temporal.horizon import Horizon
from ..components.temporal.scale import Scale
from ..elements.specialparams.dataset import DataSet
from ..elements.specialparams.theta import Theta
from ..elements.specialparams.unbound import Unbound

# from .input.aspect import CashFlow, Emission, Land, Life, Limit, Loss #TODO - Change Land enum


# *Base types
# aspect is given as a numeric value
IsNumeric = Union[float, int]
# aspect is unbounded
IsUnbound = Union[bool, Unbound]
# aspect is defined using a data
IsData = Union[DataFrame, DataSet]
# aspect is defined as a parametric variable
IsParVar = Union[Tuple[Union[IsNumeric, IsData],
                       Union[IsNumeric, IsData]], Theta]

# *Compound types
# as an exact value (equality constraint)
IsExact = Union[IsNumeric, IsData, IsParVar]
# as a list of bounds [lower, upper] (inequality constraints)
IsBound = List[IsExact]
# as a dictionary of exact values or bounds, with keys being the temporal scale
IsTempDict = Dict[Scale, Union[IsExact, IsBound]]

IsValue = Union[IsExact, IsBound, IsTempDict]

# *Temporal types
IsHorizon = Horizon
IsTemporal = Scale

# *Network type
IsNetwork = Network

# *Specific Aspect types
IsLimit = Union[IsBound, IsExact, IsTempDict, IsUnbound]
IsCapBound = Union[IsExact, IsBound]
IsCashFlow, IsEmission, IsLandUse, IsLife, IsLoss = (IsExact for _ in range(5))
IsEmissionCap, IsLandCap = (IsBound for _ in range(2))

# *Commodity types
IsCash = Cash
IsEmission = Emission
IsLand = Land
IsMaterial = Material
IsResource = Resource


# *Operation types
IsProcess = Process
IsStorage = Storage
IsTransit = Transit

# *Spatial types
IsLinkage = Linkage
IsLocation = Location


# *Component types
IsCommodity = Union[IsMaterial, IsResource]
IsOperation = Union[IsProcess, IsStorage, IsTransit]
IsSpatial = Union[IsLinkage, IsLocation]
IsComponent = Union[IsCommodity, IsOperation, IsSpatial]

# *Classes and Enums
IsAspect = Union[IsCapBound, IsCashFlow, IsEmission, IsEmissionCap,
                 IsLand, IsLandCap, IsLandUse, IsLife, IsLimit, IsLoss]
IsAspectShared = Dict[IsComponent, IsAspect]
IsSpatialPair = Union[Tuple[IsOperation, IsSpatial],
                      Tuple[IsSpatial, IsSpatial]]
IsDeclaredAt = Union[IsSpatialPair, IsComponent]

# *Conversion
# can be multimode or single mode
IsSingleConv = Dict[Resource, IsNumeric]
IsMultiConv = Dict[Union[IsNumeric, str], IsSingleConv]
IsConvBalance = Union[IsSingleConv, IsMultiConv]
IsConv = Dict[Resource, IsConvBalance]

# *MaterialUse
# can be multimode or single mode
IsSingleMat = Dict[Material, IsNumeric]
IsMultiMat = Dict[Union[IsNumeric, str], IsSingleMat]
IsMatUse = Union[IsSingleMat, IsMultiMat]

# *General Balance
IsBalance = Union[IsConv, IsMatUse]


# *Piecewise Linear
IsPWL = Dict[Tuple[IsNumeric, IsNumeric], IsNumeric]

# *Details
IsDetail = str

# *Depreciated
IsDepreciated = str

IsInput = Union[IsAspect, IsBalance, IsPWL, IsDetail]
