"""Defined Parameters for Player actions
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ._parameter import _Parameter


@dataclass
class Has(_Parameter):
    """What Commodoties a Player Has"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @staticmethod
    def id() -> str:
        """Symbol"""
        return IndexedBase('Has')


@dataclass
class Needs(_Parameter):
    """What Commodities a Player Needs"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @staticmethod
    def id() -> str:
        """Symbol"""
        return IndexedBase('Needs')
