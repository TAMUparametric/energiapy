""" Aliases for Variables 
"""

from typing import TypeAlias, Union

from ...variables.capacitate import Capacity
from ...variables.emit import (EmitBuy, EmitCap, EmitLoss, EmitSell, EmitSys,
                               EmitUse)
from ...variables.expense import (Credit, Earn, ExpBuy, ExpCap, ExpOp, ExpSell,
                                  ExpUse, Penalty, Spend)
from ...variables.loss import Loss
from ...variables.operate import Produce, Store, Transport
from ...variables.trade import Buy, Recieve, Sell, Ship
from ...variables.use import Use

IsCapacity: TypeAlias = Capacity
IsEmit: TypeAlias = Union[EmitSys, EmitBuy, EmitSell, EmitLoss, EmitUse, EmitCap]
IsExpense: TypeAlias = Union[
    Spend, Earn, ExpBuy, ExpSell, Penalty, Credit, ExpUse, ExpCap, ExpOp
]
IsLoss: TypeAlias = Loss
IsOperate: TypeAlias = Union[Produce, Store, Transport]
IsTrade: TypeAlias = Union[Buy, Sell, Ship, Recieve]
IsUse: TypeAlias = Use

IsVariable: TypeAlias = Union[
    IsCapacity, IsEmit, IsExpense, IsLoss, IsOperate, IsTrade, IsUse
]
