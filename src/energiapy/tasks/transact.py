from dataclasses import dataclass

from .task import Task


@dataclass
class Transact(Task):
    """Transact Cash
    """

    def __post_init__(self):
        Task.__post_init__(self)


@dataclass
class Earn(Transact):
    """Earn from Sell Resource
    """

    def __post_init__(self):
        Transact.__post_init__(self)


@dataclass
class Spend(Transact):
    """Spend on Buy Resource
    """

    def __post_init__(self):
        Transact.__post_init__(self)


@dataclass
class Invest(Transact):
    """Invest to build Operation Capacity
    """

    def __post_init__(self):
        Transact.__post_init__(self)


@dataclass
class Penalty(Transact):
    """Penalty for not meeting Sell limit (demand)
    """

    def __post_init__(self):
        Transact.__post_init__(self)


@dataclass
class Credit(Transact):
    """Credit for Produce Resource
    """

    def __post_init__(self):
        Transact.__post_init__(self)
