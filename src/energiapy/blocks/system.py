from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from ..components.analytical.player import Player
from ..components.commodity.cash import Cash
from ..components.commodity.land import Land
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource, ResourceStg
from ..components.commodity.emission import Emission
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit
from ..components.scope.horizon import Horizon
from ..components.scope.network import Network
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.temporal.scale import Scale
from ._base._block import _Block

if TYPE_CHECKING:
    from .._core._aliases._is_component import IsComponent


@dataclass
class System(_Block):
    """Collects System Components"""

    name: str = field(default=None)

    def __post_init__(self):

        _Block.__post_init__(self)

        self.name = f'System|{self.name}|'

        # SpatioTemporal Scope
        # Is always [Horizon, Network]
        self.scopes = [None, None]

        # Assets
        # Is always [Cash, Land]
        self.assets = [None, None]

    def __setattr__(self, name, value):

        if isinstance(value, Horizon):
            self.scopes[0] = value
        elif isinstance(value, Network):
            self.scopes[1] = value

        elif isinstance(value, Cash):
            self.assets[0] = value
        elif isinstance(value, Land):
            self.assets[1] = value

        super().__setattr__(name, value)

    @property
    def horizon(self):
        """Returns the Horizon of the System"""
        return self.scopes[0]

    @property
    def network(self):
        """Returns the Network of the System"""
        return self.scopes[1]

    @property
    def cash(self):
        """Returns the Cash of the System"""
        return self.assets[0]

    @property
    def land(self):
        """Returns the Land of the System"""
        return self.assets[1]

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

    def fetch(self, cmp: IsComponent) -> List[IsComponent]:
        """Fetches defined Components of a particular class in the System

        Args:
            cmp (IsComponent): Component type

        Returns:
            List[IsComponent]: list of defined Components
        """
        return sorted(
            [
                getattr(self, k)
                for k, v in self.components().items()
                if isinstance(v, cmp)
            ]
        )
