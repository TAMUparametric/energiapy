"""TypeAliases for Program Elements 
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

]"""Type aliases for Constraints"""

from typing import TypeAlias, Union

from ...constraints.bind import Bind
from ...constraints.calculate import Calculate
from ...constraints.sumover import SumOver



from typing import TypeAlias, Union

from ...parameters.defined.bound import (BuyBnd, CapBnd, EarnBnd, EmitBnd,
                                         OprBnd, SellBnd, ShipBnd, SpendBnd,
                                         UseBnd)
from ...parameters.defined.emission import (BuyEmit, LossEmit, SellEmit,
                                            SetUpEmit, UseEmit)
from ...parameters.defined.expense import (BuyPrice, CapExp, OpExp, ResCredit,
                                           ResPenalty, SellPrice, UseExp)
from ...parameters.defined.loss import ResLoss
from ...parameters.defined.usage import Usage

IsElement: TypeAlias = Union[IsParameter, IsVariable, IsConstraint]



IsCapacity: TypeAlias = Capacity, Emit, EmitBuy, EmitSell, EmitLoss, EmitUse, EmitSetUp]
  
  Spend, Earn, ExpBuy, ExpSell, Penalty, Credit, ExpUseSetUp, ExpSetUp, ExpOpr
]
IsLoss: TypeAlias = Loss
IsOperate: TypeAlias = Operate
IsTrade: TypeAlias = Union[Buy, Sell, Ship]
IsUse: TypeAlias = Use

IsVariable: TypeAlias = Union[
    IsCapacity, IsEmit, IsExpense, IsLoss, IsOperate, IsTrade, IsUse


IsBind: TypeAlias = Bind
IsCalculate: TypeAlias = Calculate
IsSumOver: TypeAlias = SumOver

IsConstraint = IsBind | IsCalculate | IsSumOver


IsTradeBnd: TypeAlias = Union[BuyBnd, SellBnd, ShipBnd]
IsUseBnd: TypeAlias = UseBnd
IsExpBnd: TypeAlias = Union[SpendBnd, EarnBnd]
IsResExp: TypeAlias = Union[BuyPrice, SellPrice, ResCredit, ResPenalty]
IsUseExp: TypeAlias = UseExp
IsOpnExp: TypeAlias = Union[CapExp, OpExp]
IsResLoss: TypeAlias = ResLoss
IsOpnBnd: TypeAlias = Union[CapBnd, OprBnd]
IsEmitBnd: TypeAlias = EmitBnd
IsCmdUse: TypeAlias = Usage
IsResEmits: TypeAlias = Union[BuyEmit, SellEmit, LossEmit]
IsCmdEmit: TypeAlias = UseEmit
IsOpnEmit: TypeAlias = SetUpEmit

IsParameter: TypeAlias = Union[
    IsTradeBnd,
    IsUseBnd,
    IsExpBnd,
    IsResExp,
    IsUseExp,
    IsOpnExp,
    IsCmdUse,
    IsResLoss,
    IsOpnBnd,
]
