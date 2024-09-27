"""Base for Operational Components
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, fields, field

from ...utils.scaling import scaling
from .._base._defined import _Defined


@dataclass
class _Operation(
    _Defined,
    ABC,
):
    """Base for Operational Components

    Attributes:
        capacity (IsBnd): bound on the capacity of the Operation
        land (dict): land use per Capacitate
        material (dict): material use per Capacitate
        capex (dict): capital expense per Capacitate
        opex (dict): operational expense based on Operation
        emission (dict): emission due to construction per Capacitate
    """

    operate: dict = field(default=None)
    setup: dict = field(default=None)
    dismantle: dict = field(default=None)

    operate_spend: dict = field(default=None)
    operate_earn: dict = field(default=None)
    setup_spend: dict = field(default=None)
    setup_earn: dict = field(default=None)
    dismantle_spend: dict = field(default=None)
    dismantle_earn: dict = field(default=None)

    setup_emit: dict = field(default=None)
    dismantle_emit: dict = field(default=None)

    setup_sequester: dict = field(default=None)
    dismantle_sequester: dict = field(default=None)

    setup_use: dict = field(default=None)
    dismantle_dispose: dict = field(default=None)

    consume: dict = field(default=None)
    discharge: dict = field(default=None)

    operate_lose: dict = field(default=None)
    operate_recover: dict = field(default=None)

    setup_time: dict = field(default=None)
    life_time: dict = field(default=None)
    operate_time: dict = field(default=None)
    introduce: dict = field(default=None)
    retire: dict = field(default=None)

    def __post_init__(self):
        _Defined.__post_init__(self)
        if isinstance(self.operate, list):
            self.operate = scaling(data=self.operate, how='max')
        self._balanced = False

    @staticmethod
    @abstractmethod
    def _at():
        """Spatial attributes"""

    @property
    @abstractmethod
    def balance(self):
        """Balance attribute"""

    @property
    @abstractmethod
    def resources(self):
        """Resources used in the Operation"""


    @staticmethod
    def inputs():
        """Input attributes"""
        return [
            f.name
            for f in fields(_Operate)
            + fields(_OperateTrade)
            + fields(_OperateTransact)
            + fields(_OperateLose)
            + fields(_OperateRate)
            + fields(_Setup)
            + fields(_SetupTransact)
            + fields(_SetupEmit)
            + fields(_SetupUse)
            + fields(_SetupRate)
        ]


    def locate(self):
        """Locates the Component"""
        if not getattr(self, self._at()):
            setattr(self, self._at(), getattr(self.network, self._at()))
