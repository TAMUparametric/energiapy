"""Aliases are used to streamline the type hinting across energiapy
"""
from typing import Dict, List, Tuple, Union

from pandas import DataFrame

from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.operation.process import Process
from ..components.operation.storage import Storage
from ..components.operation.transport import Transport
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.spatial.network import Network
from ..components.temporal.scale import Scale
from ..elements.specialparams.dataset import DataSet
from ..elements.specialparams.theta import Theta
from ..elements.specialparams.unbound import Unbound
from .input.aspect import CashFlow, Emission, Land, Life, Limit, Loss

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

# *Specific Aspect types
IsTemporal = Scale
IsLimit = Union[IsExact, IsUnbound, IsBound, IsTempDict]
IsCapBound = Union[IsExact, IsBound]

IsCashFlow, IsLandUse, IsEmission, IsLife, IsLoss = (IsExact for _ in range(5))
IsLandCap, IsEmissionCap = (IsBound for _ in range(2))

# *Component types
IsCommodity = Union[Resource, Material]
IsOperation = Union[Process, Storage, Transport]
IsSpace = Union[Location, Linkage, Network]
IsComponent = Union[IsCommodity, IsOperation, IsSpace]

# *Classes and Enums
IsAspect = Union[CashFlow, Emission, Land, Life, Limit, Loss]
IsAspectShared = Dict[IsComponent, IsAspect]
IsSpatialPair = Union[Tuple[IsOperation, IsSpace], Tuple[IsSpace, IsSpace]]
IsDeclaredAt = Union[IsSpatialPair, IsComponent]

# *Conversion
# can be multimode or single mode
IsSingleConv = Dict[Resource, IsNumeric]
IsMultiConv = Dict[Union[IsNumeric, str], IsSingleConv]
IsBalance = Union[IsSingleConv, IsMultiConv]
IsConv = Dict[Resource, IsBalance]

# *MaterialUse
# can be multimode or single mode
IsSingleMat = Dict[Material, IsNumeric]
IsMultiMat = Dict[Union[IsNumeric, str], IsSingleMat]
IsMatUse = Union[IsSingleMat, IsMultiMat]

# *Piecewise Linear
IsPWL = Dict[Tuple[IsNumeric, IsNumeric], IsNumeric]

# *Details
IsDetail = str

# *Depreciated
IsDepreciated = str
