from dataclasses import dataclass
from typing import Tuple, Union, List
from .type.condition import Condition, LeftHandSide, SumOver
from .type.disposition import SpatialDisp, TemporalDisp
from .type.aspect import Limit, CashFlow, Land, Life, Loss
from .type.special import SpecialParameter
from .type.variability import Variability, Uncertain
from .type.bound import Bound
from ..components.temporal_scale import TemporalScale
from .parameter import Parameter
from .variable import Variable
from .factor import Factor


@dataclass
class Constraint:
    condition: Condition
    variable: Variable = None
    associated: Variable = None
    parameter: Parameter = None
    balance: List[Variable] = None
    bound: Bound = None
    lb: Union[float, SpecialParameter, Factor] = None
    ub: Union[float, SpecialParameter, Factor] = None
    lhs: List[LeftHandSide] = None
    sumover: SumOver = None

    def __post_init__(self):

        variable, associated, parameter, lb, ub, multip, theta_bounds = ('' for _ in range(7))

        if self.variable:
            variable = self.variable.name
            for i in ['index', 'temporal', 'spatial', 'disposition']:
                setattr(self, i, getattr(self.variable, i))
                
        if self.associated:
            associated = self.associated.name
        if self.parameter:
            parameter = self.parameter.value
        if self.lb:
            if isinstance(self.lb, Factor):
                lb = self.lb.name
            else:
                lb = self.lb
        if self.ub:
            if isinstance(self.ub, Factor):
                ub = self.ub.name
            else:
                ub = self.ub
        if hasattr(self.parameter, 'theta_bounds'):
            theta_bounds = f', Th in {self.parameter.theta_bounds}'
            

        if all([self.lb, self.associated, self.ub]):
            multip = '*'
        
        if self.condition == Condition.CALCULATE:
            constraint = f'{variable}={parameter}*{associated}'

        if self.condition == Condition.BIND:
            if self.bound == Bound.LOWER:
                constraint = f'{lb}{multip}{associated}<={variable}'
            if self.bound == Bound.UPPER:
                constraint = f'{variable}<={ub}{multip}{associated}'
            if self.bound == Bound.EXACT:
                constraint = f'{variable}={ub}{multip}{associated}{theta_bounds}'
            if self.bound == Bound.BOTH:
                constraint = f'{lb}{multip}{associated}<={variable}<={ub}{multip}{associated}'

        self.name = constraint
        

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

