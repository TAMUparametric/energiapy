from .aspect import Limit, CashFlow, Land, Life, Loss, Emission
from .condition import Condition, LeftHandSide, SumOver
from dataclasses import dataclass
from ..parameter import Parameter
from typing import Union, List


@dataclass
class Match:
    condition: Condition
    variable: Union[Limit, CashFlow, Land, Life, Loss] = None
    associated: Union[Limit, CashFlow, Land, Life, Loss] = None
    balance: List[Union[Limit, CashFlow, Land, Life, Loss]] = None
    parameter: Union[Limit, CashFlow, Land, Life, Loss] = None
    sumover: SumOver = None

    def __post_init__(self):

        self.lhs = list()

        var, assoc, param = ('' for _ in range(3))
        if self.variable:
            var = f'{self.variable.name.lower()}'
        if self.associated:
            assoc = f'{self.associated.name.lower()}'
            self.lhs.append(LeftHandSide.CONTINUOUS)
        if self.parameter:
            param = f'{self.parameter.name.lower()}'
            self.lhs.append(LeftHandSide.PARAMETER)

        self.name = f'{self.condition.name}|var_x:{var},var_y:{assoc},parm:{param}'.lower()

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


@dataclass
class Matches:
    matches: List[Match] = None

    def __post_init__(self):
        self.matches = list()
        self.name = 'Matches'

    def add(self, match: Match):
        self.matches.append(match)

    def find(self, variable: Union[Limit, CashFlow, Land, Life, Loss]):

        return [match for match in self.matches if match.variable == variable]

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


matches = Matches()

matches.add(Match(variable=CashFlow.SELL_COST, associated=Limit.DISCHARGE,
                  parameter=CashFlow.SELL_COST, condition=Condition.CALCULATE))
matches.add(Match(variable=CashFlow.PURCHASE_COST, associated=Limit.CONSUME,
                  parameter=CashFlow.PURCHASE_COST, condition=Condition.CALCULATE))
matches.add(Match(variable=CashFlow.STORE_COST, associated=Limit.STORE,
                  parameter=CashFlow.STORE_COST, condition=Condition.CALCULATE))
matches.add(Match(variable=CashFlow.CREDIT, associated=Limit.DISCHARGE,
                  parameter=CashFlow.CREDIT, condition=Condition.CALCULATE))
matches.add(Match(variable=CashFlow.PENALTY, associated=Limit.DISCHARGE,
                  parameter=CashFlow.PENALTY, condition=Condition.CALCULATE))
matches.add(Match(variable=CashFlow.VOPEX, associated=Limit.DISCHARGE,
                  parameter=CashFlow.VOPEX, condition=Condition.CALCULATE))
matches.add(Match(variable=CashFlow.CAPEX, associated=Limit.CAPACITY,
                  parameter=CashFlow.CAPEX, condition=Condition.CALCULATE))
matches.add(Match(variable=CashFlow.FOPEX, associated=Limit.CAPACITY,
                  parameter=CashFlow.FOPEX, condition=Condition.CALCULATE))
matches.add(Match(variable=CashFlow.INCIDENTAL, associated=None,
                  parameter=CashFlow.INCIDENTAL, condition=Condition.CALCULATE))

matches.add(Match(variable=Loss.STORE_LOSS, associated=Limit.STORE,
                  parameter=Loss.STORE_LOSS, condition=Condition.CALCULATE))
matches.add(Match(variable=Loss.TRANSPORT_LOSS, associated=Limit.TRANSPORT,
                  parameter=Loss.TRANSPORT_LOSS, condition=Condition.CALCULATE))

matches.add(Match(variable=Land.LAND, associated=Land.LAND_USE,
                  condition=Condition.SUMOVER, sumover=SumOver.SPACE))
matches.add(Match(variable=Land.LAND, parameter=Land.LAND,
                  condition=Condition.BIND))
matches.add(Match(variable=CashFlow.LAND_COST, associated=Land.LAND,
                  parameter=CashFlow.LAND_COST, condition=Condition.CALCULATE))
matches.add(Match(variable=Land.LAND_USE, associated=Limit.CAPACITY,
                  parameter=Land.LAND_USE, condition=Condition.CALCULATE))

matches.add(Match(variable=Limit.CONSUME, parameter=Limit.CONSUME,
                  condition=Condition.BIND))
matches.add(Match(variable=Limit.DISCHARGE, parameter=Limit.DISCHARGE,
                  condition=Condition.BIND))
matches.add(Match(variable=Limit.STORE, parameter=Limit.STORE,
                  condition=Condition.BIND))
matches.add(Match(variable=Limit.DISCHARGE, associated=Limit.CAPACITY,
                  condition=Condition.BIND))
matches.add(Match(variable=Limit.TRANSPORT, parameter=Limit.CAPACITY,
                  condition=Condition.BIND))
matches.add(Match(variable=Limit.CAPACITY, parameter=Limit.CAPACITY,
                  condition=Condition.BIND))

for i in Emission.all():
    matches.add(Match(variable=i, associated=Limit.CONSUME,
                      parameter=i, condition=Condition.CALCULATE))
    matches.add(Match(variable=i, associated=Limit.DISCHARGE,
                      parameter=i, condition=Condition.CALCULATE))
    matches.add(Match(variable=i, associated=Limit.TRANSPORT,
                      parameter=i, condition=Condition.CALCULATE))
    matches.add(Match(variable=i, associated=Limit.CAPACITY,
                      parameter=i, condition=Condition.CALCULATE))
