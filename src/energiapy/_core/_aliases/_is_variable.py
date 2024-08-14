""" Aliases for Variables 
"""

from typing import TypeAlias, Union

from ...variables.capacitate import Capacity
from ...variables.emit import (
    EmitBuy,
    EmitOpn,
    EmitLoss,
    EmitSell,
    EmitSys,
    EmitUse,
)
from ...variables.expense import (
    Credit,
    ExpBuy,
    ExpCap,
    ExpOp,
    ExpSell,
    ExpSys,
    ExpUse,
    Penalty,
)
from ...variables.loss import Loss
from ...variables.operate import Operate
from ...variables.trade import Buy, Sell, Ship
from ...variables.use import Use

IsCapacity: TypeAlias = Capacity
IsEmit: TypeAlias = Union[EmitSys, EmitBuy, EmitSell, EmitLoss, EmitUse, EmitOpn]
IsExpense: TypeAlias = Union[
    ExpSys, ExpBuy, ExpSell, Penalty, Credit, ExpUse, ExpCap, ExpOp
]
IsLoss: TypeAlias = Loss
IsOperate: TypeAlias = Operate
IsTrade: TypeAlias = Union[Buy, Sell, Ship]
IsUse: TypeAlias = Use

IsVariable: TypeAlias = Union[
    IsCapacity, IsEmit, IsExpense, IsLoss, IsOperate, IsTrade, IsUse
]
