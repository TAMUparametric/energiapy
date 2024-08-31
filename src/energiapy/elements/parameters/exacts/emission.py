"""Defined Emission Parameters 
"""

from dataclasses import dataclass

from sympy import IndexedBase

from .._parameter import _ExactPar


@dataclass
class BuyEmission(_ExactPar):
    """Resource Emission Buy"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Emit^buy')


@dataclass
class SllEmission(_ExactPar):
    """Resource Emission Sell"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Emit^sell')


@dataclass
class LseEmission(_ExactPar):
    """Resource Emission Loss"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Emit^loss')


@dataclass
class UseEmission(_ExactPar):
    """Commodity Emission Use"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Emit^use')


@dataclass
class StpEmission(_ExactPar):
    """Emission due to setting up operation"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Emit^setup')
