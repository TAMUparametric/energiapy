"""Inventory Balance for Storage 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..._core._handy._dunders import _Reprs
from ..designators.mode import X

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsStorage
    from ..._core._aliases._is_input import IsInvInput


@dataclass
class Inventory(_Reprs):
    """Inventory Balance for Storage

    Attributes:
        inventory (IsInvInput): The inventory balance.
        storage (IsStorage): The storage component.


    """

    inventory: IsInvInput = field(default=None)
    storage: IsStorage = field(default=None)

    def __post_init__(self):
        # If dictionary is given, there are dependent Resources
        # this is mostly used for material Resources
        # Hydrogen for example, may need Power to be stored
        if isinstance(self.inventory, dict):

            # The purpose of the Process is to produce the base Resource
            # The basis if set to one unit of this Resource
            # Cost inputs, for example, are scaled as per this base
            self.base = list(self.inventory)[0]

            # if Modes are given, then personalize the Modes to the Inventory Conversion
            if isinstance(self.inventory[self.base], dict):
                if not all(isinstance(i, X) for i in self.inventory[self.base]):
                    # add a dummy mode if no modes present
                    self.inventory[self.base] = {'x': self.inventory[self.base]}

                # Inventory hosts the charging an discharging conversion balances
                # Take a gander at Conversion if whats happening here is not clear
                self.conversion_c = {'resource_stg': {}}

                # iterate over modes
                for x in self.inventory[self.base]:
                    self.conversion_c['resource_stg'][x] = {
                        **{
                            res: -1 / val
                            for res, val in self.inventory[self.base][x].items()
                        },
                        **{self.base: -1},
                    }
                #'x' is a dummy mode, which can be removed here
                if self.conversion_c['resource_stg'] == 'x':

                    self.conversion_c['resource_stg'] = self.conversion_c[
                        'resource_stg'
                    ]['x']

                    del self.conversion_c['resource_stg']['x']

                self.conversion_d = {self.base: {'resource_stg': 1}}

            else:
                # This is used when a single efficiency value is given
                efficiency = self.inventory[self.base]
                self.conversion_c = {'resource_stg': {self.base: -1 / efficiency}}
                self.conversion_d = {self.base: {'resource_stg': -1}}

        else:
            # If only a Resource is given, consider 100% efficiency
            self.base = self.inventory
            self.conversion_c = {'resource_stg': {self.base: -1}}
            self.conversion_d = {self.base: {'resource_stg': -1}}

        self.name = f'Inv({self.base}, {self.storage})'
