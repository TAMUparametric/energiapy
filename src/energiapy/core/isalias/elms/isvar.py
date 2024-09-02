"""Aliases for Program Variable Elements 
"""

from typing import TypeAlias

from ....elements.variables.boundbounds.operate import Operate
from ....elements.variables.bounds.act import Give, Take
from ....elements.variables.bounds.capacitate import Capacitate
from ....elements.variables.bounds.trade import Buy, Sell, Ship
from ....elements.variables.exacts.emit import (Emit, EmitBuy, EmitLse,
                                                EmitSll, EmitStp, EmitUse)
from ....elements.variables.exacts.lose import Lose
from ....elements.variables.exacts.rate import Rate
from ....elements.variables.transact import (Earn, Spend, TransactBuy,
                                             TransactCrd, TransactOpr,
                                             TransactPnt, TransactSll,
                                             TransactStp, TransactUse)
from ....elements.variables.use import Use

# Bound Vars
IsAct: TypeAlias = Give | Take
IsStp: TypeAlias = Capacitate
IsOpr: TypeAlias = Operate
IsTrd: TypeAlias = Buy | Sell | Ship
IsBndVar: TypeAlias = IsAct | IsStp | IsOpr | IsTrd

# Exact Vars
# The naming convention is:
# three character names are used for Parent Variables in the end
# so VariablePrn

IsEmt: TypeAlias = Emit | EmitBuy | EmitLse | EmitSll | EmitStp | EmitUse
IsTsc: TypeAlias = (
    Earn
    | Spend
    | TransactBuy
    | TransactOpr
    | TransactSll
    | TransactStp
    | TransactUse
    | TransactPnt
    | TransactCrd
)
IsLse: TypeAlias = Lose
IsRte: TypeAlias = Rate
IsUse: TypeAlias = Use
IsExtVar: TypeAlias = IsEmt | IsTsc | IsLse | IsRte | IsUse

# All Variables
IsVar: TypeAlias = IsBndVar | IsExtVar
