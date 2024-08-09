"""Base Classes for Components
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..._core._handy._dunders import _Dunders
from ...blocks._model import _Model

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsInput
    from ..._core._aliases._is_block import (IsAbstract, IsData, IsMatrix,
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
