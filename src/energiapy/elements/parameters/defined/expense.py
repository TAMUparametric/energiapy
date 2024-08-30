"""Defined Expense Parameters 
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ._parameter import _ExactPar


@dataclass
class BuyPrice(_ExactPar):
    """Resource Buy Price"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Price^buy')


@dataclass
class SellPrice(_ExactPar):
    """Resource Sell Price"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Price^sell')


@dataclass
class ResPenalty(_ExactPar):
    """Resource Penalty Price"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Penalty')


@dataclass
class ResCredit(_ExactPar):
    """Resource Buy Price"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Credit')


@dataclass
class UseExp(_ExactPar):
    """Resource Use Expense"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Cost^use')


@dataclass
class CapExp(_ExactPar):
    """Operation Capital Expense"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Capex')


@dataclass
class OpExp(_ExactPar):
    """Operational Expense"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Opex')


@dataclass
class CapExpI(_ExactPar):
    """Incidental Capital Expense"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Capex^i')


@dataclass
class OpExpI(_ExactPar):
    """Incidental Operational Expense"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Opex^i')
