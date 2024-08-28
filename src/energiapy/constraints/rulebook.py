"""RuleBook for Constraint generation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from operator import is_
from typing import TYPE_CHECKING, Dict, List

from ..constraints.bind import Bind
from ..constraints.calculate import Calculate
from ..core._handy._dunders import _Dunders
from ..core.nirop.errors import CacodcarError
from ..parameters.defined.bound import (
    BuyBnd,
    CapBnd,
    EarnBnd,
    OprBnd,
    SellBnd,
    ShipBnd,
    SpendBnd,
    UseBnd,
    EmitBnd,
    Has,
    Needs,
)
from ..parameters.defined.emission import (
    UseEmit,
    SetUpEmit,
    BuyEmit,
    LossEmit,
    SellEmit,
)
from ..parameters.defined.expense import (
    BuyPrice,
    CapExp,
    CapExpI,
    OpExp,
    OpExpI,
    ResCredit,
    ResPenalty,
    SellPrice,
    UseExp,
)
from ..parameters.defined.loss import ResLoss
from ..parameters.defined.use import LndUse, MatUse
from ..variables.action import Give, Take
from ..variables.capacitate import Capacity
from ..variables.emit import EmitBuy, EmitSetUp, EmitLoss, EmitSell, Emit, EmitUse
from ..variables.expense import (
    Credit,
    Earn,
    ExpBuy,
    ExpSetUp,
    ExpSetUpI,
    ExpOpr,
    ExpOprI,
    ExpSell,
    ExpUsage,
    Penalty,
    Spend,
)
from ..variables.loss import Loss
from ..variables.operate import Operate
from ..variables.trade import Buy, Sell, Ship
from ..variables.use import Use, Usage
from .rules import Condition, SumOver

if TYPE_CHECKING:
    from ..core.aliases.is_element import IsConstraint, IsParameter, IsVariable


@dataclass
class Rule(_Dunders):
    """Rule for Constraint generation

    Attributes:
        constraint (IsConstraint): The Constraint to apply
        variable (IsVariable): The main Variable in the Rule
        parameter (IsParameter): The associated Parameter of the Variable
        balance (Dict[IsVariable, float]): Variables to balance at some spatio temporal disposition
        sumover (SumOver): Sum over either a Spatial or Temporal dimension
    """

    constraint: IsConstraint = field(default=None)
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
            parameter = f'Param:{self.parameter.id}|'

        self.name = f'{self.constraint.id()}|{variable}{parent}{parameter}'


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
        rule = [rule for rule in self.rules if is_(rule.variable, variable)]
        if rule:
            return rule
        else:
            raise CacodcarError(f'No Rule found for {variable.id()}')


rulebook = RuleBook()

# Bounded
trade_bnd = [(Buy, BuyBnd), (Sell, SellBnd), (Ship, ShipBnd)]
cap_bnd = [(Capacity, CapBnd)]
op_bnd = [(Operate, OprBnd)]
exp_bnd = [(Spend, SpendBnd), (Earn, EarnBnd)]
emission_bnd = [(Emit, EmitBnd)]
ply_bnd = [(Give, Has), (Take, Needs)]
use_bnd = [(Use, UseBnd)]

# Calculated
use_cmd = [(Usage, LndUse), (Usage, MatUse)]
loss = [(Loss, ResLoss)]

# Calculated Expenses
exp_res = [
    (ExpBuy, BuyPrice),
    (ExpSell, SellPrice),
    (Credit, ResCredit),
    (Penalty, ResPenalty),
]
exp_use = [(ExpUsage, UseExp)]
exp_opn = [(ExpOpr, OpExp), (ExpSetUp, CapExp), (ExpOprI, OpExpI), (ExpSetUpI, CapExpI)]

# Calculated Emissions
emit = [
    (EmitBuy, BuyEmit),
    (EmitSell, SellEmit),
    (EmitUse, UseEmit),
    (EmitSetUp, SetUpEmit),
    (EmitLoss, LossEmit),
]

for var, param in (
    trade_bnd + cap_bnd + op_bnd + exp_bnd + emission_bnd + ply_bnd + use_bnd
):

    rulebook.add(
        Rule(
            variable=var,
            parameter=param,
            constraint=Bind,
        )
    )

for var, param in use_cmd + loss + exp_res + exp_use + exp_opn + emit:
    rulebook.add(
        Rule(
            variable=var,
            parameter=param,
            constraint=Calculate,
        )
    )
