from dataclasses import dataclass

from .task import Task


@dataclass
class Trade(Task):
    """Trade Task
    Moves Resource
    """

    def __post_init__(self):
        Task.__post_init__(self)


@dataclass
class Buy(Trade):
    """Buy Resource at Location"""

    def __post_init__(self):
        Trade.__post_init__(self)


@dataclass
class Sell(Trade):
    """Sell Resource at Location"""

    def __post_init__(self):
        Trade.__post_init__(self)


@dataclass
class Consume(Trade):
    """Consume Resource via Process"""

    def __post_init__(self):
        Trade.__post_init__(self)


@dataclass
class Dispatch(Trade):
    """Consume Resource via Process"""

    def __post_init__(self):
        Trade.__post_init__(self)


@dataclass
class Charge(Trade):
    """Charge Resource via Storage"""

    def __post_init__(self):
        Trade.__post_init__(self)


@dataclass
class Discharge(Trade):
    """Discharge Resource via Storage"""

    def __post_init__(self):
        Trade.__post_init__(self)


@dataclass
class Export(Trade):
    """Export Resource via Transit"""

    def __post_init__(self):
        Trade.__post_init__(self)


@dataclass
class Import(Trade):
    """Import Resource via Transit"""

    def __post_init__(self):
        Trade.__post_init__(self)


@dataclass
class Procure(Trade):
    """Procure Material for Operation"""

    def __post_init__(self):
        Trade.__post_init__(self)


@dataclass
class Use(Trade):
    """Use Material for Operation"""

    def __post_init__(self):
        Trade.__post_init__(self)


@dataclass
class Acquire(Trade):
    """Acquire Land for Operation"""

    def __post_init__(self):
        Trade.__post_init__(self)
