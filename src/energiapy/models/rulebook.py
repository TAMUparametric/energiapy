from __future__ import annotations

from dataclasses import dataclass
from operator import is_
from typing import TYPE_CHECKING, List

from ..core.base import Dunders
from ..type.element.condition import Condition, RightHandSide, SumOver
from ..type.input.aspect import (CapBound, CashFlow, Emission, Land,  # Life,
                                 Limit, Loss)

if TYPE_CHECKING:
    from ...type.alias import IsAspect, IsComponent, IsDeclaredAt


@dataclass
class Rule(Dunders):
    condition: Condition
    variable: IsAspect
    associated: IsAspect = None
    balance: IsAspect = None
    parameter: IsAspect = None
    sumover: SumOver = None
    declared_at: IsComponent = None

    def __post_init__(self):

        self.rhs = []

        assoc, param = ('' for _ in range(2))
        var = f'{self.variable.name.lower()}'
        if self.associated:
            assoc = f'{self.associated.name.lower()}'
            self.rhs.append(RightHandSide.CONTINUOUS)
        if self.parameter:
            param = f'{self.parameter.name.lower().capitalize()}'
            self.rhs.append(RightHandSide.PARAMETER)

        if not any([self.associated, self.parameter]):
            raise ValueError(
                'Rule must have at least one of associated (variable) or parameter')

        self.name = f'{self.condition.name.lower()}|var:{var},var2:{assoc},parm:{param}'


@dataclass
class RuleBook(Dunders):
    rules: List[Rule] = None

    def __post_init__(self):
        self.rules = []
        self.name = 'RuleBook'

    def add(self, rule: Rule):
        self.rules.append(rule)

    def find(self, variable: IsAspect):

        return [rule for rule in self.rules if is_(rule.variable, variable)]


rulebook = RuleBook()


rulebook.add(Rule(variable=CashFlow.PURCHASE_COST, associated=Limit.CONSUME,
                  parameter=CashFlow.PURCHASE_COST, condition=Condition.CALCULATE))

rulebook.add(Rule(variable=CashFlow.STORE_COST, associated=CapBound.STORE,
                  parameter=CashFlow.STORE_COST, condition=Condition.CALCULATE))

for i in [CashFlow.SELL_COST, CashFlow.CREDIT, CashFlow.PENALTY]:
    rulebook.add(Rule(variable=i, associated=Limit.DISCHARGE,
                      parameter=i, condition=Condition.CALCULATE))

rulebook.add(Rule(variable=CashFlow.VOPEX, associated=CapBound.PRODUCE,
                  parameter=CashFlow.VOPEX, condition=Condition.CALCULATE))

rulebook.add(Rule(variable=CashFlow.CAPEX, associated=Limit.CAPACITY,
                  parameter=CashFlow.CAPEX, condition=Condition.CALCULATE))

rulebook.add(Rule(variable=CashFlow.FOPEX, associated=Limit.CAPACITY,
                  parameter=CashFlow.FOPEX, condition=Condition.CALCULATE))

rulebook.add(Rule(variable=CashFlow.INCIDENTAL, associated=None,
                  parameter=CashFlow.INCIDENTAL, condition=Condition.CALCULATE))


rulebook.add(Rule(variable=Loss.STORE_LOSS, associated=CapBound.STORE,
                  parameter=Loss.STORE_LOSS, condition=Condition.CALCULATE))
rulebook.add(Rule(variable=Loss.TRANSPORT_LOSS, associated=CapBound.TRANSPORT,
                  parameter=Loss.TRANSPORT_LOSS, condition=Condition.CALCULATE))

rulebook.add(Rule(variable=Land.LAND, associated=Land.LAND_USE,
                  condition=Condition.SUMOVER, sumover=SumOver.SPACE))
rulebook.add(Rule(variable=Land.LAND, parameter=Land.LAND,
                  condition=Condition.BIND))


rulebook.add(Rule(variable=CashFlow.LAND_COST, associated=Land.LAND,
                  parameter=CashFlow.LAND_COST, condition=Condition.CALCULATE))
rulebook.add(Rule(variable=Land.LAND_USE, associated=Limit.CAPACITY,
                  parameter=Land.LAND_USE, condition=Condition.CALCULATE))

for i in Limit.all():
    rulebook.add(Rule(variable=i, parameter=i, condition=Condition.BIND))


rulebook.add(Rule(variable=CapBound.PRODUCE, associated=Limit.CAPACITY,
                  condition=Condition.CAPACITATE, declared_at='Process'))

rulebook.add(Rule(variable=CapBound.STORE, associated=Limit.CAPACITY,
                  condition=Condition.CAPACITATE, declared_at='Storage'))

rulebook.add(Rule(variable=CapBound.TRANSPORT, associated=Limit.CAPACITY,
                  condition=Condition.CAPACITATE, declared_at='Transit'))


for i in Emission.all():
    rulebook.add(Rule(variable=i, associated=Limit.CONSUME,
                      parameter=i, condition=Condition.CALCULATE))
    rulebook.add(Rule(variable=i, associated=Limit.DISCHARGE,
                      parameter=i, condition=Condition.CALCULATE))
    rulebook.add(Rule(variable=i, associated=Limit.CAPACITY,
                      parameter=i, condition=Condition.CALCULATE))
