from typing import TypeAlias, Union

from ...values._bounds import _SpcLmt, _VarBnd
from ...values.constant import Constant
from ...values.dataset import DataSet
from ...values.m import M
from ...values.theta import Theta

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
IsData: TypeAlias = Union[IsConstant, IsDataSet, IsM, IsParVar]

# *Bound types
# is parameter bound on variable
IsVarBnd: TypeAlias = _VarBnd
# is a limit to the domain of a parametric variable
IsSpcLmt: TypeAlias = _SpcLmt
