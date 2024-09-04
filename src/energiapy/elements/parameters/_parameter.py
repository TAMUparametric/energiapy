"""Defined Parameters 
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ...core._handy._dunders import _Dunders
from ...core.isalias.elms.isval import IsVal


@dataclass
class _Parameter(_Dunders, ABC):
    """Model Parameter

    Attributes:
        value (IsValue): The value of the parameter. Can be Constant, M, Theta, DataSet
    """

    value: IsVal = field(default=None)
    symbol: str = field(default=None)

    def __post_init__(self):
        self.index = self.value.index
        self.name = str(self.sym)

    @property
    @abstractmethod
    def id(self) -> str:
        """Symbolic representation of the Parameter"""

    @property
    @abstractmethod
    def symib(self):
        """Symbolic representation of the Parameter"""

    @property
    def sym(self):
        """Symbol"""
        return self.symib[self.index.sym]


# These parameters are exact values for ExactVars



# These parameters serve as bounds for BoundVars
