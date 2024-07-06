from dataclasses import dataclass
from typing import Tuple, Union, List
from .type.condition import Condition, LeftHandSide, SumOver
from .type.disposition import SpatialDisp, TemporalDisp
from .type.aspect import Aspect, Limit, CashFlow, Land, Life, Loss
from .type.special import SpecialParameter
from .type.variability import Variability, Bound, Uncertain
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

        variable, associated, parameter, lb, ub = ('' for _ in range(5))

        if self.variable:
            variable = self.variable.name
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

        if self.condition == Condition.CALCULATE:
            constraint = f'{variable}={parameter}*{associated}'

        if self.condition == Condition.BIND:
            if self.bound == Bound.LOWER:
                constraint = f'{lb}<={variable}'
            if self.bound == Bound.UPPER:
                constraint = f'{variable}<={ub}'
            if self.bound == Bound.EXACT:
                constraint = f'{variable}={ub}'
            if self.bound == Bound.BOTH:
                constraint = f'{lb}<={variable}<={ub}'
            if self.bound == Bound.BIGM:
                constraint = f'{variable}<={ub}'

        self.name = constraint
        self.index = self.variable.index

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

        # comp, dec_at, pst, temp = ('' for _ in range(4))

        # if self.component:
        #     comp = f'{self.component.name}'

        # if isinstance(self.declared_at, tuple):
        #     dec_at = (f'{i.name},' for i in self.declared_at)

        # else:
        #     dec_at = f'{self.declared_at.name}'

        # pst = f'{self.aspect.name.lower()}'

        # if self.temporal:
        #     temp = f'{self.temporal.name.lower()}'

        # if comp == dec_at:
        #     index = f'({comp},{temp})'
        #     self.index = (comp, temp)
        # else:
        #     index = f'({comp},{dec_at},{temp})'
        #     self.index = (comp, dec_at, temp)

        # var2, dom = ('' for _ in range(2))

        # var = f'{pst}{index}'

        # if self.aspect in self.limits_capacity_bounds():
        #     if self.declared_at != self.component:
        #         # if limited by capacity at Process or Transport
        #         capacity_index = [i.temporal.name.lower(
        #         ) for i in self.declared_at.capacity.params if i.component == self.declared_at][0]
        #         nml = f'capacity({dec_at},{capacity_index})*'

        # if isinstance(self.aspect, CashFlow):
        #     var = var.replace('_cost', '_exp')
        #     var2 = self.variables_cash()[self.aspect.name]
        #     if var2 is not None:
        #         var2 = f'*{var2.lower()}{index}'
        #     else:
        #         var2 = ''

        # if isinstance(self.aspect, Land):
        #     var2 = self.variables_land()[self.aspect.name]
        #     var2 = f'*{var2.lower()}{index}'

        # if th:
        #     par = 'Th'
        #     dom = f', Th in ({self.lb},{self.ub})'
        #     bnd = ['', '<=']
        # else:
        #     bnd = [f'{self.lb}<=', f'<={nml}{self.ub}']
        #     par = f'{nml}{self.ub}'

        # if self.btype == Bound.EXACT:
        #     self.eqn = f'{var}={par}{var2}{dom}'
        # else:
        #     self.eqn = f'{bnd[0]}{var}{bnd[1]}{dom}'
