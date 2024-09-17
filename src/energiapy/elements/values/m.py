"""For unbounded parameters
"""

from dataclasses import dataclass, field

from sympy import IndexedBase
from ...core._handy._dunders import _Reprs


@dataclass
class M(_Reprs):
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
        if self.big:
            self.name = 'M'
        else:
            self.name = 'm'

    @property
    def value(self):
        """Returns a str"""
        if self.big is True:
            return self.big
        else:
            return self.m

    @property
    def sym(self):
        """Symbol"""
        return IndexedBase(f'{self.name}')

    def __gt__(self, other):
        if isinstance(other, (int, float)):
            # BigM is always greater than any number
            return self.big
        if isinstance(other, M):
            if other.big is False:
                return self.big

    def __ge__(self, other):
        return self > other

    def __lt__(self, other):
        return not self > other

    def __le__(self, other):
        return not self > other

    def __eq__(self, other):

        if isinstance(other, (int, float)):
            return False

        if isinstance(other, M):
            if self.big == other.big:
                return True
            else:
                return False

    def __ne__(self, other):
        return not self == other
