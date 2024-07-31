from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..component import Commodity

if TYPE_CHECKING:
    from ...type.alias import IsDepreciated, IsLimit


@dataclass
class Derived(Commodity):
    """Derived from the behavior of another Component
    """
    @property
    def _derived(self):
        return True


@dataclass
class Cash(Derived):
    """Cash derived from:
        Resource Consume and Discharge
        Operation Capacity
        Process Produce
        Storage Store
        Transit Transport    
    """


@dataclass
class Emission(Derived):
    """Emission derived from:
        Resource Consume and Discharge
        Material Use
        Operation Capacity
    """


@dataclass
class Land(Derived):
    """Land derived from Operation Capacity
    """
