"""Base for the Operational Components
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from pandas import DataFrame
from ...utils.scaling import scaling

from .._base._defined import _Defined
from .._base._nature import nature

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class _Operational(_Defined, ABC):
    """Operational Component"""

    capacity: IsBoundInput = field(default=True)
    operate: IsBoundInput = field(default=None)
    land: IsExactInput = field(default=None)
    material: IsExactInput = field(default=None)
    capex: IsExactInput = field(default=None)
    opex: IsExactInput = field(default=None)
    emission: IsExactInput = field(default=None)

    def __post_init__(self):
        _Defined.__post_init__(self)
        if isinstance(self.operate, DataFrame):
            self.operate = scaling(data=self.operate, how='max')

    @staticmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""
        return nature['operational']['bounds']

    @staticmethod
    def expenses():
        """Attrs that determine expenses of the component"""
        return nature['operational']['expenses']

    @staticmethod
    def emitted():
        """Attrs that determine emissions of the component"""
        return nature['operational']['emitted']

    @staticmethod
    def landuse():
        """Attrs that determine land use of the component"""
        return nature['operational']['landuse']

    @staticmethod
    def materialuse():
        """Attrs that determine material use of the component"""
        return nature['operational']['materialuse']

    @staticmethod
    def resourcebnds():
        """Attrs that determine resource bounds of the component"""
        return nature['resource']['bounds_trade']

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
    def _cnst_csh(cls):
        """Adds Cash when making consistent"""
        return cls.expenses()

    @classmethod
    def _cnst_lnd(cls):
        """Adds Land when making consistent"""
        return cls.landuse()

    @classmethod
    def _cnst_nstd(cls):
        """Is a nested input to be made consistent"""
        return (
            cls.materialuse() + cls.resourceloss() + cls.resourcebnds() + cls.emitted()
        )

    @classmethod
    def _cnst_nstd_csh(cls):
        """Is a nested input to be made consistent with Cash"""
        return cls.resourceexps()
