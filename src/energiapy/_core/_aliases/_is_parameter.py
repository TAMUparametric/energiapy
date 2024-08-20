"""Aliases for parameters
"""

from typing import TypeAlias, Union

from ...parameters.bound import (BuyBnd, CapBnd, EarnBnd, OpBnd, SellBnd,
                                 ShipBnd, SpendBnd, UseBnd)
from ...parameters.calculated import LndUse, MatUse, ResLoss
from ...parameters.emission import (CmdEmitUse, EmitBnd, OpnEmit, ResEmitBuy,
                                    ResEmitLoss, ResEmitSell)
from ...parameters.expense import (BuyPrice, CapExp, OpExp, ResCredit,
                                   ResPenalty, SellPrice, UseExp)

IsTradeBnd: TypeAlias = Union[BuyBnd, SellBnd, ShipBnd]
IsUseBnd: TypeAlias = UseBnd
IsExpBnd: TypeAlias = Union[SpendBnd, EarnBnd]
IsResExp: TypeAlias = Union[BuyPrice, SellPrice, ResCredit, ResPenalty]
IsUseExp: TypeAlias = UseExp
IsOpnExp: TypeAlias = Union[CapExp, OpExp]
IsResLoss: TypeAlias = ResLoss
IsOpnBnd: TypeAlias = Union[CapBnd, OpBnd]
IsEmitBnd: TypeAlias = EmitBnd
IsCmdUse: TypeAlias = Union[LndUse, MatUse]
IsResEmits: TypeAlias = Union[ResEmitBuy, ResEmitSell, ResEmitLoss]
IsCmdEmit: TypeAlias = CmdEmitUse
IsOpnEmit: TypeAlias = OpnEmit

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
