"""For unbounded parameters
"""

from dataclasses import dataclass, field

from sympy import IndexedBase

from ...disposition.bounds import VarBnd
from ..approach import Certainty
from ._value import _Value
from .constant import Constant


@dataclass
class M(_Value):
    """
    If big is True:
        A really big number like the weight on my shoulders
    If big is False:
        really small number like the money in my bank account

    Attributes:
        big (bool): True if big, False if small
        m (float): small m value

    The magic methods allow sorting
    """

    big: bool = field(default=True)
    m: float = field(default=None)

    def __post_init__(self):
        _Value.__post_init__(self)

        self._certainty, self._approach = Certainty.CERTAIN, None

        if self.big is True:
            # if Big M
            self.varbnd = VarBnd.UB
        else:
            # if small m
            self.varbnd = VarBnd.LB

    @property
    def value(self):
        """Returns a str"""
        if self.big is True:
            return self.big
        else:
            return self.m

    @property
    def id(self):
        """Symbol"""
        if self.big is True:
            return IndexedBase('M')
        else:
            return IndexedBase('m')

    def __gt__(self, other):
        if isinstance(other, (int, float, Constant)):
            # BigM is always greater than any number
            return getattr(self, 'big')
        if isinstance(other, M):
            if other.big is False:
                return getattr(self, 'big')
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (int, float, Constant)):
            # BigM is always big than any number
            return not getattr(self, 'big')
        if isinstance(other, M):
            if other.big is False:
                return not getattr(self, 'big')
        return NotImplemented
