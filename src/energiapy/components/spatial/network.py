"""Network is made up of Locations connected by Linkages
"""

from dataclasses import dataclass, field

from ...core._handy._dunders import _Dunders

from .linkage import Linkage
from .location import Location


@dataclass
class Network(_Dunders):
    """Network of Locations and Linkages

    Attributes:
        locs (list[str] | int): Locations in the Network
        label_locs (list[str]): label of Locations
        link_all (bool): link all Locations
        label (str): label of the Network
    """

    link_all: bool = field(default=False)

    def __post_init__(self):
        self.locations: list[Location] = []
        self.linkages: list[Linkage] = []

    def __setattr__(self, name, component):

        if isinstance(component, Location):
            self.locations.append(component)

        if isinstance(component, Linkage):
            self.linkages.append(component)

        super().__setattr__(name, component)

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