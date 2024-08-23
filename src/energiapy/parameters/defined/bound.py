"""Defined Expense Parameters 
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ._parameter import _Bnd


@dataclass
class BuyBnd(_Bnd):
    """Buy Bounds"""

    def __post_init__(self):
        _Bnd.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Buy{self.varbnd.value}')


@dataclass
class SellBnd(_Bnd):
    """Sell Bounds"""

    def __post_init__(self):
        _Bnd.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Sell{self.varbnd.value}')


@dataclass
class ShipBnd(_Bnd):
    """Ship Bounds"""

    def __post_init__(self):
        _Bnd.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Ship{self.varbnd.value}')


@dataclass
class SpendBnd(_Bnd):
    """Expense Bound on Spending"""

    def __post_init__(self):
        _Bnd.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Spend{self.varbnd.value}')


@dataclass
class EarnBnd(_Bnd):
    """Expense Bound on Earning"""

    def __post_init__(self):
        _Bnd.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Earn{self.varbnd.value}')


@dataclass
class CapBnd(_Bnd):
    """Capacity Bounds"""

    def __post_init__(self):
        _Bnd.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Capacity{self.varbnd.value}')


@dataclass
class OpBnd(_Bnd):
    """Operation Bounds
    This one is multiplied by capacity
    """

    def __post_init__(self):
        _Bnd.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Cap_F{self.varbnd.value}')


@dataclass
class UseBnd(_Bnd):
    """Use Bounds"""

    def __post_init__(self):
        _Bnd.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Use{self.varbnd.value}')
