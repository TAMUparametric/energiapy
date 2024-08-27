"""Attr Block 
Handles the attributes of components
Defines strict behaviour
"""

from dataclasses import dataclass, field, fields

from ..core._handy._dunders import _Dunders


@dataclass
class Bounds:
    """These are Bounds for the Components

    Bounds can be different for Network and individual Spatial Components

    """

    # Player
    has: list = field(default_factory=list)
    needs: list = field(default_factory=list)
    # Cash
    spend: list = field(default_factory=list)
    earn: list = field(default_factory=list)
    # Emission
    emit: list = field(default_factory=list)
    # Land and Material (Used)
    use: list = field(default_factory=list)
    # Resource
    buy: list = field(default_factory=list)
    sell: list = field(default_factory=list)
    ship: list = field(default_factory=list)
    # Operational
    capacity: list = field(default_factory=list)
    # Process
    produce: list = field(default_factory=list)
    # Storage
    capacity_c: list = field(default_factory=list)
    capacity_d: list = field(default_factory=list)
    store: list = field(default_factory=list)
    # Transit
    transport: list = field(default_factory=list)


@dataclass
class Collects:
    """These are at the root Component and collect
    the values defined at other Components
    """

    # Cash
    expenses: list = field(default_factory=list)
    # Emission
    emits: list = field(default_factory=list)
    # Land
    lands: list = field(default_factory=list)


@dataclass
class Exacts:
    """These are Exact Component Inputs

    These are inherited across all Spatial Components
    if defined at Network

    There is no Network value for these

    """

    # Land and Material (Used)
    cost: list = field(default_factory=list)
    emission: list = field(default_factory=list)
    # Resource
    buy_price: list = field(default_factory=list)
    sell_price: list = field(default_factory=list)
    credit: list = field(default_factory=list)
    penalty: list = field(default_factory=list)
    buy_emission: list = field(default_factory=list)
    sell_emission: list = field(default_factory=list)
    loss_emission: list = field(default_factory=list)
    # Operational
    land: list = field(default_factory=list)
    material: list = field(default_factory=list)
    capex: list = field(default_factory=list)
    opex: list = field(default_factory=list)
    emission: list = field(default_factory=list)


@dataclass
class BoundsRes:
    """These are Bounds for Resources
    defined at Operational Components
    """

    # Process
    buy: list = field(default_factory=list)
    sell: list = field(default_factory=list)
    # Transit
    ship: list = field(default_factory=list)


@dataclass
class ExactRes:
    """These are Exact Resource Inputs
    defined at Operational Components
    """

    # Process
    buy_price: list = field(default_factory=list)
    sell_price: list = field(default_factory=list)
    credit: list = field(default_factory=list)
    penalty: list = field(default_factory=list)


@dataclass
class Balances:
    """These are Balances for Resources
    defined at Operational Components
    """

    # Process
    conversion: list = field(default_factory=list)
    # Storage
    inventory: list = field(default_factory=list)
    # Transit
    freight: list = field(default_factory=list)


@dataclass
class Attr(Bounds, Collects, Exacts, BoundsRes, ExactRes, Balances, _Dunders):
    """This object collects all the attributes defined
    and makes a list of Dispositions they are defined at

    """

    name: str = field(default=None)

    def __post_init__(self):

        self.name = f'Attr|{self.name}|'

    @staticmethod
    def bounds():
        """Returns all Bounds"""
        return fields(Bounds) + fields(BoundsRes)

    @staticmethod
    def collects():
        """Returns all Collects"""
        return fields(Collects)

    @staticmethod
    def exacts():
        """Returns all Exacts"""
        return fields(Exacts) + fields(ExactRes)

    @staticmethod
    def balances():
        """Returns all Balances"""
        return fields(Balances)
