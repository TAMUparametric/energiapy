"""Inventory Balance for Storage 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from ..designators.mode import X

from ..._core._handy._dunders import _Reprs

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsStorage, IsResource
    from ..._core._aliases._is_input import IsInvInput


@dataclass
class Inventory(_Reprs):
    """Inventory Balance for Storage"""

    inventory: IsInvInput = field(default=None)
    storage: IsStorage = field(default=None)

    def __post_init__(self):

        if isinstance(self.inventory, dict):
            self.base = list(self.inventory)[0]

            if isinstance(self.inventory[self.base], dict):
                if not all(isinstance(i, X) for i in self.inventory[self.base]):
                    self.inventory[self.base] = {'x': self.inventory[self.base]}

                self.conversion_c = {'resource_stg': {}}
                for x in self.inventory[self.base]:
                    print(self.inventory[self.base][x])
                    self.conversion_c['resource_stg'][x] = {
                        **{i: -1 / j for i, j in self.inventory[self.base][x].items()},
                        **{self.base: -1},
                    }

                if self.conversion_c['resource_stg'] == 'x':

                    self.conversion_c['resource_stg'] = self.conversion_c[
                        'resource_stg'
                    ]['x']

                    del self.conversion_c['resource_stg']['x']

                self.conversion_d = {self.base: {'resource_stg': 1}}

            else:
                efficiency = self.inventory[self.base]
                self.conversion_c = {'resource_stg': {self.base: -1 / efficiency}}
                self.conversion_d = {self.base: {'resource_stg': -1}}

        else:
            self.base = self.inventory
            self.conversion_c = {'resource_stg': {self.base: -1}}
            self.conversion_d = {self.base: {'resource_stg': -1}}
