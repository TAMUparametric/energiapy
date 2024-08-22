"""Defined Calculative Parameters 
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ._parameter import _Parameter


@dataclass
class MatUse(_Parameter):
    """Material Use"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @staticmethod
    def id() -> str:
        """Symbol"""
        return IndexedBase('Mat')


@dataclass
class LndUse(_Parameter):
    """Land Use"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @staticmethod
    def id() -> str:
        """Symbol"""
        return IndexedBase('Land')


@dataclass
class ResLoss(_Parameter):
    """Resource Loss"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @staticmethod
    def id() -> str:
        """Symbol"""
        return IndexedBase('Loss')
