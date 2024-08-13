"""energiapy.Resource - Resource as refined in the RT(M)N framework
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..._base._defined import _Trade

if TYPE_CHECKING:
    from ...._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class _Resource(_Trade):
    """Base Resource Class"""

    @staticmethod
    def collection():
        """The collection in System"""
        return 'resources'


@dataclass
class Resource(_Resource):

    buy: IsBoundInput = field(default=None)
    sell: IsBoundInput = field(default=None)
    ship: IsBoundInput = field(default=None)
    deliver: IsBoundInput = field(default=None)
    buy_price: IsExactInput = field(default=None)
    sell_price: IsExactInput = field(default=None)
    credit: IsExactInput = field(default=None)
    penalty: IsExactInput = field(default=None)

    # Depreciated
    varying: str = field(default=None)
    price: str = field(default=None)
    revenue: str = field(default=None)
    cons_max: str = field(default=None)
    store_max: str = field(default=None)
    store_min: str = field(default=None)

    def __post_init__(self):
        _Resource.__post_init__(self)

        # *-----------------Set ctype (ResourceType)---------------------------

        # if self.sell_cost is not None:
        #     getattr(self, 'ctypes').append(ResourceType.SELL)1
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

@dataclass
class ResourceInStorage(_Resource):
    """Stored Resource"""

    def __post_init__(self):
        _Resource.__post_init__(self)


@dataclass
class ResourceInTransit(_Resource):
    """Resource in transit"""

    def __post_init__(self):
        _Resource.__post_init__(self)


@dataclass
class ResourceLost(_Resource):
    """Resource lost"""

    def __post_init__(self):
        _Resource.__post_init__(self)
