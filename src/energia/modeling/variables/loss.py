"""Loss Variable"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .aspect import Aspect

if TYPE_CHECKING:
    from ..indices.domain import Domain


@dataclass
class Loss(Aspect):
    """Loss Entails the degradation of a state
    In the case of Capacity, it is the loss of capacity
    In the case of Inventory, it is the loss of inventory
    Unlike Dismantle, loss is not a decision
    """

    def update(self, domain: Domain, reporting: bool = False):
        """Add a domain to the decision variable"""
        # Write a mapping constraint
        self.Map(domain=domain, reporting=reporting)
