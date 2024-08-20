from typing import TypeAlias, Union

from ...disposition.bounds import SpcLmt, VarBnd
from ...parameters.balance.conversion import Conversion
from ...parameters.balance.inventory import Inventory
from ...parameters.designators.mode import X
from ...parameters.values.constant import Constant
from ...parameters.values.dataset import DataSet
from ...parameters.values.m import M
from ...parameters.values.theta import Theta

# Value
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

# Bound types
# is parameter bound on variable
IsVarBnd: TypeAlias = VarBnd
# is a limit to the domain of a parametric variable
IsSpcLmt: TypeAlias = SpcLmt

# Operation Balances
# Process Conversion
IsConv: TypeAlias = Conversion
# Inventory Balance for Storage
IsInv: TypeAlias = Inventory

# Is operating mode
IsMode: TypeAlias = X
