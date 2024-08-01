from .task import Task
from dataclasses import dataclass
from .trade import Acquire


@dataclass
class Invest(Task):
    """Invest Cash for Operation
    """

    def __post_init__(self):
        Task.__post_init__(self)


@dataclass
class Purchase(Invest):
    """Purchase Land for Operation
    """

    def __post_init__(self):
        Invest.__post_init__(self)

    @staticmethod
    def _dependent():
        return Acquire

    @staticmethod
    def _variable():
        return 'land'
