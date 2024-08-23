"""Inventory Balance for Storage 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ._balance import _Balance

if TYPE_CHECKING:
    from ...core.aliases.is_component import IsStorage
    from ...core.aliases.is_input import IsBalInput


@dataclass
class Inventory(_Balance):
    """Inventory Balance for Storage

    Attributes:
        inventory (IsBalInput): The inventory balance.
        storage (IsStorage): The storage component.
    """

    inventory: IsBalInput = field(default=None)
    storage: IsStorage = field(default=None)

    def __post_init__(self):
        _Balance.__post_init__(self)

    @property
    def balance(self):
        """Returns the Inventory balance"""
        return self.inventory

    @property
    def operation(self):
        """Returns the Storage component"""
        return self.storage

    @property
    def conversion_c(self):
        """Charging conversion
        Returns input conversion
        """
        return self.conversion_in

    @property
    def conversion_d(self):
        """Discharging conversion
        Returns output conversion
        """
        return self.conversion_out
