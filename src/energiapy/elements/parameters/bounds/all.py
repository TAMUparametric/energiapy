"""Defined Bound Parameters 
"""

from dataclasses import dataclass

from sympy import IndexedBase

from .._parameter import _BoundPar


@dataclass
class Has(_BoundPar):
    """Bound on What Commodoties a Player Has"""

    def __post_init__(self):
        _BoundPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Has')


@dataclass
class Needs(_BoundPar):
    """Bound on what Commodities a Player Needs"""

    def __post_init__(self):
        _BoundPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Needs')


@dataclass
class BuyBound(_BoundPar):
    """Buy Bounds"""

    def __post_init__(self):
        _BoundPar.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Buy{self.varbnd.value}')


@dataclass
class SllBound(_BoundPar):
    """Sell Bounds"""

    def __post_init__(self):
        _BoundPar.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Sell{self.varbnd.value}')


@dataclass
class ShpBound(_BoundPar):
    """Ship Bounds"""

    def __post_init__(self):
        _BoundPar.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Ship{self.varbnd.value}')


@dataclass
class SpdBound(_BoundPar):
    """Transact Bound on Spending"""

    def __post_init__(self):
        _BoundPar.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Spend{self.varbnd.value}')


@dataclass
class ErnBound(_BoundPar):
    """Transact Bound on Earning"""

    def __post_init__(self):
        _BoundPar.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Earn{self.varbnd.value}')


@dataclass
class CapBound(_BoundPar):
    """Capacitate Bounds"""

    def __post_init__(self):
        _BoundPar.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Capacitate{self.varbnd.value}')


@dataclass
class OprBound(_BoundPar):
    """Operation Bounds
    This one is multiplied by capacity
    """

    def __post_init__(self):
        _BoundPar.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Cap_F{self.varbnd.value}')


@dataclass
class UseBound(_BoundPar):
    """Use Bounds"""

    def __post_init__(self):
        _BoundPar.__post_init__(self)

    @property
    def id(self) -> str:
        """ID"""
        return IndexedBase(f'Use{self.varbnd.value}')


@dataclass
class EmnBound(_BoundPar):
    """Bound on Emission"""

    def __post_init__(self):
        _BoundPar.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Emit')
