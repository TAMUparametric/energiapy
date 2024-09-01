"""Functions for printing 
"""

from abc import ABC, abstractmethod

from IPython.display import Math, display
from sympy import latex


class _Print(ABC):
    """
    Printing functions for:
        - Component
        - Model Block
        - Scenario
    """

    @abstractmethod
    def eqns(self):
        """Yields all equations"""

    def pprint(self):
        """Pretty prints the component"""
        for eq in self.eqns():
            display(Math(latex(eq, mul_symbol='dot')))

    def latex(self):
        """Returns the latex"""
        for eq in self.eqns():
            display(latex(eq, mul_symbol='dot'))


class _EasyPrint(_Print):
    """Printing functions with a straightforward setup

    Basically the object has an attribute called constraints
    and you want to print the equations in these constraints
    """

    def eqns(self):
        """Prints all equations in Constraints"""
        for constraint in getattr(self, 'constraints'):
            yield constraint.equation
