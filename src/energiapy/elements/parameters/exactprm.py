"""Helps calculate ExactVar
"""

from dataclasses import dataclass
from sympy import IndexedBase

from ._parameter import _Parameter


@dataclass
class ExactPrm(_Parameter):
    """Calculated Parameter"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @property
    def symib(self):
        """Symbolic representation of the Parameter"""
        return IndexedBase(self.symbol)
