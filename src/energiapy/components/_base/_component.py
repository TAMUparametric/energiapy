"""Base Object for all Components
"""

from __future__ import annotations

from dataclasses import dataclass, field 
from typing import TYPE_CHECKING

from ...core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from ...environ.model import Model


@dataclass
class _Component(_Dunders):
    """This is inherited by all Components

    Personalizes the Component based on the attribute name set in Scenario

    Also adds Model and reports individual Blocks of the Model
    """

    label: str = field(default=None)

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
    def program_full(self):
        """The Program for the entire Scenario"""
        return self._model.program

    @property
    def taskmaster(self):
        """Chanakya of the Scenario"""
        return self._model.taskmaster

    @property
    def rulebook(self):
        """Bhaskara of the Scenario"""
        return self._model.rulebook

    @property
    def registrar(self):
        """Registrar of the Scenario"""
        return self._model.registrar

    def personalize(
        self,
        name: str,
        model: Model,
    ):
        """Personalize the compoenent
        give it a name (public),
        add model components

        Args:
            name (str): name of the component. Given as Scenario attribute
            model (IsModel): Model with System, Program, Data, Matrix, Chanakya, Rulebook, Registrar
        """
        self.name = name
        self._named = True  # update flag
        self._model = model
