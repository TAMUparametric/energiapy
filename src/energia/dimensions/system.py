"""System"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .._core._dimension import _Dimension

if TYPE_CHECKING:
    from ..components.commodity.currency import Currency
    from ..components.commodity.emission import Emission
    from ..components.commodity.land import Land
    from ..components.commodity.material import Material
    from ..components.commodity.resource import Resource
    from ..components.game.couple import Couple
    from ..components.game.player import Player
    from ..components.operation.process import Process
    from ..components.operation.storage import Storage
    from ..components.operation.transport import Transport
    from ..represent.model import Model


@dataclass
class System(_Dimension):
    """System representation as a Resource Task Network (RTN)
    All resources and tasks are attached to this object
    
    :param model: Model to which the representation belongs.
    :type model: Model

    :ivar name: Name of the dimension, generated based on the class and model name. 
    :vartype name: str
    :ivar resources: List of resources. Defaults to [].
    :vartype resources: list[Resource]
    :ivar lands: List of land resources. Defaults to [].
    :vartype lands: list[Land]
    :ivar materials: List of material resources. Defaults to [].
    :vartype materials: list[Material]
    :ivar currencies: List of currency resources. Defaults to [].
    :vartype currencies: list[Currency]
    :ivar emissions: List of emission resources. Defaults to [].
    :vartype emissions: list[Emission]
    :ivar processes: List of processes. Defaults to [].
    :vartype processes: list[Process]
    :ivar storages: List of storage operations. Defaults to [].
    :vartype storages: list[Storage]
    :ivar transports: List of transport operations. Defaults to [].
    :vartype transports: list[Transport]
    :ivar players: List of players. Defaults to [].
    :vartype players: list[Player]
    :ivar couples: List of couples. Defaults to [].
    :vartype couples: list[Couple]
    """

    def __post_init__(self):
        # ---------- Commodities/Resources ----------

        self.resources: list[Resource] = []
        self.lands: list[Land] = []
        self.materials: list[Material] = []
        self.currencies: list[Currency] = []
        self.emissions: list[Emission] = []

        # ---------- Operations/Tasks ----------

        self.processes: list[Process] = []
        self.storages: list[Storage] = []
        self.transports: list[Transport] = []

        # ------------Decision-Makers----------------------
        self.players: list[Player] = []
        self.couples: list[Couple] = []

    @property
    def operations(self) -> list[Process | Storage | Transport]:
        """All Operations"""
        return self.processes + self.storages + self.transports
