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

    def __post_init__(self):
        self.index = self.value.index
        self.name = str(self.sym)

    @property
    @abstractmethod
    def id(self) -> str:
        """Symbolic representation of the Parameter"""

    @property
    def sym(self):
        """Symbol"""
        return self.id[self.index.sym]


# These parameters are exact values for ExactVars


@dataclass
class _ExactPar(_Parameter):
    """Calculated Parameter"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


# These parameters serve as bounds for BoundVars


class _BoundPar(_Parameter):
    """Bounded Parameter"""

    def __post_init__(self):
        setattr(self, 'varbnd', self.value.varbnd)
        _Parameter.__post_init__(self)

    @property
    def varbnd(self):
        """Variable Bound"""
        return self._varbnd

    @varbnd.setter
    def varbnd(self, varbnd):
        self._varbnd = varbnd
