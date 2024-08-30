from typing import Dict, List, Literal, Tuple, TypeAlias, Union

from pandas import DataFrame
from ...components.temporal.scale import Scale
from ...components.spatial.location import Location
from ...components.spatial.linkage import Linkage
from ...components.scope.network import Network

# Parameter value input
type IsNumeric = float | int

DataFrame

# is unbounded (=< BigM), constraint not written by variable declared
# a futher check of whether value is True is required
# so if value are given as False, then they are set to None
type IsBig = Literal[True]


# a range is give, treated as bounds for a parameteric variable
type IsSpaceBound = IsNumeric | DataFrame
type IsSpace = tuple[IsSpaceBound, IsSpaceBound]

# as an exact value (equality constraint)
type IsExact = IsNumeric | DataFrame | IsSpace
type IsIncidental = set[IsExact]

# as a list of bounds [lower, upper] (inequality constraints)
type IsBound = IsExact | IsBig | list[IsExact | IsBig]


# compound input types
IsTmpExact = dict[Scale | IsExact]
IsTmpBound = dict[Scale | IsBound]

IsTmpInput = IsTmpExact | IsTmpBound

IsSpt = Location | Linkage 

IsSptExact: TypeAlias = Dict[IsSpt, IsExact]
IsSptBound: TypeAlias = Dict[IsSpt, IsBound]

IsSptInput: TypeAlias = Union[IsSptExact, IsSptBound]

IsSptTmpExact: TypeAlias = Dict[IsSpt, IsTmpExact]
IsSptTmpBound: TypeAlias = Dict[IsSpt | Network, IsTmpBound]

IsSptTmpDict: TypeAlias = Union[IsSptTmpExact, IsSptTmpBound]

IsSptTmpDict: TypeAlias = Union[Dict[IsMode, IsSptTmpDict], IsSptTmpDict]


# attribute inputs
IsExactInput: TypeAlias = Union[IsExact, IsTmpExact, IsSptExact, IsSptTmpExact]

IsBoundInput: TypeAlias = Union[IsBound, IsTmpBound, IsSptBound, IsSptTmpBound]

IsInput: TypeAlias = Union[IsExactInput, IsBoundInput]

IsInputDict: TypeAlias = Union[IsComponent, IsSptInput, IsSptTmpDict]

IsSingleConvInput: TypeAlias = Dict[IsResource, Dict[IsResource, IsNumeric]]

IsMultiConvInput: TypeAlias = Dict[IsMode, IsSingleConvInput]

IsConvInput = Union[IsSingleConvInput, IsMultiConvInput]

IsBalInput = Union[IsResource, IsConvInput]

type IsInput = IsExact | IsBound
