"""Aliases are used to streamline the type hinting across energiapy
"""
from typing import Dict, List, Tuple, Union

from pandas import DataFrame

from ..components.linkage import Linkage
from ..components.location import Location
from ..components.material import Material
from ..components.process import Process
from ..components.resource import Resource
from ..components.storage import Storage
from ..components.temporal_scale import TemporalScale
from ..components.transport import Transport
from ..elements.specialparams.dataset import DataSet
from ..elements.specialparams.theta import Theta
from ..elements.specialparams.unbound import Unbound
from .element.aspect import CashFlow, Emission, Land, Life, Limit, Loss

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
IsTempDict = Dict[TemporalScale, Union[IsExact, IsBound]]

IsValue = Union[IsExact, IsBound, IsTempDict]

# *Specific Aspect types
IsTemporal = TemporalScale
IsLimit = Union[IsExact, IsUnbound, IsBound, IsTempDict]
IsCapBound = Union[IsExact, IsBound]
IsCashFlow, IsLand, IsEmission, IsLife, IsLoss = (IsExact for _ in range(5))

# *Classes and Enums
IsAspect = Union[CashFlow, Emission, Land, Life, Limit, Loss]
IsComponent = Union[Resource, Process, Material,
                    Storage, Location, Transport, Linkage]
IsAspectDict = Dict[IsComponent, IsAspect]
IsSpatialPair = Union[Tuple[Process, Location], Tuple[Transport, Linkage]]
IsDeclaredAt = Union[IsSpatialPair, IsComponent]

# *Conversion
# can be multimode or single mode
IsSingleConv = Dict[Resource, IsNumeric]
IsMultiConv = Dict[Union[IsNumeric, str], IsSingleConv]
IsBalance = Union[IsSingleConv, IsMultiConv]
IsConv = Dict[Resource, IsBalance]

# *Material
# can be multimode or single mode
IsSingleMat = Dict[Material, IsNumeric]
IsMultiMat = Dict[Union[IsNumeric, str], IsSingleMat]
IsMatCons = Union[IsSingleMat, IsMultiMat]

# *Piecewise Linear
IsPWL = Dict[Tuple[IsNumeric, IsNumeric], IsNumeric]

# *Details
IsDetail = str

# *Depreciated
IsDepreciated = str
