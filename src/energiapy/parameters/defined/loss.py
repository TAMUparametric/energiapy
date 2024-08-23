"""Defined Loss Parameter
"""
from dataclasses import dataclass

from sympy import IndexedBase

from ._parameter import _Parameter


@dataclass
class ResLoss(_Parameter):
    """Resource Loss"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Loss')
