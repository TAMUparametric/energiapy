"""Base Classes for Components
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..._core._handy._dunders import _Dunders
from ...blocks._base._model import _Model

if TYPE_CHECKING:
    from ..._core._aliases._is_block import IsData, IsMatrix, IsProgram, IsSystem


@dataclass
class _Component(_Dunders, _Model):

    def __post_init__(self):
        self.name = None
        self._named = False

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
