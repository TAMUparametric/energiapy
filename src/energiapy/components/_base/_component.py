"""Base Object for all Components
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...core._handy._dunders import _Dunders
from ...environ.program import Block

if TYPE_CHECKING:
    from ...environ.model import Model
    from ...environ.horizon import Horizon
    from ...environ.network import Network


@dataclass
class _Component(_Dunders):
    """This is inherited by all Components

    Personalizes the Component based on the attribute name set in Scenario

    Also adds Model and reports individual Blocks of the Model
    """

    def __post_init__(self):
        self.name = None
        self._named = False
        self._model: Model = None
        self.horizon: Horizon = None
        self.network: Network = None
        # this is a block of the Program
        # only contains modeling elements pertaining to the component
        self.block = Block(self)

    @property
    def is_named(self):
        """The component has been named"""
        return self._named

    @property
    def system(self):
        """The System of the Component"""
        return self._model.system

    @property
    def program(self):
        """The Mathematical Program of the Scenario"""
        return self._model.program

    @property
    def taskmaster(self):
        """Task Master of the Scenario"""
        return self._model.taskmaster

    @property
    def registrar(self):
        """Registrar of the Scenario"""
        return self._model.registrar

    def personalize(
        self,
        name: str,
        model: Model,
        horizon: Horizon,
        network: Network,
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
        self.horizon = horizon
        self.network = network
