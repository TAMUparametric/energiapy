"""These are methods that are common to all Component dataclasses
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..core.balance import OpnMatUse
from ..core.base import Base
from ..core.cashflow import OpnCashFlow, SptCashFlow
from ..core.detail import CmpDetail
from ..core.emission import CmdEmission, OpnEmission, SptEmissionCap
from ..core.handle import HandleAspect
from ..core.land import OpnLand, SptLand
from ..core.life import OpnLife
from ..core.limit import OpnLimit
from ..core.onset import CmpInit, EmtCol

if TYPE_CHECKING:
    from ..type.alias import IsComponent, IsValue
    from .horizon import Horizon


@dataclass
class Temporal(Base):
    """Temporal describes time 
    Scale, Horizon are special cases of Temporal
    """
    _temporal = True


@dataclass
class Component(CmpInit, CmpDetail, EmtCol, HandleAspect, Base):
    """Most energiapy components are inherited from this.
    Some like Horizon, Scale, Scenario only take a subset of the methods 
    """

    def __post_init__(self):
        CmpInit.__post_init__(self)
        EmtCol.__post_init__(self)
        self._component = True


@dataclass
class Commodity(CmdEmission, Component):
    """A Commodity is a good or service that is produced, consumed, or traded in the model.
    Resource and Material are special cases of Commodity.
    """

    def __post_init__(self):
        Component.__post_init__(self)
        self._commodity = True
        self._members = ['Resource', 'Material']


@dataclass
class Operation(OpnLimit, OpnMatUse, OpnCashFlow, OpnEmission, OpnLand, OpnLife, Component):
    """An Operation is a process that transforms commodities.
    Process, Storage, and Transit are special cases of Operation. 
    """

    def __post_init__(self):
        Component.__post_init__(self)
        OpnMatUse.__post_init__(self)
        self._operation = True
        self._members = ['Process', 'Storage', 'Transit']


@dataclass
class Spatial(SptCashFlow, SptLand, SptEmissionCap, Component):
    """Spatial is a location where operations are performed.
    Location, Linkage, Network are special cases of Spatial.
    """

    def __post_init__(self):
        Component.__post_init__(self)
        self._spatial = True
