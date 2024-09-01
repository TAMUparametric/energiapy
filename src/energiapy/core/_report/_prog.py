"""Properties to report Program Modeling Block Elements
"""

from abc import ABC, abstractmethod


class _Elms(ABC):
    """Program Elements"""

    @property
    @abstractmethod
    def program(self):
        """Program"""

    @property
    def constraints(self):
        """All Constraints in the Program"""
        return self.program.constraints

    @property
    def variables(self):
        """All Variables in the Program"""
        return self.program.variables

    @property
    def parameters(self):
        """All Parameters in the Program"""
        return self.program.parameters

    @property
    def indices(self):
        """All Indexs in the Program"""
        return self.program.indices
