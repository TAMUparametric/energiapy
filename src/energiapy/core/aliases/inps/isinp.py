"""Aliases for User Inputs
"""

from typing import Literal, TypeAlias

from pandas import DataFrame

from ....components.scope.spatial.linkage import Linkage
from ....components.scope.spatial.location import Location
from ....components.scope.spatial.network import Network
from ....components.scope.temporal.incidental import I
from ....components.scope.temporal.mode import X
from ....components.scope.temporal.scale import Scale

# --------------Base Inputs--------------

# Parameter value input
IsNum: TypeAlias = float | int

# is unbounded (=< BigM), constraint not written by variable declared
# a futher check of whether value is True is required
# so if value are given as False, then they are set to None
IsBig: TypeAlias = Literal[True]


# a range is give, treated as bounds for a parameteric variable
IsSpcBnd: TypeAlias = IsNum | DataFrame
IsSpc: TypeAlias = tuple[IsSpcBnd, IsSpcBnd]


# as an exact value (equality constraint)
IsExtInp: TypeAlias = IsNum | DataFrame | IsSpc

# has an incidental parameter input
IsIncInp: TypeAlias = set[IsExtInp | I]

# as a list of bounds [lower, upper (inequality constraints)
IsBndInp: TypeAlias = IsExtInp | IsBig | list[IsExtInp | IsBig]


# --------------Inputs Provided as Dictionaries--------------


# Only Spatial Disposition is provided
IsSptExt: TypeAlias = dict[Location | Linkage, IsExtInp]
IsSptInc: TypeAlias = dict[Location | Linkage, IsIncInp]
IsSptBnd: TypeAlias = dict[Location | Linkage | Network, IsBndInp]

# Only Temporal Disposition is provided
IsTmpExt: TypeAlias = dict[Scale, IsExtInp]
IsTmpInc: TypeAlias = dict[Scale, IsIncInp]
IsTmpBnd: TypeAlias = dict[Scale, IsBndInp]

# Only Mode is Provided, these have to be Exact or Incidental inputs
IsMdeExt: TypeAlias = dict[X, IsExtInp]
IsMdeInc: TypeAlias = dict[X, IsIncInp]

# --------------Compound Dict Inputs--------------

# Both Spatial and Temporal Dispositions are provided
IsSptTmpExt: TypeAlias = dict[Location | Linkage, IsTmpExt]
IsSptTmpInc: TypeAlias = dict[Location | Linkage, IsTmpInc]
IsSptTmpBnd: TypeAlias = dict[Location | Linkage | Network, IsTmpBnd]


# SpatioTemporal and Mode Dispositions are provided
IsSptMdeExt: TypeAlias = dict[Location | Linkage, IsMdeExt]
IsTmpMdeExt: TypeAlias = dict[Scale, IsMdeExt]
IsSptTmpMdeExt: TypeAlias = dict[Location | Linkage, IsTmpMdeExt]

# with incidental values
IsSptMdeInc: TypeAlias = dict[Location | Linkage, IsMdeInc]
IsTmpMdeInc: TypeAlias = dict[Scale, IsMdeInc]
IsSptTmpMdeInc: TypeAlias = dict[Location | Linkage, IsTmpMdeInc]

IsSptTmp: TypeAlias = (
    IsSptTmpExt | IsSptTmpInc | IsSptTmpBnd | IsSptTmpMdeExt | IsSptTmpMdeInc
)

# attribute inputs
IsExt: TypeAlias = (
    IsExtInp
    | IsSptExt
    | IsTmpExt
    | IsMdeExt
    | IsSptTmpExt
    | IsSptMdeExt
    | IsTmpMdeExt
    | IsSptTmpMdeExt
)

IsInc: TypeAlias = (
    IsIncInp
    | IsSptInc
    | IsTmpInc
    | IsMdeInc
    | IsSptTmpInc
    | IsSptMdeInc
    | IsTmpMdeInc
    | IsSptTmpMdeInc
)

IsBnd: TypeAlias = IsBndInp | IsSptBnd | IsTmpBnd | IsSptTmpBnd

IsInp: TypeAlias = IsExt | IsInc | IsBnd
