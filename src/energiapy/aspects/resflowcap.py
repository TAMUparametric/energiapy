from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .aspect import Aspect

if TYPE_CHECKING:
    from ...type.alias import IsOperation, IsResFlowCap, IsResource, IsSpatial


@dataclass
class ResFlowCap(Aspect):
    """Operation capacity bounded flow - 

    Args:
        resource (IsResource): of Resource 
    """
    resource: IsResource = field(default=None)
    operation: IsOperation = field(default=None)
    spatial: IsSpatial = field(default=None)

    @property
    def _of(self):
        return self.resource

    @property
    def _from(self):
        return self.operation

    @property
    def _at(self):
        return self.spatial


@dataclass
class Produce(ResFlowCap):
    """For Process
    """


@dataclass
class Store(ResFlowCap):
    """For Storage
    """


@dataclass
class Transport(ResFlowCap):
    """For Transit
    """
