"""Trade Task
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ..disposition.structure import make_structures
from ._variable import _Variable


@dataclass
class Trade(_Variable):
    """Trade changes the ownership of Resource between Players
    This is a parent class
    """

    def __post_init__(self):
        _Variable.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""

    @classmethod
    def child(cls):
        """The Parent Variable doesnot carry Child Component"""


@dataclass
class LocTrade(Trade):
    """LocTrade changes the ownership of Resource between Players at a Location
    This is a parent class
    """

    def __post_init__(self):
        Trade.__post_init__(self)

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""
        return make_structures(cmd='res', opn='pro', spt=['loc', 'ntw'])


@dataclass
class Buy(LocTrade):
    """Buy allows Players to purchase Resource"""

    def __post_init__(self):
        LocTrade.__post_init__(self)

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('buy')


@dataclass
class Sell(LocTrade):
    """Sell allows Players to Sell Resource"""

    def __post_init__(self):
        LocTrade.__post_init__(self)

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('sell')


@dataclass
class Ship(Trade):
    """Resource sent out of a Location"""

    def __post_init__(self):
        Trade.__post_init__(self)

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""
        return make_structures(cmd='res', opn='trn', spt=['lnk', 'ntw'])

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('ship')
