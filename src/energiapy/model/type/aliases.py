"""Aliases are used to streamline the type hinting across energiapy
"""
from typing import Dict, List, Tuple, Union

from pandas import DataFrame

from ...components.linkage import Linkage
from ...components.location import Location
from ...components.process import Process
from ...components.resource import Resource
from ...components.temporal_scale import TemporalScale
from ...components.transport import Transport
from ..specialparams.dataset import DataSet
from ..specialparams.theta import Theta
from ..specialparams.unbound import BigM, smallm
from .aspect import CashFlow, Emission, Land, Life, Limit, Loss

# *Base types
# aspect is given as a numeric value
IsNumeric = Union[float, int]
# aspect is unbounded
IsUnbound = Union[bool, BigM, smallm]
# aspect is defined using a data
IsData = Union[DataFrame, DataSet]
# aspect is defined as a parametric variable
IsParVar = Union[Tuple[Union[IsNumeric, IsData],
                       Union[IsNumeric, IsData]], Theta]

# *Compound types
# as an exact value (equality constraint)
IsExact = Union[IsNumeric, IsUnbound, IsData, IsParVar]
# as a list of bounds [lower, upper] (inequality constraints)
IsBound = List[IsExact, IsExact]
# as a dictionary of exact values or bounds, with keys being the temporal scale
IsTempDict = Dict[TemporalScale, Union[IsExact, IsBound]]

IsParameter = Union[IsExact, IsBound, IsTempDict]

# *Specific Aspect types
IsTemporal = TemporalScale
IsLimit = Union[IsExact, IsBound, IsTempDict]
IsCapBound = Union[IsExact, IsBound]
IsCashFlow, IsLand, IsEmission, IsLife, IsLoss = (IsExact for _ in range(5))

# *Classes and Enums
IsAspect = Union[CashFlow, Emission, Land, Life, Limit, Loss]
IsComponent = Union[Resource, Process, Location, Transport, Linkage]
IsSpatialPair = Union[Tuple[Process, Location], Tuple[Transport, Linkage]]
IsDeclaredAt = Union[IsSpatialPair, IsComponent]
