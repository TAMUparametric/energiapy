"""Resource are: 
    1. converted by Processes
    2. stored by Storage
    3. transported by Transits
    4. lost by Storage and Transits
"""

from dataclasses import dataclass, fields

from .._attrs._bounds import _Trade, _Use
from .._attrs._exacts import _TradeTransact, _TradeEmit, _UseTransact, _UseEmit
from ._commodity import _Commodity


@dataclass
class Resource(
    _Commodity, _Trade, _Use, _TradeTransact, _TradeEmit, _UseTransact, _UseEmit
):
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
        _Commodity.__post_init__(self)

    @property
    def losses(self):
        """Resource Losses"""
        return self.taskmaster.report_lose

    @staticmethod
    def inputs():
        """Input attributes"""
        return [
            f.name
            for f in fields(_Trade)
            + fields(_Use)
            + fields(_TradeTransact)
            + fields(_TradeEmit)
            + fields(_UseTransact)
            + fields(_UseEmit)
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
