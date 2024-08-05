from typing import Union, TypeAlias

from ...data._bounds import _SpcLmt, _VarBnd
from ...data.constant import Constant
from ...data.dataset import DataSet
from ...data.m import M
from ...data.theta import Theta

# * Value
# these are generated internally
IsConstant: TypeAlias = Constant
# if a range is provided
IsParVar: TypeAlias = Theta
# if deterministic data is provided
IsDataSet: TypeAlias = DataSet
# if unbounded
IsM: TypeAlias = M
# this is the value attribute of Value dataclass
IsData: TypeAlias = Union[IsConstant, IsParVar, IsDataSet, IsM]

# *Bound types
# is parameter bound on variable
IsVarBnd: TypeAlias = _VarBnd
# is a limit to the domain of a parametric variable
IsSpcLmt: TypeAlias = _SpcLmt
