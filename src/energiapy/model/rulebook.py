from dataclasses import dataclass
from typing import List, Union

from .type.aspect import CashFlow, Emission, Land, Life, Limit, Loss, Capacity
from .type.condition import Condition, RightHandSide, SumOver


@dataclass
class Rule:
    condition: Condition
    variable: Union[Limit, CashFlow, Land, Life, Loss]
    associated: Union[Limit, CashFlow, Land, Life, Loss] = None
    balance: List[Union[Limit, CashFlow, Land, Life, Loss]] = None
    parameter: Union[Limit, CashFlow, Land, Life, Loss] = None
    sumover: SumOver = None
    declared_at: Union['Process', 'Location', 'Transport', 'Linkage'] = None

    def __post_init__(self):

        self.rhs = list()

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

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


@dataclass
class RuleBook:
    rules: List[Rule] = None

    def __post_init__(self):
        self.rules = list()
        self.name = 'RuleBook'

    def add(self, rule: Rule):
        self.rules.append(rule)

    def find(self, variable: Union[Limit, CashFlow, Land, Life, Loss]):

        return [rule for rule in self.rules if rule.variable == variable]

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


rulebook = RuleBook()


rulebook.add(Rule(variable=CashFlow.PURCHASE_COST, associated=Limit.CONSUME,
                  parameter=CashFlow.PURCHASE_COST, condition=Condition.CALCULATE))

rulebook.add(Rule(variable=CashFlow.STORE_COST, associated=Capacity.STORE,
                  parameter=CashFlow.STORE_COST, condition=Condition.CALCULATE))

for i in [CashFlow.SELL_COST, CashFlow.CREDIT, CashFlow.PENALTY]:
    rulebook.add(Rule(variable=i, associated=Limit.DISCHARGE,
                      parameter=i, condition=Condition.CALCULATE))

rulebook.add(Rule(variable=CashFlow.VOPEX, associated=Capacity.PRODUCE,
                  parameter=CashFlow.VOPEX, condition=Condition.CALCULATE))

rulebook.add(Rule(variable=CashFlow.CAPEX, associated=Limit.CAPACITY,
                  parameter=CashFlow.CAPEX, condition=Condition.CALCULATE))

rulebook.add(Rule(variable=CashFlow.FOPEX, associated=Limit.CAPACITY,
                  parameter=CashFlow.FOPEX, condition=Condition.CALCULATE))

rulebook.add(Rule(variable=CashFlow.INCIDENTAL, associated=None,
                  parameter=CashFlow.INCIDENTAL, condition=Condition.CALCULATE))


rulebook.add(Rule(variable=Loss.STORE_LOSS, associated=Capacity.STORE,
                  parameter=Loss.STORE_LOSS, condition=Condition.CALCULATE))
rulebook.add(Rule(variable=Loss.TRANSPORT_LOSS, associated=Capacity.TRANSPORT,
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



rulebook.add(Rule(variable=Capacity.STORE, associated=Limit.CAPACITY,
                  condition=Condition.CAPACITATE, declared_at='Process'))

rulebook.add(Rule(variable=Capacity.PRODUCE, associated=Limit.CAPACITY,
                  condition=Condition.CAPACITATE, declared_at='Process'))

rulebook.add(Rule(variable=Capacity.TRANSPORT, associated=Limit.CAPACITY,
                  condition=Condition.CAPACITATE, declared_at='Transport'))


for i in Emission.all():
    rulebook.add(Rule(variable=i, associated=Limit.CONSUME,
                      parameter=i, condition=Condition.CALCULATE))
    rulebook.add(Rule(variable=i, associated=Limit.DISCHARGE,
                      parameter=i, condition=Condition.CALCULATE))
    rulebook.add(Rule(variable=i, associated=Limit.CAPACITY,
                      parameter=i, condition=Condition.CALCULATE))
