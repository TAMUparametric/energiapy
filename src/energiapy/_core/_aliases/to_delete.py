"""Aliases are used to streamline the type hinting across energiapy
alias should only be called if TYPE_CHECKING is True, to avoid circular imports

There are a lot of redundancies in the definition of type hints
This is intentionally, for the sake of clarity and consistency in using the Is format for type hinting
"""

# from typing import Dict, List, Literal, Tuple, Union

# from pandas import DataFrame

# from ..components.commodity.cash import Cash
# from ..components.commodity.emission import Emission
# from ..components.commodity.land import Land
# from ..components.commodity.material import Material
# from ..components.commodity.resource import Resource
# from ..components.operation.process import Process
# from ..components.operation.storage import Storage
# from ..components.operation.transit import Transit
# from ..components.spatial.linkage import Linkage
# from ..components.spatial.location import Location
# from ..components.spatial.network import Network
# from ..components.temporal.horizon import Horizon
# from ..components.temporal.scale import Scale
# from ..elements.constraint import Constraint
# from ..elements.index import Index
# from ..elements.parameter import Parameter
# from ..elements.variable import Variable
# from ..inputs.values.bounds import SpcLmt, VarBnd
# from ..inputs.values.dataset import DataSet
# from ..inputs.values.m import BigM, M
# from ..inputs.values.constant import Number
# from ..inputs.values.theta import Th, Theta

# from .input.aspect import CashFlow, Emission, Land, Life, Limit, Loss
# #TODO - Change Land enum


# # *input types
# IsNumeric = Union[float, int]
# # is unbounded (=< BigM), constraint not written by variable declared
# # a futher check of whether value is True is required
# # so if value are given as False, then they are set to None
# IsFree = Union[Literal[True], Literal[BigM]]
# # deterministic data is provided
# IsData = DataFrame
# # a range is give, treated as bounds for a parameteric variable
# IsSpaceBound = Union[IsNumeric, IsData]
# IsSpace = Union[Tuple[IsSpaceBound, IsSpaceBound], Literal[Th]]
# # as an exact value (equality constraint)
# IsExact = Union[IsNumeric, IsData, IsSpace]


# *Temporal types
# IsHorizon = Horizon
# IsScale = Scale

# *Network type
# IsNetwork = Network

# *Operation types
# IsProcess = Process
# IsStorage = Storage
# IsTransit = Transit

# *Spatial types
# IsLinkage = Linkage
# IsLocation = Location

# *Component types
# IsCommodity = Union[IsCash, IsEmission, IsLand, IsMaterial, IsResource]
# IsOperation = Union[IsProcess, IsStorage, IsTransit]
# IsSpatial = Union[IsLinkage, IsLocation]
# IsComponent = Union[IsCommodity, IsOperation, IsSpatial]

# * compound input types
# as a list of bounds [lower, upper] (inequality constraints)

# IsBound = List[IsExact, IsFree]

# IsTmpDict = Dict[IsScale, Union[IsExact, IsBound, IsFree]]

# IsSptDict = Dict[IsSpatial, Union[IsExact, IsBound, IsFree]]

# IsSptTmpDict = Dict[IsSpatial, IsTmpDict]

# as a dictionary with keys being the temporal scale
# IsLimit = Union[IsBound, IsExact, IsTmpDict, IsSptDict, IsSptTmpDict, IsFree]
# IsCap = Union[IsBound, IsExact, IsSptDict, IsTmpDict]
# IsInput = Union[IsExact, IsBound, IsFree, IsSptDict, IsSptTmpDict, IsTmpDict]


# # * Value types
# # these are generated internally
# IsNumber = Number
# # if a range is provided
# IsParVar = Theta
# # if deterministic data is provided
# IsDataSet = DataSet
# # if unbounded
# IsM = M
# # this is the value attribute of Value dataclass
# IsValue = Union[IsNumber, IsParVar, IsDataSet, IsM]


# # *Bound types
# # is parameter bound on variable
# IsVarBnd = VarBnd
# # is a limit to the domain of a parametric variable
# IsSpcLmt = SpcLmt


# *Specific Aspect types
# IsCapacity = IsLimit
# IsResFlow = IsLimit
# IsCashFlow, IsEmission, IsLandUse, IsLife, IsLoss = (IsExact for _ in range(5))
# IsResFlowCap = IsCap
# IsEmissionCap, IsCap = (IsBound for _ in range(2))

# * Commodity types
# IsCash = Cash
# IsEmission = Emission
# IsLand = Land
# IsMaterial = Material
# IsResource = Resource

# *Classes and Enums
# IsTask = Union[IsResFlowCap, IsCashFlow, IsEmission, IsEmissionCap,
#                IsLand, IsLandCap, IsLandUse, IsLife, IsLimit, IsLoss]
# IsAspectShared = Dict[IsComponent, IsAspect]
# IsSpatialPair = Union[Tuple[IsOperation, IsSpatial],
#                       Tuple[IsSpatial, IsSpatial]]
# IsDeclaredAt = Union[IsSpatialPair, IsComponent]

# # *Conversion
# # can be multimode or single mode
# IsSingleConv = Dict[Resource, IsNumeric]
# IsMultiConv = Dict[Union[IsNumeric, str], IsSingleConv]
# IsConvBalance = Union[IsSingleConv, IsMultiConv]
# IsConv = Dict[Resource, IsConvBalance]

# # *MaterialUse
# # can be multimode or single mode
# IsSingleMat = Dict[Material, IsNumeric]
# IsMultiMat = Dict[Union[IsNumeric, str], IsSingleMat]
# IsMatUse = Union[IsSingleMat, IsMultiMat]

# # *General Balance
# IsBalance = Union[IsConv, IsMatUse]


# # *Piecewise Linear
# IsPWL = Dict[Tuple[IsNumeric, IsNumeric], IsNumeric]

# # *Details
# IsDetail = str

# # *Depreciated
# IsDepreciated = str

# IsInput = Union[IsAspect, IsBalance, IsPWL, IsDetail]


# # * Elements

# IsParameter = Parameter
# IsConstraint = Constraint
# IsVariable = Variable
# IsIndex = Index


# # *Player

# IsOwns = Dict[IsSpatial, List[IsOperation]]
# IsCan = Dict[IsSpatial,
#              List[Dict[IsCommodity, IsValue]]]
