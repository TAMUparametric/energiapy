"""Constraint to calculate Variable. There is usually a parent Variable associated"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from sympy import IndexedBase, Mul, Rel

from ._constraint import _Constraint

if TYPE_CHECKING:
    from ..core.aliases.is_element import IsParameter, IsVariable


@dataclass
class Calculate(_Constraint):
    """Calculates; expenses, emissions, etc."""

    parent: IsVariable = field(default=None)
    parameter: IsParameter = field(default=None)

    def __post_init__(self):
        _Constraint.__post_init__(self)

        # calculations always have an equality sign
        self.calculate_variable(par=self.parameter, prn=self.parent)

    def calculate_variable(self, par: IsParameter, prn: IsVariable):
        """Create the equation for the constraint

        Args:
            var (IsVariable): The main Variable in the constraint
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
        setattr(self, 'equation', Rel(lhs, rhs, '=='))
