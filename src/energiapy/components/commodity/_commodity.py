"""Base for Commodity Component"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, List

from ...core.nirop.errors import check_attr
from .._base._consistent import _ConsistentBnd, _ConsistentCsh, _ConsistentNstd
from .._base._defined import _Defined
from ...attrs.bounds import UsedBounds
from ...attrs.exacts import UsedExpExacts, UsedEmnExacts

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
class _Traded(
    _Defined, _Commodity, _ConsistentBnd, _ConsistentCsh, _ConsistentNstd, ABC
):
    """Applied for Land, Material and Resource"""

    def __post_init__(self):
        _Defined.__post_init__(self)
        _Commodity.__post_init__(self)

    @staticmethod
    @abstractmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""

    @staticmethod
    @abstractmethod
    def expenses():
        """Attrs that determine expenses of the component"""

    @staticmethod
    @abstractmethod
    def emitted():
        """Attrs that determine emissions of the component"""

    @classmethod
    def inputs(cls):
        """Attrs"""
        return cls.bounds() + cls.expenses() + cls.emitted()

    @classmethod
    def _csh_inputs(cls):
        """Adds Cash when making consistent"""
        return cls.expenses()

    @classmethod
    def _nstd_inputs(cls):
        """Is a nested input to be made consistent"""
        return cls.emitted()

    def make_consistent(self, ok_inconsistent: bool):
        """Makes the data inputs consistent IsSptTmpDict

        Args:
            ok_inconsistent (bool): Fix Dispositions, with warnings.

        """

        for attr in self.inputs():

            check_attr(component=self, attr=attr)

            if getattr(self, attr) is not None:
                if attr in self.bounds():
                    self.make_bounds_consistent(attr, ok_inconsistent)

                if attr in self._csh_inputs():
                    self.make_csh_consistent(attr, ok_inconsistent)

                if attr in self._nstd_inputs():
                    self.make_nstd_consistent(attr, ok_inconsistent)

        # update flag, the inputs have been made consistent
        self._consistent = True


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
    def bounds():
        """Attrs that quantify the bounds of the component"""
        return fields(UsedBounds)

    @staticmethod
    def expenses():
        """Attrs that determine expenses of the component"""
        return fields(UsedExpExacts)

    @staticmethod
    def emitted():
        """Attrs that determine emissions of the component"""
        return fields(UsedEmnExacts)
