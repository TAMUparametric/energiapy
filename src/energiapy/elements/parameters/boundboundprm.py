"""Parameter that serves as a bound for a BoundBoundVar
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass
from sympy import IndexedBase
from ._parameter import _Parameter

if TYPE_CHECKING:
    from ..disposition.bound import VarBnd


@dataclass
class BoundBoundPrm(_Parameter):
    """Bounded Bound Parameter"""

    def __post_init__(self):
        setattr(self, 'varbnd', self.value.varbnd)
        _Parameter.__post_init__(self)

    @property
    def varbnd(self):
        """Variable Bound"""
        return self._varbnd

    @varbnd.setter
    def varbnd(self, varbnd: VarBnd):
        self._varbnd = varbnd

    @property
    def symib(self):
        """Symbolic representation of the Parameter"""
        return IndexedBase(f'{self.symbol}{self.varbnd.value}')
