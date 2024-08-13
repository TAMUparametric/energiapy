""" Aliases for Variables 
"""

from typing import TypeAlias, Union

from ...variables.capacitate import Capacitate
from ...variables.emit import (EmitBuy, EmitCap, EmitLoss, EmitSell, EmitSys,
                               EmitTrade, EmitUse)
from ...variables.expense import (Credit, ExpBuy, ExpCap, ExpOp, ExpSell,
                                  ExpSys, ExpUse, Penalty)
from ...variables.loss import Loss
from ...variables.operate import Operate
from ...variables.trade import Buy, Sell, Ship
from ...variables.use import Use

IsCapacitate: TypeAlias = Capacitate
IsEmit: TypeAlias = Union[
    EmitSys, EmitTrade, EmitBuy, EmitSell, EmitLoss, EmitUse, EmitCap
]
IsExpense: TypeAlias = Union[
    ExpSys, ExpBuy, ExpSell, Penalty, Credit, ExpUse, ExpCap, ExpOp
]
IsLoss: TypeAlias = Loss
IsOperate: TypeAlias = Operate
IsTrade: TypeAlias = Union[Buy, Sell, Ship]
IsUse: TypeAlias = Use

IsVariable: TypeAlias = Union[
    IsCapacitate, IsEmit, IsExpense, IsLoss, IsOperate, IsTrade, IsUse
]
