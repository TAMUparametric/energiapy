"""Base for any Commodity Component
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .._base._defined import _Defined

if TYPE_CHECKING:
    from ..spatial.linkage import Linkage
    from ..spatial.location import Location


@dataclass
class _Commodity(_Defined):
    """Commodities"""

    def __post_init__(self):
        _Defined.__post_init__(self)

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
