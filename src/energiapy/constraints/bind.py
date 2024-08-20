"""Constraint to Bind variable to a lower or upper Parameter or Variable (or both) Bound
"""

from ._constraint import _Constraint

from __future__ import annotations

from dataclasses import dataclass, field
from operator import is_
from typing import TYPE_CHECKING, List

from ..parameters.bounds import VarBnd

if TYPE_CHECKING:
    from .._core._aliases._is_element import IsParameter, IsVariable


@dataclass
class Bind(_Constraint):
    """Bind variable to another variable or parameter"""

    variable: IsVariable = field(default=None)
    varbnd: VarBnd = field(default=None)
    parent: IsVariable = field(default=None)
    parameter: IsParameter = field(default=None)
    balance: List[IsVariable] = field(default=None)

    def __post_init__(self):
        _Constraint.__post_init__(self)

        # A multiplication sign is needed if both parent and parameter are needed
        if self.parameter and self.parent:
            self.multiply = True
        else:
            self.multiply = False

        if is_(self.varbnd, VarBnd.LOWER):
            self.equality = 'geq'
            nm_vb = 'LB'
        if self.varbnd in [VarBnd.UPPER, VarBnd.FREE]:
            self.equality = 'leq'
            nm_vb = 'UB'
        if is_(self.varbnd, VarBnd.EXACT):
            self.equality = 'eq'
            nm_vb = ''

        # The disposition of the constraint is the same as the main Variable
        self.disposition = self.variable.disposition
        self.name = f'{self.id()}{nm_vb}[{self.variable}]'
        # The equation for any Defined Component or the Scenario can be printed using .eqns()
        self.equation = f'{self.variable}{self.pr_sign}{self.pr_parameter}{self.pr_multiply}{self.pr_parent}'

    @property
    def pr_parent(self):
        """for printing"""
        if self.parent:
            return self.parent
        else:
            return ''

    @property
    def pr_parameter(self):
        """for printing"""
        if self.parameter:
            return self.parameter
        else:
            return ''

    @property
    def pr_multiply(self):
        """Mutliplication sign"""
        if self.multiply:
            return '*'
        else:
            return ''

    @property
    def pr_sign(self):
        """Returns type of equality"""

        if is_(self.equality, 'geq'):
            return '>='
        if is_(self.equality, 'leq'):
            return '<='
        if is_(self.equality, 'eq'):
            return '=='
