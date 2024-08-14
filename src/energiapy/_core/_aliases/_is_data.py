from typing import TypeAlias, Union

from ...parameters.data.bounds import SpcLmt, VarBnd
from ...parameters.data.constant import Constant
from ...parameters.data.dataset import DataSet
from ...parameters.data.m import M
from ...parameters.data.theta import Theta

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
IsVarBnd: TypeAlias = VarBnd
# is a limit to the domain of a parametric variable
IsSpcLmt: TypeAlias = SpcLmt
