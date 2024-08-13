"""Aliases for parameters
"""

from typing import TypeAlias, Union

from ...parameters.parameter import (BuyBnd, BuyPrice, CapBnd, CapExp, CmdUse,
                                     ExpBnd, OpExp, ResCredit, ResLoss,
                                     ResPenalty, SellBnd, SellPrice, UseExp)

IsTradeBnd: TypeAlias = Union[BuyBnd, SellBnd]
IsCmdUse: TypeAlias = CmdUse
IsExpBnd: TypeAlias = ExpBnd
IsResExp: TypeAlias = Union[BuyPrice, SellPrice, ResCredit, ResPenalty]
IsUseExp: TypeAlias = UseExp
IsOpnExp: TypeAlias = Union[CapExp, OpExp]
IsResLoss: TypeAlias = ResLoss
IsCapBnd: TypeAlias = CapBnd

IsParameter: TypeAlias = Union[
    IsTradeBnd, IsCmdUse, IsExpBnd, IsResExp, IsUseExp, IsOpnExp, IsResLoss, IsCapBnd
]
