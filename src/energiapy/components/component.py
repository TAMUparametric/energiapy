"""These are methods that are common to all Component dataclasses
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..core.balance import OpnMatUse
from ..core.base import Base
from ..core.cashflow import OpnCashFlow, SpcCashFlow
from ..core.detail import CompDetail
from ..core.emission import CmdEmission, OpnEmission, SpcEmissionCap
from ..core.handle import HandleAspect
from ..core.land import OpnLand, SpcLand
from ..core.life import OpnLife
from ..core.limit import OpnLimit
from ..core.onset import CompInit, ElementCol

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
class Component(CompInit, CompDetail, ElementCol, HandleAspect, Base):
    """Most energiapy components are inherited from this.
    Some like Horizon, Scale, Scenario only take a subset of the methods 
    """

    def __post_init__(self):
        CompInit.__post_init__(self)
        ElementCol.__post_init__(self)
        self._component = True


@dataclass
class Commodity(CmdEmission, Component):
    """A Commodity is a good or service that is produced, consumed, or traded in the model.
    Resource and Material are special cases of Commodity.
    """

    def __post_init__(self):
        Component.__post_init__(self)
        self._commodity = True


@dataclass
class Operation(OpnLimit, OpnMatUse, OpnCashFlow, OpnEmission, OpnLand, OpnLife, Component):
    """An Operation is a process that transforms commodities.
    Process, Storage, and Transport are special cases of Operation. 
    """

    def __post_init__(self):
        Component.__post_init__(self)
        OpnMatUse.__post_init__(self)
        self._operation = True


@dataclass
class Spatial(SpcCashFlow, SpcLand, SpcEmissionCap, Component):
    """Spatial is a location where operations are performed.
    Location, Linkage, Network are special cases of Spatial.
    """

    def __post_init__(self):
        Component.__post_init__(self)
        self._spatial = True
