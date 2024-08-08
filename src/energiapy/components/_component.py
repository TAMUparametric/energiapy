"""Base Classes for Components
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._core._handy._dunders import _Dunders
from ..model._model import _Model

if TYPE_CHECKING:
    from .._core._aliases._is_input import IsInput
    from .._core._aliases._is_model import (IsAbstract, IsData, IsMatrix,
                                            IsProgram, IsSystem)


@dataclass
class _Component(_Dunders, _Model):

    def __post_init__(self):
        self.name = None

    @property
    def is_named(self):
        """The component has been named"""
        return self._named

    def personalize(
        self,
        name,
        system: IsSystem,
        data: IsData,
        matrix: IsMatrix,
        program: IsProgram,
        abstract: IsAbstract,
    ):
        """Personalize the compoenent
        give it a name (public),
        add model components
        """
        self.name = name
        self._named = True
        self._system = system
        self._data = data
        self._matrix = matrix
        self._program = program
        self._abstract = abstract


@dataclass
class _Scope(_Component):
    """Components which have only one instance in the model
    Horizon and Network are the only scope components
    """

    def __post_init__(self):
        _Component.__post_init__(self)


@dataclass
class _Temporal(_Component):
    """Temporal Component
    Basically the Scale which is derived from Horizon
    """

    def __post_init__(self):
        _Component.__post_init__(self)


@dataclass
class _DefinedComponent(_Component):
    """Common initial attributes of components"""

    basis: str = field(default='unit')
    citation: dict = field(default=None)  # TODO - for each attribute make dict
    block: str = field(default=None)
    introduce: str = field(default=None)
    retire: str = field(default=None)
    label: str = field(default=None)

    def __post_init__(self):
        _Component.__post_init__(self)
        self.ctypes = []

    @property
    def _horizon(self):
        """The Horizon of the Component"""
        return self._system.horizon

    @property
    def _network(self):
        """The Network of the Component"""
        return self._system.network


@dataclass
class _Commodity(_DefinedComponent):
    """Commodity Component"""

    def __post_init__(self):
        _DefinedComponent.__post_init__(self)


@dataclass
class _Operational(_DefinedComponent):
    """Operational Component"""

    def __post_init__(self):
        _DefinedComponent.__post_init__(self)


@dataclass
class _Spatial(_DefinedComponent):
    """Spatial Component"""

    def __post_init__(self):
        _DefinedComponent.__post_init__(self)


@dataclass
class _Analytical(_DefinedComponent):
    """Analytical Component"""

    def __post_init__(self):
        _DefinedComponent.__post_init__(self)
