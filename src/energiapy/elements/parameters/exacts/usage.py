"""Defined Use Parameters
"""

from dataclasses import dataclass

from sympy import IndexedBase

from .._parameter import _ExactPar


@dataclass
class Usage(_ExactPar):
    """Material or Land Usage"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Usage')
