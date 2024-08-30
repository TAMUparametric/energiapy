""" Aliases for Variables 
"""

from typing import TypeAlias, Union

from ...variables.capacitate import Capacity
from ...variables.emit import (Emit, EmitBuy, EmitLoss, EmitSell, EmitSetUp,
                               EmitUse)
from ...variables.expense import (Credit, Earn, ExpBuy, ExpOpr, ExpSell,
                                  ExpSetUp, ExpUseSetUp, Penalty, Spend)
from ...variables.loss import Loss
from ...variables.operate import Operate
from ...variables.trade import Buy, Sell, Ship
from ...variables.use import Use

IsCapacity: TypeAlias = Capacity
IsEmit: TypeAlias = Union[Emit, EmitBuy, EmitSell, EmitLoss, EmitUse, EmitSetUp]
IsExpense: TypeAlias = Union[
    Spend, Earn, ExpBuy, ExpSell, Penalty, Credit, ExpUseSetUp, ExpSetUp, ExpOpr
]
IsLoss: TypeAlias = Loss
IsOperate: TypeAlias = Operate
IsTrade: TypeAlias = Union[Buy, Sell, Ship]
IsUse: TypeAlias = Use

IsVariable: TypeAlias = Union[
    IsCapacity, IsEmit, IsExpense, IsLoss, IsOperate, IsTrade, IsUse
]
