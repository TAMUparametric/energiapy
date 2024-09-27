"""Resource are: 
    1. converted by Processes
    2. stored by Storage
    3. transported by Transits
    4. lost by Storage and Transits
"""

from dataclasses import dataclass, fields, field


from ._commodity import _Commodity


@dataclass
class Resource(_Commodity):
    """Resources are Produced by Processes, Stored by Storage, and Transported by Transits
    They can be bought, sold, shipped, and received by Locations or Processes

    Attributes:
        buy (IsBnd): bound on amount bought at Location or by Process
        sell (IsBnd): bound on amount sold at Location or by Process
        ship (IsBnd): bound on amount shipped through Linkage
        buy_price (dict): price to buy per unit basis
        sell_price (dict): price at which to sell per unit basis
        credit (dict): credit received per unit basis sold
        penalty (dict): penalty paid for not meeting lower bound of sell
        buy_emission (dict): emission per unit basis of buy
        sell_emission (dict): emission per unit basis of sell
        loss_emission (dict): emission per unit basis of loss (Storage, Transit)
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component
    """

    # Intra-player trade
    buy: dict = field(default=None)
    buy_spend: dict = field(default=None)
    buy_earn: dict = field(default=None)
    buy_emit: dict = field(default=None)
    buy_seq: dict = field(default=None)

    sell: dict = field(default=None)
    sell_earn: dict = field(default=None)
    sell_emit: dict = field(default=None)
    sell_spend: dict = field(default=None)
    sell_seq: dict = field(default=None)

    # Intra-Location Trade (through Linkage)
    # Linkages go in one direction
    receive: dict = field(default=None)
    ship: dict = field(default=None)

    # Setup and Disposal for Operations
    use: dict = field(default=None)
    use_spend: dict = field(default=None)
    use_earn: dict = field(default=None)
    use_emit: dict = field(default=None)
    use_seq: dict = field(default=None)

    dispose: dict = field(default=None)
    dispose_spend: dict = field(default=None)
    dispose_earn: dict = field(default=None)
    dispose_emit: dict = field(default=None)
    dispose_seq: dict = field(default=None)

    # Lose and Recover at Location or between Linkage through Storage or Transit
    lose: dict = field(default=None)
    recover: dict = field(default=None)
    lose_emit: dict = field(default=None)
    recover_sequester: dict = field(default=None)

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


@dataclass
class ResourcePrd(Resource):
    """Resource Produced"""

    def __post_init__(self):
        Resource.__post_init__(self)
