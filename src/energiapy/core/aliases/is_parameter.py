"""Aliases for parameters
"""

from typing import TypeAlias, Union

from ...parameters.defined.bound import (BuyBnd, CapBnd, EarnBnd, OprBnd,
                                         SellBnd, ShipBnd, SpendBnd, UseBnd)
from ...parameters.defined.emission import (BuyEmit, EmitBnd, LossEmit,
                                            SellEmit, SetUpEmit, UseEmit)
from ...parameters.defined.expense import (BuyPrice, CapExp, OpExp, ResCredit,
                                           ResPenalty, SellPrice, UseExp)
from ...parameters.defined.loss import ResLoss
from ...parameters.defined.use import LndUse, MatUse

IsTradeBnd: TypeAlias = Union[BuyBnd, SellBnd, ShipBnd]
IsUseBnd: TypeAlias = UseBnd
IsExpBnd: TypeAlias = Union[SpendBnd, EarnBnd]
IsResExp: TypeAlias = Union[BuyPrice, SellPrice, ResCredit, ResPenalty]
IsUseExp: TypeAlias = UseExp
IsOpnExp: TypeAlias = Union[CapExp, OpExp]
IsResLoss: TypeAlias = ResLoss
IsOpnBnd: TypeAlias = Union[CapBnd, OprBnd]
IsEmitBnd: TypeAlias = EmitBnd
IsCmdUse: TypeAlias = Union[LndUse, MatUse]
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
