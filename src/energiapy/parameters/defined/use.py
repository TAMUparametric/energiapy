"""Defined Use Parameters
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ._parameter import _ExactPar


@dataclass
class MatUse(_ExactPar):
    """Material Use"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Mat')


@dataclass
class LndUse(_ExactPar):
    """Land Use"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Land')
