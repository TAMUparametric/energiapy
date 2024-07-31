"""Aliases are used to streamline the type hinting across energiapy
alias should only be called if TYPE_CHECKING is True, to avoid circular imports

There are a lot of redundancies in the definition of type hints
This is intentionally, for the sake of clarity and consistency in using the Is format for type hinting
"""
from typing import Dict, List, Tuple, Union, Literal

from pandas import DataFrame

from ..components.commodity.derived import Cash, Emission, Land
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.operation.process import Process
from ..components.operation.storage import Storage
from ..components.operation.transit import Transit
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.spatial.network import Network
from ..components.temporal.horizon import Horizon
from ..components.temporal.scale import Scale
from ..values.dataset import DataSet
from ..values.m import BigM, M
from ..values.theta import Theta, Th
from ..values.number import Number
from ..values.bound import VarBnd, SpcLmt

from ..elements.parameter import Parameter
from ..elements.constraint import Constraint
from ..elements.variable import Variable
from ..elements.index import Index

# from .input.aspect import CashFlow, Emission, Land, Life, Limit, Loss #TODO - Change Land enum


# *input types
IsNumeric = Union[float, int]
# is unbounded (=< BigM), constraint not written by variable declared
# a futher check of whether value is True is required
# so if value are given as False, then they are set to None
IsFree = Union[Literal[True], Literal[BigM]]
# deterministic data is provided
IsData = DataFrame
# a range is give, treated as bounds for a parameteric variable
IsSpaceBound = Union[IsNumeric, IsData]
IsSpace = Union[Tuple[IsSpaceBound, IsSpaceBound], Literal[Th]]
# as an exact value (equality constraint)
IsExact = Union[IsNumeric, IsData, IsSpace]

# * compound input types
# as a list of bounds [lower, upper] (inequality constraints)
IsBound = List[IsExact, IsFree]
# as a dictionary with keys being the temporal scale
IsTempDict = Dict[Scale, Union[IsExact, IsBound, IsFree]]
IsLimit = Union[IsBound, IsExact, IsTempDict, IsFree]
IsCap = Union[IsBound, IsExact, IsTempDict]
IsInput = Union[IsExact, IsBound, IsFree, IsTempDict]


# * Value types
# these are generated internally
IsNumber = Number
# if a range is provided
IsParVar = Theta
# if deterministic data is provided
IsDataSet = DataSet
# if unbounded
IsM = M
# this is the value attribute of Value dataclass
IsValue = Union[IsNumber, IsParVar, IsDataSet, IsM]


# *Bound types
# is parameter bound on variable
IsVarBnd = VarBnd
# is a limit to the domain of a parametric variable
IsSpcLmt = SpcLmt

# *Temporal types
IsHorizon = Horizon
IsTemporal = Scale

# *Network type
IsNetwork = Network

# *Specific Aspect types
IsCapacity = IsLimit
IsResFlow = IsLimit
IsCashFlow, IsEmission, IsLandUse, IsLife, IsLoss = (IsExact for _ in range(5))
IsResFlowCap = IsCap
IsEmissionCap, IsCap = (IsBound for _ in range(2))

# *Derived Commodity types
IsCash = Cash
IsEmission = Emission
IsLand = Land

# *Commodity types
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
IsDerived = Union[IsCash, IsEmission, IsLand]
IsCommodity = Union[IsMaterial, IsResource]
IsOperation = Union[IsProcess, IsStorage, IsTransit]
IsSpatial = Union[IsLinkage, IsLocation]
IsComponent = Union[IsCommodity, IsOperation, IsSpatial]

# *Classes and Enums
IsAspect = Union[IsResFlowCap, IsCashFlow, IsEmission, IsEmissionCap,
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


# * Elements

IsParameter = Parameter
IsConstraint = Constraint
IsVariable = Variable
IsIndex = Index
