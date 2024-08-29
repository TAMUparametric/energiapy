"""Constraint to Bind variable to a lower or upper Parameter or Variable (or both) Bound
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from sympy import Rel, Sum

from ._constraint import _Constraint

if TYPE_CHECKING:
    from ..core.aliases.is_element import IsParameter, IsVariable


@dataclass
class SumOver(_Constraint):
    """Bind variable to another variable or parameter"""

    def __post_init__(self):
        _Constraint.__post_init__(self)

    def sumtemporal_variable(self):
        """Create the equation for the constraint

        Args:
            var (IsVariable): The main Variable in the constraint
        """

        # Left Hand Side is always the main Variable
        lhs = self.variable.sym

        # Right Hand Side is at a lower temporal disposition
        rhs = Sum(self.variable.sym)

        # Set the equation property
        setattr(self, 'equation', Rel(lhs, rhs, '=='))
