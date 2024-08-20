"""Resource are: 
    1. converted by Processes
    2. stored by Storage
    3. transported by Transits
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ._commodity import _Traded

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class Resource(_Traded):
    """Resources are Produced by Processes, Stored by Storage, and Transported by Transits
    They can be bought, sold, shipped, and received by Locations or Processes

    Attributes:
        buy (IsBoundInput): bound on amount bought at Location or by Process
        sell (IsBoundInput): bound on amount sold at Location or by Process
        ship (IsBoundInput): bound on amount shipped from Location
        receive (IsBoundInput): bound on amount received by Location
        buy_price (IsExactInput): price to buy per unit basis
        sell_price (IsExactInput): price at which to sell per unit basis
        credit (IsExactInput): credit received per unit basis sold
        penalty (IsExactInput): penalty paid for not meeting lower bound of sell
        buy_emission (IsExactInput): emission per unit basis of buy
        sell_emission (IsExactInput): emission per unit basis of sell
        loss_emission (IsExactInput): emission per unit basis of loss (Storage, Transit)
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component
    """

    buy: IsBoundInput = field(default=None)
    sell: IsBoundInput = field(default=None)
    ship: IsBoundInput = field(default=None)
    receive: IsBoundInput = field(default=None)
    buy_price: IsExactInput = field(default=None)
    sell_price: IsExactInput = field(default=None)
    credit: IsExactInput = field(default=None)
    penalty: IsExactInput = field(default=None)
    buy_emission: IsExactInput = field(default=None)
    sell_emission: IsExactInput = field(default=None)
    loss_emission: IsExactInput = field(default=None)

    # Depreciated
    varying: str = field(default=None)
    price: str = field(default=None)
    revenue: str = field(default=None)
    cons_max: str = field(default=None)
    store_max: str = field(default=None)
    store_min: str = field(default=None)

    def __post_init__(self):
        _Traded.__post_init__(self)

        # Depreciation Warnings
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

    @classmethod
    def bounds(cls):
        """Attrs that quantify the bounds of the Component"""
        return ['buy', 'sell', 'ship', 'receive']

    @classmethod
    def expenses(cls):
        """Attrs that determine expenses of the component"""
        return ['buy_price', 'sell_price', 'credit', 'penalty']

    @classmethod
    def emitted(cls):
        """Attrs that determine emissions of the component"""
        return ['buy_emission', 'sell_emission', 'loss_emission']

    @classmethod
    def inputs(cls):
        """Attrs"""
        return cls.bounds() + cls.expenses() + cls.emitted()

    @classmethod
    def _csh_inputs(cls):
        """Adds Cash when making consistent"""
        return cls.expenses()

    @classmethod
    def _nstd_inputs(cls):
        """Is a nested input to be made consistent"""
        return cls.emitted()


@dataclass
class ResourceStg(Resource):
    """Stored Resource"""

    def __post_init__(self):
        Resource.__post_init__(self)


@dataclass
class ResourceTrn(Resource):
    """Resource in transit"""

    def __post_init__(self):
        Resource.__post_init__(self)


