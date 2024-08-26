"""Base Classes for Components
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from ...core.aliases.is_block import IsModel


@dataclass
class _Component(_Dunders):
    """Base for all Components"""

    def __post_init__(self):
        self.name = None
        self._named = False
        self._model = None

    @property
    def is_named(self):
        """The component has been named"""
        return self._named

    @property
    def system(self):
        """The System of the Component"""
        return self._model.system

    @property
    def data(self):
        """The Data of the Component"""
        return getattr(self._model.data, self.name)

    @property
    def matrix(self):
        """The Matrix of the Component"""
        return getattr(self._model.matrix, self.name)

    @property
    def program(self):
        """The Program of the Component"""
        return getattr(self._model.program, self.name)

    @property
    def attr(self):
        """The Attributes of the Component"""
        return self._model.attr

    def personalize(
        self,
        name: str,
        model: IsModel,
    ):
        """Personalize the compoenent
        give it a name (public),
        add model components

        Args:
            name (str): name of the component. Given as Scenario attribute
            model (IsModel): Model with System, Program, Data, Matrix
        """
        self.name = name
        self._named = True  # update flag
        self._model = model
