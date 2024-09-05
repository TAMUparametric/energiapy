"""Parameter that serves as a bound for a BoundVar
"""

from dataclasses import dataclass
from sympy import IndexedBase
from ._parameter import _Parameter


@dataclass
class BoundPrm(_Parameter):
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

    @property
    def symib(self):
        """Symbolic representation of the Parameter"""
        return IndexedBase(f'{self.symbol}{self.varbnd.value}')
