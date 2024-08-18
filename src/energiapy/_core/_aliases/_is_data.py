from typing import TypeAlias, Union

from ...parameters.bounds import SpcLmt, VarBnd
from ...parameters.data.constant import Constant
from ...parameters.data.conversion import Conversion
from ...parameters.data.dataset import DataSet
from ...parameters.data.m import M
from ...parameters.data.theta import Theta
from ...parameters.designators.mode import X

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
IsValue: TypeAlias = Union[IsConstant, IsDataSet, IsM, IsParVar]

# *Bound types
# is parameter bound on variable
IsVarBnd: TypeAlias = VarBnd
# is a limit to the domain of a parametric variable
IsSpcLmt: TypeAlias = SpcLmt

IsConv: TypeAlias = Conversion

# Is operating mode
IsMode: TypeAlias = X
