"""Constraint to Bind variable to a lower or upper Parameter or Variable (or both) Bound
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sympy import Mul, Rel

from ..indices.enums import VarBnd
from ._constraint import _Constraint

if TYPE_CHECKING:
    from ..core.aliases.is_element import IsParameter, IsVariable


@dataclass
class Bind(_Constraint):
    """Bind variable to another variable or parameter"""

    varbnd: VarBnd = field(default=None)
    parent: IsVariable = field(default=None)
    parameter: IsParameter = field(default=None)

    def __post_init__(self):
        _Constraint.__post_init__(self)

        # Check the bound and add to name and make equality sign
        if self.varbnd == VarBnd.LB:
            eq = '>='
        if self.varbnd == VarBnd.UB:
            eq = '<='
        if self.varbnd == VarBnd.EQ:
            eq = '=='

        # Update the name of the constraint if it is a bound
        self.name = f'{self.name}{self.varbnd.value}'

        # Create the equation for the constraint
        self.bind_variable(eq=eq, par=self.parameter, prn=self.parent)

    def bind_variable(self, eq: str, par: IsParameter, prn: IsVariable):
        """Create the equation for the constraint

        Args:
            var (IsVariable): The main Variable in the constraint
            eq (str): The equality sign. '==', '<=', '>='
            par (IsParameter): The parameter in the constraint
            mlt (str): The multiplication sign
            prn (IsVariable): The parent Variable in the constraint
        """

        # Left Hand Side is always the main Variable
        lhs = self.variable.sym

        # Right Hand Side can have both the parameter and the parent Variable
        if all([par, prn]):
            rhs = Mul(prn.sym, par.value.sym)

        else:
            # Or only one of the two
            if par:
                rhs = par.value.sym
            if prn:
                rhs = prn.sym

        # Set the equation property
        setattr(self, 'equation', Rel(lhs, rhs, eq))
