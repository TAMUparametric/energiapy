"""Aliases for Program Parameter Elements 
"""

from typing import TypeAlias

from ....components.scope.temporal.incidental import I
from ....elements.parameters.balances.conversion import Conversion
from ....elements.parameters.balances.freight import Freight
from ....elements.parameters.balances.inventory import Inventory
from ....elements.parameters.bounds.all import (BuyBound, CapBound, EmnBound,
                                                ErnBound, OprBound, ShpBound,
                                                SllBound, SpdBound, UseBound)
from ....elements.parameters.exacts.emission import (BuyEmission, LseEmission,
                                                     SllEmission, StpEmission,
                                                     UseEmission)
from ....elements.parameters.exacts.expense import (BuyPrice, OprExpense,
                                                    SllCredit, SllPenalty,
                                                    SllPrice, StpExpense,
                                                    UseCost)
from ....elements.parameters.exacts.loss import Loss
from ....elements.parameters.exacts.usage import Usage

# The naming convention is:
# three character names are used in the start for the variable
# this parameter models, data-driven modeling ftw
#

# Bound Parameters
IsResBnd: TypeAlias = BuyBound | SllBound | ShpBound
IsUsdBnd: TypeAlias = UseBound
IsTscBnd: TypeAlias = SpdBound | ErnBound
IsOpnBnd: TypeAlias = CapBound | OprBound
IsEmnBnd: TypeAlias = EmnBound

IsBndPar: TypeAlias = IsResBnd | IsUsdBnd | IsTscBnd | IsOpnBnd

# Exact Parameters
# Transacts
IsResExp: TypeAlias = BuyPrice | SllPrice | SllCredit | SllPenalty
IsUseExp: TypeAlias = UseCost
IsOpnExp: TypeAlias = StpExpense | OprExpense
# Emissions
IsResEmn: TypeAlias = BuyEmission | SllEmission | LseEmission
IsUsdEmn: TypeAlias = UseEmission
IsOpnEmn: TypeAlias = StpEmission
# Losses
IsLss: TypeAlias = Loss
# Usage
IsUsg: TypeAlias = Usage

IsExtPar: TypeAlias = (
    IsResExp | IsResEmn | IsUsdEmn | IsLss | IsUsg | IsOpnEmn | IsUseExp | IsOpnExp
)

# Balances
IsBal: TypeAlias = Conversion | Inventory | Freight

# Designators
# Incidental Parameter
IsDgn: TypeAlias = I

# All Parameters
IsPrm: TypeAlias = IsBndPar | IsExtPar | IsBal | IsDgn
