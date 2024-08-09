from dataclasses import dataclass
from typing import Union

from ..components.analytical.player import Player
from ..components.asset.cash import Cash
from ..components.asset.land import Land
from ..components.commodity.resource import Resource
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit
from ..components.scope.network import Network
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ._task import _Task


@dataclass
class Trade(_Task):
    """Trade changes the ownership of Resource between Players"""

    def __post_init__(self):
        _Task.__post_init__(self)


@dataclass
class Transact(_Task):
    """Transact allows Players to give Cash for Resource"""

    def __post_init__(self):
        _Task.__post_init__(self)


@dataclass
class Ship(_Task):
    """Ship moves Resource between Locations"""

    def __post_init__(self):
        _Task.__post_init__(self)


@dataclass
class Operate(_Task):
    """Operate changes the state of Resource"""

    def __post_init__(self):
        _Task.__post_init__(self)


@dataclass
class Inventory(_Task):
    """Stash Resource and pull it out later in time"""

    def __post_init__(self):
        _Task.__post_init__(self)


@dataclass
class Capacitate(_Task):
    """Increase the capacity of a Storage"""

    def __post_init__(self):
        _Task.__post_init__(self)


@dataclass
class Emit(_Task):
    """Release Emissions"""

    def __post_init__(self):
        _Task.__post_init__(self)
