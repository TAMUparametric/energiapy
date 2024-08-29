"""RuleBook for Constraint generation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from operator import is_
from typing import TYPE_CHECKING, Dict

from ..constraints.bind import Bind
from ..constraints.calculate import Calculate
from ..constraints.rules import Condition, SumOver
from ..core._handy._dunders import _Dunders
from ..core.nirop.errors import CacodcarError
from ..parameters.defined.bound import (BuyBnd, CapBnd, EarnBnd, EmitBnd, Has,
                                        Needs, OprBnd, SellBnd, ShipBnd,
                                        SpendBnd, UseBnd)
from ..parameters.defined.emission import (BuyEmit, LossEmit, SellEmit,
                                           SetUpEmit, UseEmit)
from ..parameters.defined.expense import (BuyPrice, CapExp, CapExpI, OpExp,
                                          OpExpI, ResCredit, ResPenalty,
                                          SellPrice, UseExp)
from ..parameters.defined.loss import ResLoss
from ..parameters.defined.usage import Usage
from ..variables.action import Give, Take
from ..variables.capacitate import Capacity
from ..variables.emit import (Emit, EmitBuy, EmitLoss, EmitSell, EmitSetUp,
                              EmitUse)
from ..variables.expense import (Credit, Earn, ExpBuy, ExpOpr, ExpOprI,
                                 ExpSell, ExpSetUp, ExpSetUpI, ExpUseSetUp,
                                 Penalty, Spend)
from ..variables.loss import Loss
from ..variables.operate import Operate
from ..variables.trade import Buy, Sell, Ship
from ..variables.use import Use, UseSetUp

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
    """RuleBook for constraint generation

    Attributes:
        name (str): name of the RuleBook, borrows from Scenario
    """

    name: str = field(default=None)

    def __post_init__(self):
        self.rules = []
        self.name = 'RuleBook'
        # Bounded
        trade_bnd = [(Buy, BuyBnd), (Sell, SellBnd), (Ship, ShipBnd)]
        cap_bnd = [(Capacity, CapBnd)]
        op_bnd = [(Operate, OprBnd)]
        exp_bnd = [(Spend, SpendBnd), (Earn, EarnBnd)]
        emission_bnd = [(Emit, EmitBnd)]
        ply_bnd = [(Give, Has), (Take, Needs)]
        use_bnd = [(Use, UseBnd)]

        # Calculated
        use_cmd = [(UseSetUp, Usage)]
        loss = [(Loss, ResLoss)]

        # Calculated Expenses
        exp_res = [
            (ExpBuy, BuyPrice),
            (ExpSell, SellPrice),
            (Credit, ResCredit),
            (Penalty, ResPenalty),
        ]
        exp_use = [(ExpUseSetUp, UseExp)]
        exp_opn = [
            (ExpOpr, OpExp),
            (ExpSetUp, CapExp),
            (ExpOprI, OpExpI),
            (ExpSetUpI, CapExpI),
        ]

        # Calculated Emissions
        emit = [
            (EmitBuy, BuyEmit),
            (EmitSell, SellEmit),
            (EmitUse, UseEmit),
            (EmitSetUp, SetUpEmit),
            (EmitLoss, LossEmit),
        ]

        # Bind Constraints

        for var, param in (
            trade_bnd + cap_bnd + op_bnd + exp_bnd + emission_bnd + ply_bnd + use_bnd
        ):

            self.add(
                Rule(
                    variable=var,
                    parameter=param,
                    constraint=Bind,
                )
            )

        # Exact Constraints

        for var, param in use_cmd + loss + exp_res + exp_use + exp_opn + emit:
            self.add(
                Rule(
                    variable=var,
                    parameter=param,
                    constraint=Calculate,
                )
            )

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

    def variables(self):
        """Fetch all the Variables in the RuleBook"""
        return sorted([rule.variable for rule in self.rules], key=lambda x: x.cname())

    def parents(self):
        """Fetch all the parent Variables in the RuleBook"""
        return sorted(
            [rule.variable.parent() for rule in self.rules if rule.variable.parent()],
            key=lambda x: x.cname(),
        )

    def parameters(self):
        """Fetch all the Parameters in the RuleBook"""
        return sorted(
            [rule.parameter for rule in self.rules if rule.parameter],
            key=lambda x: x.cname(),
        )
