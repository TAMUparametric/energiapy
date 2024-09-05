"""Program Constraints 
"""

from dataclasses import dataclass, field

from sympy import IndexedBase, Mul, Rel
from ..disposition.bound import VarBnd

from ...core._handy._dunders import _Dunders
from ...core.isalias.elms.isprm import IsPrm
from ...core.isalias.elms.isvar import IsVar


@dataclass
class _Constraint(_Dunders):
    """Constraints for Program
    Attributes:
        variable (IsVariable): The main Variable in the constraint
    """

    variable: IsVar = field(default=None)
    varbnd: VarBnd = field(default=None)
    parent: IsVar = field(default=None)
    parameter: IsPrm = field(default=None)

    def __post_init__(self):
        # The index of the constraint is the same as the main Variable
        self.index = self.variable.index
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
        return IndexedBase(cls.cname())

    @property
    def sym(self):
        """Symbol"""
        return self.id()[self.index.sym]

    def birth_equation(self, eq: str, par: IsPrm, prn: IsVar):
        """Create the equation for the constraint
        Args:
            eq (str): The equality sign. '==', '<=', '>='
            par (IsPrm): The parameter in the constraint
            mlt (str): The multiplication sign
            prn (IsVar): The parent Variable in the constraint
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
