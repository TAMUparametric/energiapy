"""Base for Operational Components
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, fields, field

from ...utils.scaling import scaling
from .._attrs._boundbounds import _Operate

)
from .._attrs._rates import _OperateRate, _SetupRate
from .._base._defined import _Defined


@dataclass
class _Operation(
    _Operate,
    _OperateRate,
    _Defined,
    ABC,
):
    """Base for Operational Components

    Attributes:
        capacity (IsBnd): bound on the capacity of the Operation
        land (IsExt): land use per Capacitate
        material (IsExt): material use per Capacitate
        capex (IsExt): capital expense per Capacitate
        opex (IsExt): operational expense based on Operation
        emission (IsExt): emission due to construction per Capacitate
    """

    setup: dict = field(default=None)
    dismantle: dict = field(default=None)

    setup_spend: IsInc = field(default=None)
    setup_earn: IsInc = field(default=None)
    dismantle_spend: IsInc = field(default=None)
    dismantle_earn: IsInc = field(default=None)
    setup_emit: IsExt = field(default=None)
    dismantle_emit: IsExt = field(default=None)
    setup_sequester: IsExt = field(default=None)
    dismantle_sequester: IsExt = field(default=None)
    setup_use: IsExt = field(default=None)
    dismantle_dispose: IsExt = field(default=None)
    consume: IsInc = field(default=None)
    discharge: IsInc = field(default=None)
    operate_spend: IsInc = field(default=None)
    operate_earn: IsInc = field(default=None)
    operate_lose: IsExt = field(default=None)
    operate_recover: IsExt = field(default=None)
    setup_time: IsExt = field(default=None)
    life_time: IsExt = field(default=None)
    introduce: IsExt = field(default=None)
    retire: IsExt = field(default=None)
    operate_time: IsExt = field(default=None)

    

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

    @property
    def emissions(self):
        """Emissions from the Operation"""
        if self.setup_emit:
            return [i.index.emn for i in self.setup_emit.data.values()]
        else:
            return []

    @property
    def commodities(self):
        """Commodities used in the Operation"""
        return self.emissions + self.resources + self.system.cashes + self.system.lands

    def locate(self):
        """Locates the Component"""
        if not getattr(self, self._at()):
            setattr(self, self._at(), getattr(self.network, self._at()))
