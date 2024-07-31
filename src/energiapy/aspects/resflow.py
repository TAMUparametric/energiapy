from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .aspect import Aspect

if TYPE_CHECKING:
    from ...type.alias import IsLocation, IsProcess, IsResFlow, IsResource


@dataclass
class ResFlow(Aspect):
    """Flow  

    Args:
        resource (IsResource): of Resource 
        operation (IsOperation): from Operation
        spatial (IsSpatial): at Spatial 
    """
    resource: IsResource = field(default=None)
    process: IsProcess = field(default=None)
    location: IsLocation = field(default=None)

    @property
    def _of(self):
        return self.resource

    @property
    def _from(self):
        return self.process

    @property
    def _at(self):
        return self.location


@dataclass
class Discharge(ResFlow):
    """Discharge Resource Flow 
    """
    


@dataclass
class Consume(ResFlow):
    """Consume Resource Flow
    """
