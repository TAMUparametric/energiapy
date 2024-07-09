from dataclasses import dataclass
from typing import Tuple, Union, List
from .type.condition import Condition, LeftHandSide, SumOver
from .type.disposition import SpatialDisp, TemporalDisp
from .type.aspect import Limit, CashFlow, Land, Life, Loss
from .type.special import SpecialParameter
from .type.variability import Certainty, Approach
from .type.bound import Bound
from ..components.temporal_scale import TemporalScale
from .parameter import Parameter
from .variable import Variable
from .data import Data


@dataclass
class Constraint:
    condition: Condition
    variable: Variable = None
    associated: Variable = None
    parameter: Parameter = None
    balance: List[Variable] = None
    bound: Bound = None
    lb: Union[float, SpecialParameter, Data] = None
    ub: Union[float, SpecialParameter, Data] = None
    lhs: List[LeftHandSide] = None
    sumover: SumOver = None

    def __post_init__(self):

        variable, associated, parameter, multip, theta_bounds = (
            '' for _ in range(5))

        if self.variable:
            variable = self.variable.name
            for i in ['index', 'temporal', 'spatial', 'disposition']:
                setattr(self, i, getattr(self.variable, i))

        if self.associated:
            associated = self.associated.name
            
        if self.parameter:
            parameter = self.parameter.value

        if all([self.associated, self.parameter]):
            multip = '*'
        
        if hasattr(self.parameter, 'theta_bounds'):
            theta_bounds = f', Th in {self.parameter.theta_bounds}'

        if self.condition == Condition.CALCULATE:
            constraint = f'{variable}={parameter}{multip}{associated}'

        if self.condition == Condition.BIND:
            if self.bound == Bound.LOWER:
                constraint = f'{parameter}{multip}{associated}<={variable}'
            if self.bound in [Bound.UPPER, Bound.UNBOUNDED]:
                constraint = f'{variable}<={parameter}{multip}{associated}'
            if self.bound == Bound.EXACT:
                constraint = f'{variable}={parameter}{multip}{associated}'
            if self.bound == Bound.PARAMETRIC:
                constraint = f'{variable}={parameter}{multip}{associated}{theta_bounds}'

        self.name = constraint

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
