from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from ..funcs.general import Dunders, Magics
from .parameter import Parameter
from .type.bound import Bound
from .type.condition import Condition, RightHandSide, SumOver
from .variable import Variable

if TYPE_CHECKING:
    from .type.alias import IsComponent


@dataclass
class Constraint(Dunders, Magics):
    condition: Condition
    variable: Variable
    rhs: List[RightHandSide]
    declared_at: IsComponent
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
