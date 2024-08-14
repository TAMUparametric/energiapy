"""Trade Task
"""

from dataclasses import dataclass

from ..disposition._structure import make_structures
from ._variable import _Variable


@dataclass
class Trade(_Variable):
    """Trade changes the ownership of Resource between Players"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the task"""
        return None


@dataclass
class LocTrade(Trade):
    """LocTrade changes the ownership of Resource between Players at a Location"""

    def __post_init__(self):
        Trade.__post_init__(self)

    @staticmethod
    def structures():
        """The allowed structures of disposition of the task"""
        return make_structures(cmd='res', opn='pro', spt=['loc', 'ntw'])


@dataclass
class Buy(LocTrade):
    """Buy allows Players to purchase Resource"""

    def __post_init__(self):
        LocTrade.__post_init__(self)


@dataclass
class Sell(LocTrade):
    """Sell allows Players to Sell Resource"""

    def __post_init__(self):
        LocTrade.__post_init__(self)


@dataclass
class Ship(Trade):
    """LocTrade changes the ownership of Resource between Players at a Location"""

    def __post_init__(self):
        Trade.__post_init__(self)

    @staticmethod
    def structures():
        """The allowed structures of disposition of the task"""
        return make_structures(cmd='res', opn='trn', spt=['lnk', 'ntw'])
