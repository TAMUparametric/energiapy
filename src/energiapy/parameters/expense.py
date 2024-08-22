"""Defined Expense Parameters 
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ._parameter import _Parameter


@dataclass
class BuyPrice(_Parameter):
    """Resource Buy Price"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @staticmethod
    def id() -> str:
        """Symbol"""
        return IndexedBase('Price^buy')


@dataclass
class SellPrice(_Parameter):
    """Resource Sell Price"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @staticmethod
    def id() -> str:
        """Symbol"""
        return IndexedBase('Price^sell')


@dataclass
class ResPenalty(_Parameter):
    """Resource Penalty Price"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @staticmethod
    def id() -> str:
        """Symbol"""
        return IndexedBase('Penalty')


@dataclass
class ResCredit(_Parameter):
    """Resource Buy Price"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @staticmethod
    def id() -> str:
        """Symbol"""
        return IndexedBase('Credit')


@dataclass
class UseExp(_Parameter):
    """Resource Use Expense"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @staticmethod
    def id() -> str:
        """Symbol"""
        return IndexedBase('Cost^use')


@dataclass
class CapExp(_Parameter):
    """Operation Capital Expense"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @staticmethod
    def id() -> str:
        """Symbol"""
        return IndexedBase('Capex')


@dataclass
class OpExp(_Parameter):
    """Operational Expense"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @staticmethod
    def id() -> str:
        """Symbol"""
        return IndexedBase('Opex')


@dataclass
class CapExpI(_Parameter):
    """Incidental Capital Expense"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @staticmethod
    def id() -> str:
        """Symbol"""
        return IndexedBase('Capex^i')


@dataclass
class OpExpI(_Parameter):
    """Incidental Operational Expense"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @staticmethod
    def id() -> str:
        """Symbol"""
        return IndexedBase('Opex^i')
