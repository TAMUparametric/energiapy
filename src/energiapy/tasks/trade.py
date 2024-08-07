from dataclasses import dataclass
from typing import Union

from ._task import _Task
from ..components.commodity.cash import Cash
from ..components.commodity.land import Land
from ..components.commodity.resource import Resource
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit
from ..components.spatial.location import Location
from ..components.spatial.linkage import Linkage
from ..components.scope.network import Network
from ..components.analytical.player import Player


@dataclass
class Trade(_Task):
    """Trade changes the ownership of Resource between Players"""

    def __post_init__(self):
        self._between = Player
        self._at = Resource
        self._give = Resource
        self._take = Resource
        self._opn = Process
        self._spt = Location
        self._scp = Network

        _Task.__post_init__(self)


@dataclass
class Transact(_Task):
    """Transact allows Players to give Cash for Resource"""

    def __post_init__(self):
        self._between = Player
        self._at = Resource
        self._give = Cash
        self._take = Resource
        self._opn = Storage
        self._spt = Location
        self._scp = Network

        _Task.__post_init__(self)


@dataclass
class Ship(_Task):
    """Ship moves Resource between Locations"""

    def __post_init__(self):
        self._between = Location
        self._at = Resource
        self._also = Process
        self._optn = Union[Location, Network]
        self._give = Resource
        self._take = Resource

        _Task.__post_init__(self)

