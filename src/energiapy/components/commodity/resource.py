"""Resource are: 
    1. converted by Processes
    2. stored by Storage
    3. transported by Transits
    4. lost by Storage and Transits
"""

from dataclasses import dataclass, fields

from .._attrs._bounds import _ResBounds
from .._attrs._exacts import _ResEmnExacts, _ResTscExacts
from ._traded import _Traded

# Associated Program Elements are:
#    Bound Parameters - BuyBound, SellBound, ShipBound
#    Exact Parameters - BuyPrice, SllPrice, SllCredit, SllPenalty, BuyEmission, SllEmission, LseEmission
#    Operational Parameters - Loss
#    Variables (Trades) - Buy, Sell, Ship
#    Variables (Transactions) - TransactBuy, TransactSell, TransactPnt, TransactCrd
#    Variables (Emissions) - BuyEmit, SellEmit, LseEmit
#    Variables (Losses) - Lose


@dataclass
class Resource(_ResBounds, _ResTscExacts, _ResEmnExacts, _Traded):
    """Resources are Produced by Processes, Stored by Storage, and Transported by Transits
    They can be bought, sold, shipped, and received by Locations or Processes

    Attributes:
        buy (IsBnd): bound on amount bought at Location or by Process
        sell (IsBnd): bound on amount sold at Location or by Process
        ship (IsBnd): bound on amount shipped through Linkage
        buy_price (IsInc): price to buy per unit basis
        sell_price (IsInc): price at which to sell per unit basis
        credit (IsExt): credit received per unit basis sold
        penalty (IsExt): penalty paid for not meeting lower bound of sell
        buy_emission (IsExt): emission per unit basis of buy
        sell_emission (IsExt): emission per unit basis of sell
        loss_emission (IsExt): emission per unit basis of loss (Storage, Transit)
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component
    """

    def __post_init__(self):
        _Traded.__post_init__(self)

    @property
    def losses(self):
        """Resource Losses"""
        return self.taskmaster.report_losses

    @staticmethod
    def inputs():
        """Input attributes"""
        return [
            f.name
            for f in fields(_ResBounds) + fields(_ResTscExacts) + fields(_ResEmnExacts)
        ]


@dataclass
class ResourceStg(Resource):
    """Resource in Inventory"""

    def __post_init__(self):
        Resource.__post_init__(self)


@dataclass
class ResourceTrn(Resource):
    """Resource in Freight"""

    def __post_init__(self):
        Resource.__post_init__(self)
