"""Base for Operational Components
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, fields

from pandas import DataFrame

from ...utils.scaling import scaling
from .._attrs._boundbounds import _Operate
from .._attrs._bounds import _Setup
from .._attrs._exacts import (
    _OperateLose,
    _OperateTrade,
    _OperateTransact,
    _SetupEmit,
    _SetupTransact,
    _SetupUse,
)
from .._attrs._rates import _OperateRate, _SetupRate
from .._base._defined import _Defined


@dataclass
class _Operation(
    _Operate,
    _Setup,
    _OperateTransact,
    _OperateRate,
    _OperateLose,
    _SetupTransact,
    _SetupRate,
    _SetupEmit,
    _SetupUse,
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

    def __post_init__(self):
        _Defined.__post_init__(self)
        if isinstance(self.operate, DataFrame):
            self.operate = scaling(data=self.operate, how='max')
        self._balanced = False

    @staticmethod
    @abstractmethod
    def _at():
        """At what Spatial can the Operation be located"""

    @property
    @abstractmethod
    def spatials(self):
        """Spatial attributes"""

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
        
        #
        if not self.spatials:
            self.spatials = self.network.locations
