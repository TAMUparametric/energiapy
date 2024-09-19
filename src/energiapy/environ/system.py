"""System Model Block represents the Scenario through Components
"""

from dataclasses import dataclass, field

from ..components.analytical.player import Player
from ..components.commodity.cash import Cash
from ..components.commodity.emission import Emission
from ..components.commodity.land import Land
from ..components.commodity.resource import Resource
from ..components.operation.process import Process
from ..components.operation.storage import Storage
from ..components.operation.transit import Transit
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.spatial.network import Network
from ..components.temporal.horizon import Horizon
from ..components.temporal.scale import Scale

from ..core._handy._dunders import _Dunders


@dataclass
class System(_Dunders):
    """System is the representation of the Scenario through the use of Components

    The methodology of commodification of the Scenario draws from the resource task network (RTN)

    Read more about the RTN methodology in the following paper:

        Barbosa-Póvoa, A. P. F. D., & Pantelides, C. C. (1997).
        Design of multipurpose plants using the resource-task network unified framework.
        Computers & chemical engineering, 21, S703-S708.

    The Components that can be added to the System are:

    Scopes:
        - Horizon (discretized into Temporal Scales)
        - Network (Locations connected via Linkages)

    Temporal:
        - Scale

    Spatial:
        - Location
        - Linkage

    Commodities:
        - Resource
        - Emission
        - Cash
        - Land

    Operations:
        - Process
        - Storage
        - Transit

    Scales and Locations are birthed internally

    Storages birth Charging and Discharging Processes and ResourceStg
    Transits birth Loading and Unloading Processes and ResourceTrn

    Attributes:

        name (str): name of the System, takes from Scenario

    """

    name: str = field(default="System")

    def __post_init__(self):

        # declare the scopes of the problem
        self.horizon = Horizon()
        self.network = Network()

        # create empty lists to collect declared components
        self.players: list[Player] = []
        self.emissions: list[Emission] = []
        self.cashes: list[Cash] = []
        self.resources: list[Resource] = []
        self.lands: list[Land] = []
        self.processes: list[Process] = []
        self.storages: list[Storage] = []
        self.transits: list[Transit] = []
        self.locations: list[Location] = []
        self.linkages: list[Linkage] = []
        self.scales: list[Scale] = []

    def __setattr__(self, name, component):

        # add components to the collections
        if isinstance(component, Player):
            self.players.append(component)

        if isinstance(component, Emission):
            self.emissions.append(component)

        if isinstance(component, Cash):
            self.cashes.append(component)

        if isinstance(component, Resource):
            self.resources.append(component)

        if isinstance(component, Land):
            self.lands.append(component)

        if isinstance(component, Process):
            self.processes.append(component)

        if isinstance(component, Storage):
            self.storages.append(component)

        if isinstance(component, Transit):
            self.transits.append(component)

        if isinstance(component, Location):
            self.locations.append(component)

        if isinstance(component, Linkage):
            self.linkages.append(component)

        if isinstance(component, Scale):
            self.scales.append(component)

        super().__setattr__(name, component)

    @property
    def scopes(self):
        """Scopes of the System"""
        return [self.horizon, self.network]

    @property
    def spatials(self):
        """Returns the Spatials of the System"""
        return self.locations + self.linkages

    @property
    def commodities(self):
        """Returns the Commodity Components of the System"""
        return self.resources + self.emissions + self.cashes + self.lands

    @property
    def operations(self):
        """Returns the Operations of the System"""
        return self.processes + self.storages + self.transits

    @property
    def components(self):
        """Returns all the Components of the System"""
        return self.scopes + self.spatials + self.commodities + self.operations

    @property
    def nodes(self):
        """Nodes of the System are just Locations"""
        return self.locations

    @property
    def edges(self):
        """Edges of the System are just Linkages"""
        return self.linkages

    @property
    def pairs(self):
        """Source Sink pairs of the System"""
        return [(i.source, i.sink) for i in self.linkages]

    @property
    def sources(self):
        """Source Locations of the System"""
        return sorted({i[0] for i in self.pairs})

    @property
    def sinks(self):
        """Sink Locations of the System"""
        return sorted({i[1] for i in self.pairs})
