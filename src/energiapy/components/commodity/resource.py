"""energiapy.Resource - Resource as refined in the RT(M)N framework
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...core.capbound import ResCapBound
from ...core.cashflow import ResCashFlow
from ...core.limit import ResLimit
from ...inputs.input_map import input_map
from ...type.component.resource import ResourceType
from ..component import Commodity

if TYPE_CHECKING:
    from ...type.alias import IsDepreciated, IsLimit


@dataclass
class Resource(ResCashFlow, ResLimit, ResCapBound, Commodity):
    # Depreciated
    sell: IsDepreciated = field(default=None)
    varying: IsDepreciated = field(default=None)
    price: IsDepreciated = field(default=None)
    revenue: IsDepreciated = field(default=None)
    cons_max: IsDepreciated = field(default=None)
    store_max: IsDepreciated = field(default=None)
    store_min: IsDepreciated = field(default=None)

    def __post_init__(self):

        ResCapBound.__post_init__(self)
        Commodity.__post_init__(self)
        # *-----------------Set ctype (ResourceType)---------------------------------

        if self.sell_cost is not None:
            getattr(self, 'ctypes').append(ResourceType.SELL)
            if self.discharge is None:
                self.discharge = True

        if self.discharge is not None:
            getattr(self, 'ctypes').append(ResourceType.DISCHARGE)

        if self.consume is not None:
            getattr(self, 'ctypes').append(ResourceType.CONSUME)

        if self.purchase_cost:
            getattr(self, 'ctypes').append(ResourceType.PURCHASE)
            if self.consume is None:
                self.consume = True
        # TODO update store, produce, transport

        # *----------------- Depreciation Warnings---------------------------------
        _name = getattr(self, 'name', None)
        _changed = {'store_max': 'store', 'store_min': 'store', 'cons_max': 'consume',
                    'sell': 'discharge and sell_cost', 'price': 'purchase_cost', 'revenue': 'sell_cost'}

        for i, j in _changed.items():
            if getattr(self, i):
                raise ValueError(
                    f'{_name}: {i} is depreciated. Please use {j} instead')

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if self.is_ready(attr_value=value):
            if input_map.is_component_aspect(attr=name, component='resource'):
                self.make_aspect(attr_name=name, attr_value=value)
