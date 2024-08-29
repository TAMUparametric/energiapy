"""Base for Commodity Component"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, List

from ...attrs.bounds import UsedBounds
from ...attrs.exacts import UsedEmnExacts, UsedExpExacts
from .._base._defined import _Defined

if TYPE_CHECKING:
    from ...core.aliases.is_component import IsLinkage, IsLocation


class _Commodity(ABC):
    """Commodities that are Traded"""

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
    def locations(self, locations: List[IsLocation]):
        """Set Locations"""
        self._locations = locations

    @property
    def linkages(self):
        """Linkages where Commodity exists"""
        return self._linkages

    @linkages.setter
    def linkages(self, linkages: List[IsLinkage]):
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
class _Used(UsedBounds, UsedExpExacts, UsedEmnExacts, _Traded):
    """Applies only for Land and Material
    For now, do not subsume my limitations
    Do whatever you can or want to with energiapy

    Attributes:
        use (IsBoundInput): bound for use at some spatiotemporal disposition
        cost (IsExactInput): cost per a unit basis at some spatiotemporal disposition
        emission (IsExactInput): emission per unit basis of use
    """

    def __post_init__(self):
        _Traded.__post_init__(self)

    @staticmethod
    def inputs():
        """Input attributes"""
        return [
            f.name
            for f in fields(UsedBounds) + fields(UsedExpExacts) + fields(UsedEmnExacts)
        ]
