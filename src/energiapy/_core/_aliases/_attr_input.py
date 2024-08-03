from typing import List, Literal, Tuple, Union, Dict

from pandas import DataFrame
from ...data.m import BigM
from ...data.theta import Th
from .component import IsScale, IsSpatial


# *input types
IsNumeric = Union[float, int]
# is unbounded (=< BigM), constraint not written by variable declared
# a futher check of whether value is True is required
# so if value are given as False, then they are set to None
IsBig = Union[Literal[True], Literal[BigM]]
# deterministic data is provided
IsDataF = DataFrame
# a range is give, treated as bounds for a parameteric variable
IsSpaceBound = Union[IsNumeric, IsDataF]
IsSpace = Union[Tuple[IsSpaceBound, IsSpaceBound], Literal[Th]]
# as an exact value (equality constraint)
IsExact = Union[IsNumeric, IsDataF, IsSpace]
# as a list of bounds [lower, upper] (inequality constraints)
IsBound = Union[IsExact, IsBig, List[IsExact, IsBig]]

IsBaseInput = Union[IsExact, IsBound]

# *compound input types
IsTmpExact = Dict[IsScale, IsExact]
IsTmpBound = Dict[IsScale, IsBound]

IsTmpInput = Union[IsTmpExact, IsTmpBound]

IsSptExact = Dict[IsSpatial, IsExact]
IsSptBound = Dict[IsSpatial, IsBound]

IsSptInput = Union[IsSptExact, IsSptBound]

IsSptTmpExact = Dict[IsSpatial, IsTmpExact]
IsSptTmpBound = Dict[IsSpatial, IsTmpBound]

IsSptTmpInput = Union[IsSptTmpExact, IsSptTmpBound]

# *attribute inputs
IsExactInput = Union[IsExact, IsTmpExact, IsSptExact, IsSptTmpExact]

IsBoundInput = Union[IsBound, IsTmpBound, IsSptBound, IsSptTmpBound]

IsInput = Union[IsExactInput, IsBoundInput]
