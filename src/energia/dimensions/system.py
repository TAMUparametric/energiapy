"""System"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .._core._dimension import _Dimension

if TYPE_CHECKING:
    from ..components.commodities.currency import Currency
    from ..components.commodities.emission import Emission
    from ..components.commodities.land import Land
    from ..components.commodities.material import Material
    from ..components.commodities.resource import Resource
    from ..components.operations.process import Process
    from ..components.operations.storage import Storage
    from ..components.operations.transport import Transport


@dataclass
class System(_Dimension):
    """
    System representation as a Resource Task Network (RTN)
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
    """

    def __post_init__(self):
        # -------Commodities/Resources ----------

        self.resources: list[Resource] = []
        self.lands: list[Land] = []
        self.materials: list[Material] = []
        self.currencies: list[Currency] = []
        self.emissions: list[Emission] = []

        # -------Operations/Tasks ----------

        self.processes: list[Process] = []
        self.storages: list[Storage] = []
        self.transports: list[Transport] = []

        _Dimension.__post_init__(self)

    @property
    def operations(self) -> list[Process | Storage | Transport]:
        """All Operations"""
        return self.processes + self.storages + self.transports
