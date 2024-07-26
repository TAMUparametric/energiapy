"""energiapy.Resource - Resource as refined in the RT(M)N framework
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...type.component.resource import ResourceType
from ...type.element.aspect import Aspects
from ...type.element.input import Input
from ..component import Component

if TYPE_CHECKING:
    from ...type.alias import (IsCashFlow, IsDepreciated, IsDetail, IsEmission,
                               IsLimit)
    from ..temporal.horizon import Horizon


@dataclass
class Resource(Component):
    # Limit Aspect
    discharge: IsLimit = field(default=None)
    consume: IsLimit = field(default=None)
    # CashFlowType
    sell_cost: IsCashFlow = field(default=None)
    purchase_cost: IsCashFlow = field(default=None)
    credit: IsCashFlow = field(default=None)
    penalty: IsCashFlow = field(default=None)
    # EmissionType
    gwp: IsEmission = field(default=None)
    odp: IsEmission = field(default=None)
    acid: IsEmission = field(default=None)
    eutt: IsEmission = field(default=None)
    eutf: IsEmission = field(default=None)
    eutm: IsEmission = field(default=None)
    # Details
    basis: IsDetail = field(default=None)
    block: IsDetail = field(default=None)
    label: IsDetail = field(default=None)
    citation: IsDetail = field(default=None)
    # Depreciated
    sell: IsDepreciated = field(default=None)
    varying: IsDepreciated = field(default=None)
    price: IsDepreciated = field(default=None)
    revenue: IsDepreciated = field(default=None)
    cons_max: IsDepreciated = field(default=None)
    store_max: IsDepreciated = field(default=None)
    store_min: IsDepreciated = field(default=None)

    def __post_init__(self):
        super().__post_init__()
        # set at Process, Storage, Transport respectively
        self.produce, self.store, self.transport = (None for _ in range(3))

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
            if Input.match(name) in self.aspects():
                self.make_aspect(attr_name=name, attr_value=value)

    @ staticmethod
    def aspects() -> list:
        """Returns Resource aspects
        """
        return Aspects.resource
