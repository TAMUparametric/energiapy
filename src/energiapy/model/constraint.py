from dataclasses import dataclass
from typing import List

from .parameter import Parameter
from .type.bound import Bound
from .type.condition import Condition, RightHandSide, SumOver
from .variable import Variable


@dataclass
class Constraint:
    condition: Condition
    variable: Variable
    rhs: List[RightHandSide]
    associated: Variable = None
    parameter: Parameter = None
    balance: List[Variable] = None
    bound: Bound = None
    sumover: SumOver = None

    def __post_init__(self):

        associated, parameter, multip, theta_bounds = (
            '' for _ in range(4))

        variable = self.variable.name
        for i in ['index', 'temporal']:
            setattr(self, i, getattr(self.variable, i))

        if self.associated:
            associated = self.associated.name

        if self.parameter:
            parameter = self.parameter.value

        if all([self.associated, self.parameter]):
            multip = '*'

        if hasattr(self.parameter, 'theta_bounds'):
            theta_bounds = f', Th in {list(self.parameter.theta_bounds)}'

        if self.condition == Condition.CALCULATE:
            constraint = f'{variable}={parameter}{multip}{associated}{theta_bounds}'

        if self.condition == Condition.BIND:
            if self.bound == Bound.LOWER:
                constraint = f'{variable}>={parameter}{multip}{associated}'
            if self.bound in [Bound.UPPER, Bound.UNBOUNDED]:
                constraint = f'{variable}<={parameter}{multip}{associated}'
            if self.bound == Bound.EXACT:
                constraint = f'{variable}={parameter}{multip}{associated}'
            if self.bound == Bound.PARAMETRIC:
                constraint = f'{variable}={parameter}{multip}{associated}{theta_bounds}'

        if self.condition == Condition.CAPACITATE:
            constraint = f'{variable}<={parameter}{multip}{associated}'

        self.name = constraint

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
