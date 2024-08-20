"""Base for Commodity Component"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from ..._core._nirop._error import check_attr
from .._base._consistent import _ConsistentBnd, _ConsistentCsh, _ConsistentNstd
from .._base._defined import _Defined

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsLinkage, IsLocation
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput


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

    def make_consistent(self):
        """Makes the data inputs consistent IsSptTmpDict"""

        for attr in self.inputs():

            check_attr(component=self, attr=attr)

            if getattr(self, attr) is not None:
                if attr in self.bounds():
                    self.make_bounds_consistent(attr)

                if attr in self._csh_inputs():
                    self.make_csh_consistent(attr)

                if attr in self._nstd_inputs():
                    self.make_nstd_consistent(attr)

        # update flag, the inputs have been made consistent
        self._consistent = True


@dataclass
class _Used(_Traded):
    """Applies only for Land and Material
    For now, do not subsume my limitations
    Do whatever you can or want to with energiapy

    Attributes:
        use (IsBoundInput): bound for use at some spatiotemporal disposition
        cost (IsExactInput): cost per a unit basis at some spatiotemporal disposition
        emission (IsExactInput): emission per unit basis of use
    """

    use: IsBoundInput = field(default=None)
    cost: IsExactInput = field(default=None)
    emission: IsExactInput = field(default=None)

    def __post_init__(self):
        _Traded.__post_init__(self)

    @staticmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""
        return ['use']

    @staticmethod
    def expenses():
        """Attrs that determine expenses of the component"""
        return ['cost']

    @staticmethod
    def emitted():
        """Attrs that determine emissions of the component"""
        return ['emission']
