"""Aliases for parameters
"""

from typing import TypeAlias, Union

from ...parameters.bound import BuyBnd, CapBnd, ExpBnd, OpBnd, SellBnd
from ...parameters.expense import (
    BuyPrice,
    CapExp,
    OpExp,
    ResCredit,
    ResPenalty,
    SellPrice,
    UseExp,
)
from ...parameters.calculated import CmdUse, ResLoss
from ...parameters.emission import (
    EmitBnd,
    ResEmitBuy,
    ResEmitSell,
    CmdEmitUse,
    OpnEmit,
    ResEmitLoss,
)


IsTradeBnd: TypeAlias = Union[BuyBnd, SellBnd]
IsCmdUse: TypeAlias = CmdUse
IsExpBnd: TypeAlias = ExpBnd
IsResExp: TypeAlias = Union[BuyPrice, SellPrice, ResCredit, ResPenalty]
IsUseExp: TypeAlias = UseExp
IsOpnExp: TypeAlias = Union[CapExp, OpExp]
IsResLoss: TypeAlias = ResLoss
IsOpnBnd: TypeAlias = Union[CapBnd, OpBnd]
IsEmitBnd: TypeAlias = EmitBnd
IsResEmits: TypeAlias = Union[ResEmitBuy, ResEmitSell, ResEmitLoss]
IsCmdEmit: TypeAlias = CmdEmitUse
IsOpnEmit: TypeAlias = OpnEmit

IsParameter: TypeAlias = Union[
    IsTradeBnd, IsCmdUse, IsExpBnd, IsResExp, IsUseExp, IsOpnExp, IsResLoss, IsOpnBnd
]
