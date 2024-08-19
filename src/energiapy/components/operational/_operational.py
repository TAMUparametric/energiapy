"""Base for the Operational Components
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pandas import DataFrame

from ...utils.scaling import scaling
from .._base._consistent import (_ConsistentBnd, _ConsistentCsh,
                                 _ConsistentLnd, _ConsistentNstd,
                                 _ConsistentNstdCsh)
from .._base._defined import _Defined

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class _Operational(
    _Defined,
    _ConsistentBnd,
    _ConsistentCsh,
    _ConsistentLnd,
    _ConsistentNstd,
    _ConsistentNstdCsh,
    ABC,
):

    capacity: IsBoundInput = field(default=True)
    land: IsExactInput = field(default=None)
    material: IsExactInput = field(default=None)
    capex: IsExactInput = field(default=None)
    opex: IsExactInput = field(default=None)
    emission: IsExactInput = field(default=None)

    def __post_init__(self):
        _Defined.__post_init__(self)
        self.operate = self._operate
        if isinstance(self._operate, DataFrame):
            self.operate = scaling(data=self.operate, how='max')

    @property
    @abstractmethod
    def _operate(self):
        """Returns attribute value that signifies operating bounds"""

    @staticmethod
    @abstractmethod
    def _spatials():
        """Spatial Components where the Operation is located"""

    @property
    @abstractmethod
    def resources(self):
        """Resources Involved"""

    @staticmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""
        return ['capacity', 'operate']

    @staticmethod
    def expenses():
        """Attrs that determine expenses of the component"""
        return ['capex', 'opex']

    @staticmethod
    def emitted():
        """Attrs that determine emissions of the component"""
        return ['emission']

    @staticmethod
    def landuse():
        """Attrs that determine land use of the component"""
        return ['land']

    @staticmethod
    def materialuse():
        """Attrs that determine material use of the component"""
        return ['material']

    @staticmethod
    @abstractmethod
    def resourcebnds():
        """Attrs that determine resource bounds of the component"""

    @staticmethod
    @abstractmethod
    def resourceexps():
        """Attrs that determine resource expenses of the component"""

    @staticmethod
    @abstractmethod
    def resourceloss():
        """Attrs that determine resource loss of the component"""

    @classmethod
    def inputs(cls):
        """Attrs"""
        return (
            cls.bounds()
            + cls.expenses()
            + cls.emitted()
            + cls.landuse()
            + cls.resourcebnds()
            + cls.resourceexps()
            + cls.materialuse()
            + cls.resourceloss()
        )

    @classmethod
    def _csh_inputs(cls):
        """Adds Cash when making consistent"""
        return cls.expenses()

    @classmethod
    def _lnd_input(cls):
        """Adds Land when making consistent"""
        return cls.landuse()

    @classmethod
    def _nstd_inputs(cls):
        """Is a nested input to be made consistent"""
        return (
            cls.materialuse() + cls.resourceloss() + cls.resourcebnds() + cls.emitted()
        )

    @classmethod
    def _nstd_csh_inputs(cls):
        """Is a nested input to be made consistent with Cash"""
        return cls.resourceexps()

    @property
    def spatials(self):
        """Spatial Components where the Operation is located"""
        return getattr(self, self._spatials())

    @property
    def materials(self):
        """Materials used in the Operation"""
        if self.material:
            return [i.disposition.mat for i in self.material]
        else:
            return []

    @property
    def emissions(self):
        """Emissions from the Operation"""
        if self.emission:
            return [i.disposition.emn for i in self.emission]
        else:
            return []

    def locate(self):
        """Locates the Component"""

        spatials = self._spatials()
        value = self.spatials

        if value and not isinstance(value, list):
            setattr(self, spatials, [value])

        if not value:
            setattr(self, spatials, getattr(self._model.system, spatials))

    def make_consistent(self):
        """Makes the data inputs consistent IsSptTmpDict"""
        for attr in self.inputs():
            if getattr(self, attr) is not None:

                if attr in self.bounds():
                    self.make_bounds_consistent(attr)

                if attr in self._csh_inputs():
                    self.make_csh_consistent(attr)

                if attr in self._lnd_input():
                    self.make_lnd_consistent(attr)

                if attr in self._nstd_inputs():
                    self.make_nstd_consistent(attr)

                if attr in self._nstd_csh_inputs():
                    self.make_nstd_csh_consistent(attr)

        self._consistent = True
