from dataclasses import dataclass

from ._task import Task


@dataclass
class Invest(Task):
    """Invest Cash for Operation"""

    def __post_init__(self):
        Task.__post_init__(self)


@dataclass
class Purchase(Invest):
    """Purchase Land for Operation"""

    def __post_init__(self):
        Invest.__post_init__(self)
        self.dependent = Acquire
        self.trigger = 'land_cost'
        self.derived = Cash
        self.commodity = Land
        self.operational = None
        self.spatial = (Location, Linkage)

    @staticmethod
    def _dependent():
        return Acquire

    @staticmethod
    def _trigger():
        return 'land_cost'

    @staticmethod
    def _derived():
        return Cash

    @staticmethod
    def _commodity():
        return Land

    @staticmethod
    def _operational():
        return None

    @staticmethod
    def _spatial():
        return (Location, Linkage)
    
    
    


@dataclass
class Transact(Task):
    """Transact Cash"""

    def __post_init__(self):
        Task.__post_init__(self)


@dataclass
class Earn(Transact):
    """Earn from Sell Resource"""

    def __post_init__(self):
        Transact.__post_init__(self)


@dataclass
class Spend(Transact):
    """Spend on Buy Resource"""

    def __post_init__(self):
        Transact.__post_init__(self)


@dataclass
class Invest(Transact):
    """Invest to build Operation Capacity"""

    def __post_init__(self):
        Transact.__post_init__(self)


@dataclass
class Penalty(Transact):
    """Penalty for not meeting Sell limit (demand)"""

    def __post_init__(self):
        Transact.__post_init__(self)


@dataclass
class Credit(Transact):
    """Credit for Produce Resource"""

    def __post_init__(self):
        Transact.__post_init__(self)
