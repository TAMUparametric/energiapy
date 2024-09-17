"""Parameter that serves as a bound for a BoundVar
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sympy import IndexedBase

from ._parameter import _Parameter

if TYPE_CHECKING:
    from ..disposition.bound import VarBnd


@dataclass
class BoundPrm(_Parameter):
    """Bounded Parameter"""

    def __post_init__(self):
        self.varbnd = self.value.varbnd
        _Parameter.__post_init__(self)

    @property
    def varbnd(self):
        """Variable Bound"""
        return self._varbnd

    @varbnd.setter
    def varbnd(self, varbnd: VarBnd):
        self._varbnd = varbnd

    @property
    def symib(self) -> IndexedBase:
        """Symbolic representation of the Parameter"""
        return IndexedBase(f'{self.symbol}{self.varbnd.value}')
