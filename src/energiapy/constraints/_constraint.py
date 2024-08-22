"""Program Constraints 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sympy import IndexedBase, Mul, Rel

from .._core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from .._core._aliases._is_element import IsParameter, IsVariable


@dataclass
class _Constraint(_Dunders):
    """Constraints for Program

    Attributes:
        variable (IsVariable): The main Variable in the constraint
        disposition (IsDisposition): The disposition of the constraint. Determined post initialization.
    """

    variable: IsVariable = field(default=None)

    def __post_init__(self):

        # The disposition of the constraint is the same as the main Variable
        self.disposition = self.variable.disposition
        self.name = str(self.sym)

    @property
    def equation(self):
        """The equation of the constraint"""
        return self._equation

    @equation.setter
    def equation(self, equation):
        self._equation = equation

    @classmethod
    def id(cls):
        """The id of the task"""
        return IndexedBase(cls.__name__)

    @property
    def sym(self):
        """Symbol"""
        return self.id()[self.disposition.sym]

    @staticmethod
    def collection():
        """What collection the element belongs to"""
        return 'constraints'

    def birth_equation(self, eq: str, par: IsParameter, prn: IsVariable):
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
            rhs = Mul(par.sym, prn.sym)

        else:
            # Or only one of the two
            if par:
                rhs = par.value.sym
            if prn:
                rhs = prn.sym

        # Set the equation property
        setattr(self, 'equation', Rel(lhs, rhs, eq))
