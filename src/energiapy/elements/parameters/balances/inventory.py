"""Inventory Balance for Storage 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ....core.isalias.inps.isblc import IsBlc
from ._balance import _Balance

if TYPE_CHECKING:
    from ....components.operation.storage import Storage


@dataclass
class Inventory(_Balance):
    """Inventory Balance for Storage

    Attributes:
        inventory (IsBlc): The inventory balance.
        storage (IsStorage): The storage component.
    """

    inventory: IsBlc = field(default=None)
    storage: Storage = field(default=None)

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
