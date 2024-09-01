"""Base for Spatial Components
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .._base._component import _Component


@dataclass
class _Spatial(_Component, ABC):
    """Spatial Component"""

    def __post_init__(self):
        _Component.__post_init__(self)

    @property
    @abstractmethod
    def operations(self):
        """Operations in the Spatial Component"""

    @property
    def cash(self):
        """Cash Commodity"""
        return self.system.cash

    @property
    def land(self):
        """Land Commodity"""
        return self.system.land

    @property
    def resources(self):
        """Resources in Inventory"""
        return self.fetch_cmd('resources')

    @property
    def materials(self):
        """Materials in Inventory"""
        return self.fetch_cmd('materials')

    @property
    def emissions(self):
        """Emissions in Inventory"""
        return self.fetch_cmd('emissions')

    @property
    def commodities(self):
        """Commodities in Inventory"""
        return (
            self.resources + self.materials + self.emissions + [self.cash] + [self.land]
        )

    def fetch(self, operation):
        """Fetches what Operational Components are in the Spatial Component"""
        return [opn for opn in getattr(self.system, operation) if self in opn.spatials]

    def fetch_cmd(self, commodity):
        """Fetches what Components are in the Spatial Component"""
        return sorted(
            set(sum([getattr(spt, commodity) for spt in self.operations], []))
        )
