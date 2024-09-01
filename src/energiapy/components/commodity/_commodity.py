"""Base for any Commodity Component
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..scope.spatial.linkage import Linkage
    from ..scope.spatial.location import Location


class _Commodity(ABC):
    """Commodities that are:

    Traded (Trade) - Resource
    Lost (Lose) - Resource
    Used (Use) - Material, Land
    Emitted (Emit) - Emission
    Transacted - Cash

    """

    def __post_init__(self):

        # This flag is used to check if the Commodity has been located
        # (assigned) to a Location or Linkage
        self._located = False

    @property
    @abstractmethod
    def system(self):
        """System Block"""

    @property
    def locations(self):
        """Locations where Commodity exists"""
        return self._locations

    @locations.setter
    def locations(self, locations: list[Location]):
        """Set Locations"""
        self._locations = locations

    @property
    def linkages(self):
        """Linkages where Commodity exists"""
        return self._linkages

    @linkages.setter
    def linkages(self, linkages: list[Linkage]):
        """Set Linkages"""
        self._linkages = linkages

    def locate(self):
        """Locates the Commodity"""
        setattr(
            self,
            'locations',
            [loc for loc in self.system.locations if self in loc.commodities],
        )
        setattr(
            self,
            'linkages',
            [lnk for lnk in self.system.linkages if self in lnk.commodities],
        )

        self._located = True

    @property
    def is_located(self):
        """Is located"""
        return self._located
