"""energiapy.components.parameters.paramtype - 

These are enums for the type and subtypes of parameters

Each parameter has a spatiotemporal disposition 
spatial: SpatialDisposition is determined from the Component where the parameter is defined
temporal: TemporalDisposition needs to be provided using the _scale attributes

The parameter could either certain or uncertain (vtype: VariabilityType)
vtypes have substypes:
Certainty subtypes are either some combination of bounds or an exact value
Uncertainty subtypes are parametric, deterministic, stochastic

Special parameters are actual dataclasses: BigM, SmallM, Factor, MPVar/Theta

Finally, 
ptype: ParameterType describes what the parameter models. There are subtypes for each type.
"""

from enum import Enum, auto
from typing import List


class Property(Enum):
    """What kind of behaviour does the parameter describe
    All of these have subclasses
    These are predetermined by me, Rahul Kakodkar. 
    The BDFO of energiapy
    """
    LIMIT = auto()
    """Helps create boundaries for the problem 
    by setting a min/max or exact limit for flow of Resource.
    """
    CASHFLOW = auto()
    """Expenditure/Revenue.
    """
    LAND = auto()
    """Describes land use and such
    """
    EMISSION = auto()
    """Is an emission.
    """
    LIFE = auto()
    """Describes earliest introduction, retirement, lifetime and such
    """
    LOSS = auto()
    """Amount lost during storage or transport
    """


class Limit(Enum):
    """What Resource flow is being limited 
    at some spatiotemporal disposition 
    """
    DISCHARGE = auto()
    """Outflow.
    Only lower bound by default
    """
    CONSUME = auto()
    """Inflow 
    """
    STORE = auto()
    """Inventory size 
    """
    CAPACITY = auto()
    """Production capacity
    Set at Process
    """
    TRANSPORT = auto()
    """Export capacity
    Set at Transport
    """

    @classmethod
    def all(cls) -> List[str]:
        return [i.name for i in cls]

    @classmethod
    def resource(cls) -> List[str]:
        return list(set(cls.all()) - set(['CAPACITY', 'TRANSPORT']))

    @classmethod
    def process(cls) -> List[str]:
        return ['CAPACITY']

    @classmethod
    def transport(cls) -> List[str]:
        return ['TRANSPORT']


class CashFlow(Enum):
    """Money going towards or being made from
    """
    SELL_PRICE = auto()
    """Revenue per unit basis of Resource sold
    """
    PURCHASE_PRICE = auto()
    """Expenditure per unit basis of Resource consumed
    """
    STORAGE_COST = auto()
    """Cost of maintaining Resource inventory
    """
    CREDIT = auto()
    """Credit earned from production of Resource
    """
    PENALTY = auto()
    """For unmet demand
    """
    CAPEX = auto()
    FOPEX = auto()
    """Capital and fixed operational expenditure. Scales by Process/Transport capacity
    """
    VOPEX = auto()
    """Variable operational expenditure. Scales by total production from Process/Transport
    """
    INCIDENTAL = auto()
    """Needs to be spent irrespective of Process/Transport capacity
    """
    LAND_COST = auto()
    """Expenditure on acquiring land
    """

    @classmethod
    def resource(cls) -> List[str]:
        return ['SELL_PRICE', 'PURCHASE_PRICE', 'STORAGE_COST', 'CREDIT', 'PENALTY']

    @classmethod
    def process(cls) -> List[str]:
        return ['CAPEX', 'FOPEX', 'VOPEX', 'INCIDENTAL']

    @classmethod
    def transport(cls) -> List[str]:
        return cls.process()

    @classmethod
    def location(cls) -> List[str]:
        return ['LAND_COST']

    @classmethod
    def network(cls) -> List[str]:
        return cls.location()


class Land(Enum):
    """Land use or available at spatial scale 
    """
    USE = auto()
    """Exact
    """
    AVAILABLE = auto()
    """Upper bound 
    """

    @classmethod
    def process(cls) -> List[str]:
        return ['USE']

    @classmethod
    def transport(cls) -> List[str]:
        return cls.process()

    @classmethod
    def location(cls) -> List[str]:
        return ['AVAILABLE']

    @classmethod
    def network(cls) -> List[str]:
        return cls.location()


class Emission(Enum):
    """Type of emission being considered
    """
    GWP = auto()
    """Global Warming Potential
    """
    ODP = auto()
    """Ozone Depletion Potential
    """
    ACID = auto()
    """Acidification Potential
    """
    EUTT = auto()
    """Terrestrial Eutrophication Potential
    """
    EUTF = auto()
    """Freshwater Eutrophication Potential
    """
    EUTM = auto()
    """Marine Eutrophication Potential
    """

    @classmethod
    def all(cls) -> List[str]:
        return [i.name for i in cls]


class Life(Enum):
    """Constrictes the life of a Process or Transport 
    """
    INTRODUCE = auto()
    """Earliest setup 
    """
    RETIRE = auto()
    """Threshold on keeping active
    """
    LIFETIME = auto()
    """Length of use. Upper bound
    """
    PFAIL = auto()
    """Chance of failure
    """

    @classmethod
    def process(cls) -> List[str]:
        return [i.name for i in cls]

    @classmethod
    def transport(cls) -> List[str]:
        return [i.name for i in cls]


class Loss(Enum):
    """Resource lost during?
    """
    STORAGE = auto()
    TRANSPORT = auto()

    @classmethod
    def resource(cls) -> List[str]:
        return ['STORAGE']

    @classmethod
    def transport(cls) -> List[str]:
        return ['TRANSPORT']
