from typing import Dict, List, Literal, Tuple, TypeAlias, Union

from pandas import DataFrame

from ...parameters.data.m import M
from ...parameters.data.theta import Theta
from ._is_component import IsComponent, IsResource, IsScale, IsSpatial
from ._is_data import IsMode

# input types
IsNumeric: TypeAlias = Union[float, int]

# deterministic data is provided
IsDataFr: TypeAlias = DataFrame

# can be given as an incidental parameter
IsIncidental: TypeAlias = Union[IsNumeric, IsDataFr]

# is unbounded (=< BigM), constraint not written by variable declared
# a futher check of whether value is True is required
# so if value are given as False, then they are set to None
IsBig: TypeAlias = Union[Literal[True], M]

# a range is give, treated as bounds for a parameteric variable
IsSpaceBound: TypeAlias = Union[IsNumeric, IsDataFr]
IsSpace: TypeAlias = Union[Tuple[IsSpaceBound, IsSpaceBound], Theta]

# as an exact value (equality constraint)
IsExact: TypeAlias = Union[IsNumeric, IsDataFr, IsSpace]

# as a list of bounds [lower, upper] (inequality constraints)
IsBound: TypeAlias = Union[IsExact, IsBig, List[Union[IsExact, IsBig]]]

IsBaseInput: TypeAlias = Union[IsExact, IsBound]

# compound input types
IsTmpExact: TypeAlias = Dict[IsScale, IsExact]
IsTmpBound: TypeAlias = Dict[IsScale, IsBound]

IsTmpInput: TypeAlias = Union[IsTmpExact, IsTmpBound]

IsSptExact: TypeAlias = Dict[IsSpatial, IsExact]
IsSptBound: TypeAlias = Dict[IsSpatial, IsBound]

IsSptInput: TypeAlias = Union[IsSptExact, IsSptBound]

IsSptTmpExact: TypeAlias = Dict[IsSpatial, IsTmpExact]
IsSptTmpBound: TypeAlias = Dict[IsSpatial, IsTmpBound]

IsSptTmpInput: TypeAlias = Union[IsSptTmpExact, IsSptTmpBound]

IsSptTmpInput: TypeAlias = Union[Dict[IsMode, IsSptTmpInput], IsSptTmpInput]


# attribute inputs
IsExactInput: TypeAlias = Union[IsExact, IsTmpExact, IsSptExact, IsSptTmpExact]

IsBoundInput: TypeAlias = Union[IsBound, IsTmpBound, IsSptBound, IsSptTmpBound]

IsInput: TypeAlias = Union[IsExactInput, IsBoundInput]

IsInputDict: TypeAlias = Union[IsComponent, IsSptInput, IsSptTmpInput]

IsSingleConvInput: TypeAlias = Dict[IsResource, Dict[IsResource, IsNumeric]]

IsMultiConvInput: TypeAlias = Dict[IsMode, IsSingleConvInput]

IsConvInput = Union[IsSingleConvInput, IsMultiConvInput]

IsInvInput = Union[IsResource, IsConvInput]
