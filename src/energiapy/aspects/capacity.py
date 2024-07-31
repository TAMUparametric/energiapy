from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .aspect import Aspect

if TYPE_CHECKING:
    from ...type.alias import (IsCapacity, IsLinkage, IsLocation, IsOperation,
                               IsProcess, IsSpatial, IsStorage, IsTransit)


@dataclass
class Capacity(Aspect):
    """Capacity

    Args:
        bound (IsBound): bound 
        operation (IsOperation): of Operation
        spatial (IsSpatial): at Spatial
    """
    capacity: IsCapacity = field(default=None)
    operation: IsOperation = field(default=None)
    spatial: IsSpatial = field(default=None)

    @property
    def _of(self):
        return self.operation

    @property
    def _at(self):
        return self.spatial
