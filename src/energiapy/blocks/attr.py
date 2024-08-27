"""Attr Block 
Handles the attributes of components
Defines strict behaviour
"""

from dataclasses import dataclass, field, fields
from typing import List

from ..core._handy._dunders import _Dunders


@dataclass
class AttrBlock(_Dunders):
    """Attr Block
    Handles the attributes of components
    Defines strict behaviour

    Attributes:
        name (str): The name of the attribute block

    """

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Attr|{self.name}|'
        # Collections associated with the attribute
        self.values = []
        self.parameters = []
        self.constraints = []
        self.variables = []
        self.dispositions = []


@dataclass
class AttrCollection(_Dunders):
    """Attr is a collection of AttrBlocks

    Attributes:
        name (str): The name of the attribute collection

    """

    name: str = field(default=None)
    attrblocks: List[AttrBlock] = field(default_factory=list)

    def __post_init__(self):
        self.name = f'Attr|{self.name}|'
        # Collections associated with the attribute
        self.values = sum([attr.values for attr in self.attrblocks], [])
        self.parameters = sum([attr.parameters for attr in self.attrblocks], [])
        self.dispositions = sum([attr.dispositions for attr in self.attrblocks], [])
        self.constraints = sum([attr.constraints for attr in self.attrblocks], [])
        self.variables = sum([attr.variables for attr in self.attrblocks], [])


@dataclass
class Bounds:
    """These are Bounds for the Components

    Bounds can be different for Network and individual Spatial Components

    """

    def __post_init__(self):
        # Player
        self.has = AttrBlock(name='has')
        self.needs = AttrBlock(name='needs')
        # Cash
        self.spend = AttrBlock(name='spend')
        self.earn = AttrBlock(name='earn')
        # Emission
        self.emit = AttrBlock(name='emit')
        # Land and Material (Used)
        self.use = AttrBlock(name='use')
        # Resource
        self.buy = AttrBlock(name='buy')
        self.sell = AttrBlock(name='sell')
        self.ship = AttrBlock(name='ship')
        # Operational
        self.capacity = AttrBlock(name='capacity')
        self.operate = AttrBlock(name='operate')


@dataclass
class Exacts:
    """These are Exact Component Inputs

    These are inherited across all Spatial Components
    if defined at Network

    There is no Network value for these

    """

    def __post_init__(self):
        # Land and Material (Used)
        self.cost = AttrBlock(name='cost')
        # Resource
        self.buy_price = AttrBlock(name='buy_price')
        self.sell_price = AttrBlock(name='sell_price')
        self.credit = AttrBlock(name='credit')
        self.penalty = AttrBlock(name='penalty')
        self.buy_emission = AttrBlock(name='buy_emission')
        self.sell_emission = AttrBlock(name='sell_emission')
        self.loss_emission = AttrBlock(name='loss_emission')
        # Operational
        self.land = AttrBlock(name='land')
        self.material = AttrBlock(name='material')
        self.capex = AttrBlock(name='capex')
        self.opex = AttrBlock(name='opex')
        self.emission = AttrBlock(name='emission')


@dataclass
class BoundsRes:
    """These are Bounds for Resources
    defined at Operational Components
    """

    def __post_init__(self):

        # Process
        self.buy = AttrBlock(name='buy')
        self.sell = AttrBlock(name='sell')
        # Transit
        self.ship = AttrBlock(name='ship')


@dataclass
class ExactRes:
    """These are Exact Resource Inputs
    defined at Operational Components
    """

    def __post_init__(self):

        # Process
        self.buy_price = AttrBlock(name='buy_price')
        self.sell_price = AttrBlock(name='sell_price')
        self.credit = AttrBlock(name='credit')
        self.penalty = AttrBlock(name='penalty')


@dataclass
class Balances:
    """These are Balances for Resources
    defined at Operational Components
    """

    def __post_init__(self):

        # Process
        self.conversion = AttrBlock(name='conversion')
        # Storage
        self.inventory = AttrBlock(name='inventory')
        # Transit
        self.freight = AttrBlock(name='freight')


@dataclass
class Attr(Bounds, Exacts, BoundsRes, ExactRes, Balances, _Dunders):
    """This object collects all the attributes defined
    and makes a list of Dispositions they are defined at

    """

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Attr|{self.name}|'
        Bounds.__post_init__(self)
        Exacts.__post_init__(self)
        BoundsRes.__post_init__(self)
        ExactRes.__post_init__(self)
        Balances.__post_init__(self)

    @staticmethod
    def bounds():
        """Returns all Bounds"""
        return fields(Bounds) + fields(BoundsRes)

    @staticmethod
    def exacts():
        """Returns all Exacts"""
        return fields(Exacts) + fields(ExactRes)

    @staticmethod
    def balances():
        """Returns all Balances"""
        return fields(Balances)

    @property
    def expenses(self):
        """Expenses"""
        return AttrCollection(
            name='expenses',
            attrblocks=[
                self.capex,
                self.opex,
                self.buy_price,
                self.sell_price,
                self.credit,
                self.penalty,
                self.cost,
            ],
        )

    @property
    def emissions(self):
        """Emissions"""
        return AttrCollection(
            name='emissions',
            attrblocks=[
                self.buy_emission,
                self.sell_emission,
                self.loss_emission,
                self.emission,
            ],
        )

    @property
    def lnduses(self):
        """Land Uses"""
        return AttrCollection(name='lnduses', attrblocks=[self.land])

    @property
    def matuses(self):
        """Material Uses"""
        return AttrCollection(name='matuses', attrblocks=[self.material])
