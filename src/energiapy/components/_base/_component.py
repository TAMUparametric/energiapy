"""Base Object for all Components
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from ......gana.src.gana.block.prg import Prg

if TYPE_CHECKING:
    from ...environ.model import Model
    from ...environ.horizon import Horizon
    from ...environ.network import Network
    from ...environ.system import System


class _Component:
    """This is inherited by all Components

    Personalizes the Component based on the attribute name set in Scenario

    Also adds Model and reports individual Blocks of the Model
    """

    def __init__(self):
        self.name: str = None
        self._named: bool = False
        self._model: Model = None
        # this is a block of the Program
        # only contains modeling elements pertaining to the component
        self.prg = Prg(self.name)

    @property
    def system(self) -> System:
        """The System of the Component"""
        return self._model.system

    @property
    def horizon(self) -> Horizon:
        """The Horizon of the Scenario"""
        return self._model.horizon

    @property
    def network(self) -> Network:
        """The Network of the Scenario"""
        return self._model.network

    @property
    def program(self) -> Prg:
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


