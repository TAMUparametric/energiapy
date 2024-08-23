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
