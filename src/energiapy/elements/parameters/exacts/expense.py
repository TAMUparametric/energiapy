"""Defined Transact Parameters 
"""

from dataclasses import dataclass

from sympy import IndexedBase

from .._parameter import _ExactPar


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
class SllPrice(_ExactPar):
    """Resource Sell Price"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Price^sell')


@dataclass
class SllPenalty(_ExactPar):
    """Resource Transact Price"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Penalty')


@dataclass
class SllCredit(_ExactPar):
    """Resource Buy Price"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Credit')


@dataclass
class UseCost(_ExactPar):
    """Resource Use Transact"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Cost^use')


@dataclass
class StpExpense(_ExactPar):
    """Operation Capital Transact"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Capex')


@dataclass
class OprExpense(_ExactPar):
    """Operational Transact"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Opex')


@dataclass
class StpExpenseI(_ExactPar):
    """Incidental Capital Transact"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Capex^i')


@dataclass
class OpExpI(_ExactPar):
    """Incidental Operational Transact"""

    def __post_init__(self):
        _ExactPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Opex^i')
