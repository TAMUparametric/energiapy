"""Program Constraints 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from operator import is_
from typing import TYPE_CHECKING, List

from .._core._handy._dunders import _Dunders
from ..parameters.bounds import VarBnd
from .rules import Condition, RightHandSide, SumOver

if TYPE_CHECKING:
    from .._core._aliases._is_element import IsParameter, IsVariable


@dataclass
class Constraint(_Dunders):
    condition: Condition = field(default=None)
    variable: IsVariable = field(default=None)
    parent: IsVariable = field(default=None)
    disposition: IsParameter = field(default=None)
    rhs: List[RightHandSide] = field(default=None)
    parameter: IsParameter = field(default=None)
    balance: List[IsVariable] = field(default=None)
    bound: VarBnd = field(default=None)
    sumover: SumOver = None

    def __post_init__(self):

        parent, parameter, multip, theta_bounds = ('' for _ in range(4))

        variable = self.variable.name
        for i in ['index', 'temporal']:
            setattr(self, i, getattr(self.variable, i))

        if self.parent:
            parent = self.parent.name

        if self.parameter:
            parameter = self.parameter.value

        if all([self.parent, self.parameter]):
            multip = '*'

        if hasattr(self.parameter, 'theta_bounds'):
            theta_bounds = f', Th in {list(self.parameter.theta_bounds)}'

        if is_(self.condition, Condition.CALCULATE):
            constraint = f'{variable}={parameter}{multip}{parent}{theta_bounds}'

        if is_(self.condition, Condition.BIND):
            if is_(self.bound, VarBnd.LOWER):
                constraint = f'{variable}>={parameter}{multip}{parent}'
            if is_(self.bound in [VarBnd.UPPER, VarBnd.UNBOUNDED]):
                constraint = f'{variable}<={parameter}{multip}{parent}'
            if is_(self.bound, VarBnd.EXACT):
                constraint = f'{variable}={parameter}{multip}{parent}'
            if is_(self.bound, VarBnd.PARAMETRIC):
                constraint = f'{variable}={parameter}{multip}{parent}{theta_bounds}'

        if is_(self.condition, Condition.CAPACITATE):
            constraint = f'{variable}<={parameter}{multip}{parent}'

        self.name = constraint
