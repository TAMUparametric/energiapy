"""System Model Block represents the Scenario through Components
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from ..components.analytical.player import Player
from ..components.commodity.emission import Emission
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource, ResourceStg, ResourceTrn
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.temporal.scale import Scale
from ._block import _Block

if TYPE_CHECKING:
    from ..core.aliases.is_component import (IsCash, IsDefined, IsHorizon,
                                             IsLand, IsNetwork)


@dataclass
class System(_Block):
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
        - Material
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

    name: str = field(default=None)

    def __post_init__(self):

        _Block.__post_init__(self)

        self.name = f'System|{self.name}|'

    @property
    def horizon(self):
        """Returns the Horizon of the System"""
        return self._horizon

    @horizon.setter
    def horizon(self, horizon: IsHorizon):
        """Sets the Horizon of the System"""
        self._horizon = horizon

    @property
    def network(self):
        """Returns the Network of the System"""
        return self._network

    @network.setter
    def network(self, network: IsNetwork):
        """Sets the Network of the System"""
        self._network = network

    @property
    def cash(self):
        """Returns the Cash of the System"""
        return self._cash

    @cash.setter
    def cash(self, cash: IsCash):
        """Sets the Cash of the System"""
        self._cash = cash

    @property
    def land(self):
        """Returns the Land of the System"""
        return self._land

    @land.setter
    def land(self, land: IsLand):
        """Sets the Land of the System"""
        self._land = land

    @property
    def locations(self):
        """Returns the Locations of the System"""
        return self.fetch(Location)

    @property
    def linkages(self):
        """Returns the Linkages of the System"""
        return self.fetch(Linkage)

    @property
    def spatials(self):
        """Returns the Spatials of the System"""
        return self.locations + self.linkages

    @property
    def scales(self):
        """Returns the Scales of the System"""
        return self.fetch(Scale)

    @property
    def players(self):
        """Returns the Players of the System"""
        return self.fetch(Player)

    @property
    def resources(self):
        """Returns the Resources of the System"""
        return self.fetch(Resource)

    @property
    def resources_stg(self):
        """Returns the Stored Resources of the System"""
        return self.fetch(ResourceStg)

    @property
    def resources_trn(self):
        """Returns the Transit Resources of the System"""
        return self.fetch(ResourceTrn)

    @property
    def materials(self):
        """Returns the Materials of the System"""
        return self.fetch(Material)

    @property
    def emissions(self):
        """Returns the Emissions of the System"""
        return self.fetch(Emission)

    @property
    def commodities(self):
        """Returns the Commodity Components of the System"""
        return (
            self.resources + self.materials + self.emissions + [self.cash] + [self.land]
        )

    @property
    def processes(self):
        """Returns the Processes of the System"""
        return self.fetch(Process)

    @property
    def storages(self):
        """Returns the Storages of the System"""
        return self.fetch(Storage)

    @property
    def transits(self):
        """Returns the Transits of the System"""
        return self.fetch(Transit)

    @property
    def operations(self):
        """Returns the Operations of the System"""
        return self.processes + self.storages + self.transits

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

    def fetch(self, cmp: IsDefined) -> List[IsDefined]:
        """Fetches defined Components of a particular class in the System

        Args:
            cmp (IsDefined): Component type

        Returns:
            List[IsDefined]: list of defined Components
        """
        return sorted(
            [
                getattr(self, name)
                for name, component in self.components().items()
                if isinstance(component, cmp)
            ]
        )
