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
