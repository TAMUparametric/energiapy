"""Base for Commodity Component"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._consistent import _ConsistentBnd, _ConsistentCsh, _ConsistentNstd
from .._base._defined import _Defined

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class _Traded(_Defined, _ConsistentBnd, _ConsistentCsh, _ConsistentNstd, ABC):
    """Applied for Land, Material and Resource"""

    def __post_init__(self):
        _Defined.__post_init__(self)

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
            if getattr(self, attr) is not None:
                if attr in self.bounds():
                    self.make_bounds_consistent(attr)

                if attr in self._csh_inputs():
                    self.make_csh_consistent(attr)

                if attr in self._nstd_inputs():
                    self.make_nstd_consistent(attr)

        self._consistent = True


@dataclass
class _Used(_Traded):
    """Applies only for Land and Material"""

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
