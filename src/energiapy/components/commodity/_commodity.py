"""Base for Commodity Component"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from .._attrs._bounds import _UsdBounds
from .._attrs._exacts import _UsdEmnExacts, _UsdExpExacts
from .._base._defined import _Defined

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


@dataclass
class _Traded(_Defined, _Commodity, ABC):
    """Applied for Land, Material and Resource"""

    def __post_init__(self):
        _Defined.__post_init__(self)
        _Commodity.__post_init__(self)

    @staticmethod
    @abstractmethod
    def inputs():
        """Input Attributes"""


@dataclass
class _Used(_UsdBounds, _UsdExpExacts, _UsdEmnExacts, _Traded):
    """Applies only for Land and Material
    For now, do not subsume my limitations
    Do whatever you can or want to with energiapy

    Attributes:
        use (IsBnd): bound for use at some spatiotemporal disposition
        cost (IsExt): cost per a unit basis at some spatiotemporal disposition
        emission (IsExt): emission per unit basis of use
    """

    def __post_init__(self):
        _Traded.__post_init__(self)

    @staticmethod
    def inputs():
        """Input attributes"""
        return [
            f.name
            for f in fields(_UsdBounds) + fields(_UsdExpExacts) + fields(_UsdEmnExacts)
        ]
