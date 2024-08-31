"""Aliases for Program Variable Elements 
"""

from ....elements.variables.act import Give, Take
from ....elements.variables.emit import (Emit, EmitBuy, EmitLss, EmitSll,
                                         EmitStp, EmitUse)
from ....elements.variables.lose import Lose
from ....elements.variables.operate import Operate
from ....elements.variables.rate import Rate
from ....elements.variables.setup import Capacity
from ....elements.variables.trade import Buy, Sell, Ship
from ....elements.variables.transact import (Earn, Spend, TransactBuy,
                                             TransactCrd, TransactOpr,
                                             TransactPnt, TransactSll,
                                             TransactStp, TransactUse)
from ....elements.variables.use import Use

# Bound Vars
type IsAct = Give | Take
type IsStp = Capacity
type IsOpr = Operate
type IsTrd = Buy | Sell | Ship
type IsBndVar = IsAct | IsStp | IsOpr | IsTrd

# Exact Vars
# The naming convention is:
# three character names are used for Parent Variables in the end
# so VariablePrn

type IsEmt = Emit | EmitBuy | EmitLss | EmitSll | EmitStp | EmitUse
type IsExp = (
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
type IsLss = Lose
type IsRte = Rate
type IsUse = Use
type IsExtVar = IsEmt | IsExp | IsLss | IsRte | IsUse

# All Variables
type IsVar = IsBndVar | IsExtVar
