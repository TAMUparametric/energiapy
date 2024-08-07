"""energiapy.Resource - Resource as refined in the RT(M)N framework
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .._component import _Commodity

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsExactInput, IsBoundInput


@dataclass
class Resource(_Commodity):

    buy: IsBoundInput = field(default=None)
    sell: IsBoundInput = field(default=None)
    ship: IsBoundInput = field(default=None)
    deliver: IsBoundInput = field(default=None)
    buy_price: IsExactInput = field(default=None)
    sell_price: IsExactInput = field(default=None)

    # Depreciated
    varying: str = field(default=None)
    price: str = field(default=None)
    revenue: str = field(default=None)
    cons_max: str = field(default=None)
    store_max: str = field(default=None)
    store_min: str = field(default=None)

    def __post_init__(self):
        _Commodity.__post_init__(self)

        # *-----------------Set ctype (ResourceType)---------------------------------

        # if self.sell_cost is not None:
        #     getattr(self, 'ctypes').append(ResourceType.SELL)
        #     if self.discharge is None:
        #         self.discharge = True

        # if self.discharge is not None:
        #     getattr(self, 'ctypes').append(ResourceType.DISCHARGE)

        # if self.consume is not None:
        #     getattr(self, 'ctypes').append(ResourceType.CONSUME)

        # if self.purchase_cost:
        #     getattr(self, 'ctypes').append(ResourceType.PURCHASE)
        #     if self.consume is None:
        #         self.consume = True
        # TODO update store, produce, transport

        # *Depreciation Warnings
        _name = getattr(self, 'name', None)
        _changed = {
            'store_max': 'store',
            'store_min': 'store',
            'cons_max': 'consume',
            'price': 'purchase_cost',
            'revenue': 'sell_cost',
        }

        for i, j in _changed.items():
            # If the attribute i is depreciated raise ValueError.
            if getattr(self, i):
                raise ValueError(f'{_name}: {i} is depreciated. Please use {j} instead')

    @property
    def _commodity(self):
        return self

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'resources'

    # def __setattr__(self, name, value):
    #     super().__setattr__(name, value)
    #     if self.is_ready(attr_value=value):
    #         if input_map.is_component_aspect(attr=name, component='resource'):
    #             self.make_aspect(attr_name=name, attr_value=value)
