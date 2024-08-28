"""Resource are: 
    1. converted by Processes
    2. stored by Storage
    3. transported by Transits
"""

from dataclasses import dataclass, field, fields

from ._commodity import _Traded
from ...attrs.bounds import ResBounds
from ...attrs.exacts import ResExpExacts, ResEmnExacts


@dataclass
class Resource(ResBounds, ResExpExacts, ResEmnExacts, _Traded):
    """Resources are Produced by Processes, Stored by Storage, and Transported by Transits
    They can be bought, sold, shipped, and received by Locations or Processes

    Attributes:
        buy (IsBoundInput): bound on amount bought at Location or by Process
        sell (IsBoundInput): bound on amount sold at Location or by Process
        ship (IsBoundInput): bound on amount shipped through Linkage
        price_buy (IsExactInput): price to buy per unit basis
        price_sell (IsExactInput): price at which to sell per unit basis
        credit (IsExactInput): credit received per unit basis sold
        penalty (IsExactInput): penalty paid for not meeting lower bound of sell
        emission_buy (IsExactInput): emission per unit basis of buy
        emission_sell (IsExactInput): emission per unit basis of sell
        emission_loss (IsExactInput): emission per unit basis of loss (Storage, Transit)
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component
    """

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

    @property
    def losses(self):
        """Resource Losses"""
        return self.taskmaster.report_losses

    @staticmethod
    def inputs():
        """Input attributes"""
        return [
            f.name
            for f in fields(ResBounds) + fields(ResExpExacts) + fields(ResEmnExacts)
        ]


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
