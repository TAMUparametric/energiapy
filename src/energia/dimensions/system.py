"""System"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..core.dimension import Dimension

if TYPE_CHECKING:
    from ..components.commodity.currency import Currency
    from ..components.commodity.emission import Emission
    from ..components.commodity.land import Land
    from ..components.commodity.material import Material
    from ..components.commodity.resource import Resource
    from ..components.operation.process import Process
    from ..components.operation.storage import Storage
    from ..components.operation.transport import Transport
    from ..components.game.couple import Couple
    from ..components.game.player import Player
    from ..represent.model import Model


@dataclass
class System(Dimension):
    """System representation as a Resource Task Network (RTN)


    All resources and tasks are attached to this object


    """

    model: Model

    def __post_init__(self):
        self.name = f'System({self.model.name})'

        # ---------- Commodities/Resources ----------

        self.resources: list[Resource] = []
        self.lands: list[Land] = []
        self.materials: list[Material] = []
        self.currencies: list[Currency] = []
        self.emissions: list[Emission] = []

        # ---------- Operations/Tasks ----------

        self.processes: list[Process] = []
        self.storages: list[Storage] = []
        self.transits: list[Transport] = []

        # ------------Decision-Makers----------------------
        self.players: list[Player] = []
        self.couples: list[Couple] = []

    @property
    def operations(self) -> list[Process | Storage | Transport]:
        """All Operations"""
        return self.processes + self.storages + self.transits
