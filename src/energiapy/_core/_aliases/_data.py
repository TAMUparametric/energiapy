from typing import Union

from ...data._bounds import _SpcLmt, _VarBnd
from ...data.constant import Constant
from ...data.dataset import DataSet
from ...data.m import M
from ...data.theta import Theta

# * Value
# these are generated internally
IsConstant = Constant
# if a range is provided
IsParVar = Theta
# if deterministic data is provided
IsDataSet = DataSet
# if unbounded
IsM = M
# this is the value attribute of Value dataclass
IsData = Union[IsConstant, IsParVar, IsDataSet, IsM]

# *Bound types
# is parameter bound on variable
IsVarBnd = _VarBnd
# is a limit to the domain of a parametric variable
IsSpcLmt = _SpcLmt
