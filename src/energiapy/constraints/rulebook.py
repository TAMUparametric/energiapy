"""RuleBook for Constraint generation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from operator import is_
from typing import TYPE_CHECKING, List, Dict

from .rules import Condition, SumOver
from .._core._nirop._error import CacodcarError

from ..variables.capacitate import Capacity
from ..variables.emit import (
    EmitBuy,
    EmitOpn,
    EmitLoss,
    EmitSell,
    EmitSys,
    EmitUse,
)

from ..variables.expense import (
    Credit,
    ExpBuy,
    ExpCap,
    ExpOp,
    ExpSell,
    ExpSys,
    ExpUse,
    Penalty,
)
from ..variables.loss import Loss
from ..variables.operate import Operate
from ..variables.trade import Buy, Sell
from ..variables.use import Use

from ..parameters.bound import BuyBnd, CapBnd, ExpBnd, OpBnd, SellBnd
from ..parameters.expense import (
    BuyPrice,
    CapExp,
    OpExp,
    ResCredit,
    ResPenalty,
    SellPrice,
    UseExp,
)
from ..parameters.calculated import CmdUse, ResLoss
from ..parameters.emission import (
    EmitBnd,
    ResEmitBuy,
    ResEmitSell,
    CmdEmitUse,
    OpnEmit,
    ResEmitLoss,
)

from .._core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from .._core._aliases._is_element import IsVariable, IsParameter


@dataclass
class Rule(_Dunders):
    """Rule for Constraint generation"""

    condition: Condition = field(default=None)
    variable: IsVariable = field(default=None)
    parameter: IsParameter = field(default=None)
    balance: Dict[IsVariable, float] = field(default=None)
    sumover: SumOver = field(default=None)

    def __post_init__(self):

        if not any([self.variable.parent(), self.parameter]):
            raise CacodcarError(
                'Rule must have at least one of parent (variable) or parameter'
            )
        variable, parent, parameter = ('' for _ in range(3))

        if self.variable:
            variable = f'var:{self.variable.id()}|'
        if self.variable.parent():
            parent = f'pvar:{self.variable.parent().id()}|'
        if self.parameter:
            parameter = f'Param:{self.parameter.id()}|'

        self.name = f'{self.condition.name}|{variable}{parent}{parameter}'


@dataclass
class RuleBook:
    """RuleBook for constraint generation"""

    rules: List[Rule] = None

    def __post_init__(self):
        self.rules = []
        self.name = 'RuleBook'

    def add(self, rule: Rule):
        """Add Rule to RuleBook"""
        self.rules.append(rule)

    def find(self, variable: IsVariable):
        """Fetch the rules that apply for a particular variable"""
        return [rule for rule in self.rules if is_(rule.variable, variable)]


rulebook = RuleBook()

# Bounded
trade_bnd = [(Buy, BuyBnd), (Sell, SellBnd)]
cap_bnd = [(Capacity, CapBnd)]
op_bnd = [(Operate, OpBnd)]
exp_bnd = [(ExpSys, ExpBnd)]
emn_bnd = [(EmitSys, EmitBnd)]

# Calculated
use_cmd = [(Use, CmdUse)]
loss = [(Loss, ResLoss)]

# Calculated Expenses
exp_res = [
    (ExpBuy, BuyPrice),
    (ExpSell, SellPrice),
    (Credit, ResCredit),
    (Penalty, ResPenalty),
]
exp_use = [(ExpUse, UseExp)]
exp_opn = [(ExpOp, OpExp), (ExpCap, CapExp)]

# Calculated Emissions
emit = [
    (EmitBuy, ResEmitBuy),
    (EmitSell, ResEmitSell),
    (EmitUse, CmdEmitUse),
    (EmitOpn, OpnEmit),
    (EmitLoss, ResEmitLoss),
]

for var, param in trade_bnd + cap_bnd + op_bnd + exp_bnd + emn_bnd:

    rulebook.add(
        Rule(
            variable=var,
            parameter=param,
            condition=Condition.BIND,
        )
    )

for var, param in use_cmd + loss + exp_res + exp_use + exp_opn + emit:
    rulebook.add(
        Rule(
            variable=var,
            parameter=param,
            condition=Condition.CALCULATE,
        )
    )
