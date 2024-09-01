"""Bhaskara for Constraint generation
"""

from dataclasses import dataclass, field
from operator import is_

from ...core._handy._dunders import _Dunders
from ...core.isalias.elms.iscns import IsCns
from ...core.isalias.elms.isprm import IsPrm
from ...core.isalias.elms.isvar import IsVar
from ...core.nirop.errors import CacodcarError
from ...elements.constraints.bind import Bind
from ...elements.constraints.calculate import Calculate
from ...elements.parameters.bounds.all import (BuyBound, CapBound, EmnBound,
                                               ErnBound, Has, Needs, OprBound,
                                               ShpBound, SllBound, SpdBound,
                                               UseBound)
from ...elements.parameters.exacts.emission import (BuyEmission, LseEmission,
                                                    SllEmission, StpEmission,
                                                    UseEmission)
from ...elements.parameters.exacts.expense import (BuyPrice, OprExpense,
                                                   OprExpenseI, SllCredit,
                                                   SllPenalty, SllPrice,
                                                   StpExpense, StpExpenseI,
                                                   UseCost)
from ...elements.parameters.exacts.loss import Loss
from ...elements.parameters.exacts.usage import Usage
from ...elements.variables.act import Give, Take
from ...elements.variables.emit import (Emit, EmitBuy, EmitLse, EmitSll,
                                        EmitStp, EmitUse)
from ...elements.variables.lose import Lose
from ...elements.variables.operate import Operate
from ...elements.variables.setup import Capacitate
from ...elements.variables.trade import Buy, Sell, Ship
from ...elements.variables.transact import (Earn, Spend, TransactBuy,
                                            TransactCrd, TransactOpr,
                                            TransactOprI, TransactPnt,
                                            TransactSll, TransactStp,
                                            TransactStpI, TransactUse)
from ...elements.variables.use import Use, UseStp


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

    constraint: IsCns = field(default=None)
    variable: IsVar = field(default=None)
    parameter: IsPrm = field(default=None)
    balance: dict[IsVar, int] = field(default=None)

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
class Bhaskara(_Dunders):
    """Bhaskara is rulebook for constraint generation

    Attributes:
        name (str): name of the Bhaskara, borrows from Scenario
    """

    name: str = field(default=None)

    def __post_init__(self):
        self.rules = []
        self.name = f'RuleBook|{self.name}|'
        # Bounded
        trade_bnd = [(Buy, BuyBound), (Sell, SllBound), (Ship, ShpBound)]
        cap_bnd = [(Capacitate, CapBound)]
        op_bnd = [(Operate, OprBound)]
        exp_bnd = [(Spend, SpdBound), (Earn, ErnBound)]
        emission_bnd = [(Emit, EmnBound)]
        ply_bnd = [(Give, Has), (Take, Needs)]
        use_bnd = [(Use, UseBound)]

        # Calculated
        use_cmd = [(UseStp, Usage)]
        loss = [(Lose, Loss)]

        # Calculated Transacts
        exp_res = [
            (TransactBuy, BuyPrice),
            (TransactSll, SllPrice),
            (TransactCrd, SllCredit),
            (TransactPnt, SllPenalty),
        ]
        exp_use = [(TransactUse, UseCost)]
        exp_opn = [
            (TransactOpr, OprExpense),
            (TransactStp, StpExpense),
            (TransactOprI, OprExpenseI),
            (TransactStpI, StpExpenseI),
        ]

        # Calculated Emissions
        emit = [
            (EmitBuy, BuyEmission),
            (EmitSll, SllEmission),
            (EmitUse, UseEmission),
            (EmitStp, StpEmission),
            (EmitLse, LseEmission),
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
        """Add Rule to Bhaskara"""
        self.rules.append(rule)

    def find(self, variable: IsVar):
        """Fetch the rules that apply for a particular variable"""
        rule = [rule for rule in self.rules if is_(rule.variable, variable)]
        if rule:
            return rule
        else:
            raise CacodcarError(f'No Rule found for {variable.id()}')

    def vars(self):
        """Fetch all the Variables in the Bhaskara"""
        return sorted([rule.variable for rule in self.rules], key=lambda x: x.cname())

    def prn_vars(self):
        """Fetch all the parent Variables in the Bhaskara"""
        return sorted(
            [rule.variable.parent() for rule in self.rules if rule.variable.parent()],
            key=lambda x: x.cname(),
        )

    def prms(self):
        """Fetch all the Parameters in the Bhaskara"""
        return sorted(
            [rule.parameter for rule in self.rules if rule.parameter],
            key=lambda x: x.cname(),
        )
