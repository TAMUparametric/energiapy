from dataclasses import dataclass

from ..components.asset.cash import Cash
from ..components.asset.land import Land
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ._task import Task
from .trade import Acquire


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
