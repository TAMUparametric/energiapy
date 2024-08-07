from dataclasses import dataclass
import stat

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

@dataclass
class Trade(_Task):
    """Trade Task
    Moves Resource
    """

    def __post_init__(self):
        _Task.__post_init__(self)


@dataclass
class Buy(Trade):
    """Buy Resource"""

    def __post_init__(self):

        self.cl_root = Resource
        self.cl_give = Resource
        self.cl_take = Resource 
        self.cl_opn = Process
        self.cl_spt = Location 
        self.cl_scp = Network 

        Trade.__post_init__(self)


@dataclass
class Sell(Trade):
    """Sell Resource at Location"""
