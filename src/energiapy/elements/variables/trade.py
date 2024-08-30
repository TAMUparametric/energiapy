"""Trade Task
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ..dispositions.structure import make_structures
from ._variable import _BoundVar

# ---------------MixIns---------------


@dataclass
class _Trade(_BoundVar):
    """Trade changes the ownership of Resource between Players
    This is a parent class
    """

    def __post_init__(self):
        _BoundVar.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""

    @classmethod
    def child(cls):
        """The Parent Variable doesnot carry Child Component"""


@dataclass
class _LocTrade(_Trade):
    """LocTrade changes the ownership of Resource between Players at a Location
    This is a parent class
    """

    def __post_init__(self):
        _Trade.__post_init__(self)

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""
        return make_structures(cmd='res', opn='pro', spt=['loc', 'ntw'])


#-------------Variables---------------

@dataclass
class Buy(_LocTrade):
    """Buy allows Players to purchase Resource"""

    def __post_init__(self):
        _LocTrade.__post_init__(self)

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('buy')


@dataclass
class Sell(_LocTrade):
    """Sell allows Players to Sell Resource"""

    def __post_init__(self):
        _LocTrade.__post_init__(self)

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('sell')


@dataclass
class Ship(_Trade):
    """Resource sent out of a Location"""

    def __post_init__(self):
        _Trade.__post_init__(self)

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""
        return make_structures(cmd='res', opn='trn', spt=['lnk', 'ntw'])

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('ship')
