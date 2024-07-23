"""energiapy.components.model.paramtype - 

These are enums for the type and subtypes of parameters

Each parameter has a spatiotemporal disposition 
spatial: SpatialDisposition is determined from the Component where the parameter is defined
temporal: TemporalDisposition needs to be provided using the _scale attributes

The parameter could either certain or uncertain (vtype: Variability)
vtypes have substypes:
Certainty subtypes are either some combination of Bounds or an Exact value
Uncertainty subtypes are Parametric, deterministic, stochastic

Special parameters are actual dataclasses: BigM, SmallM, Factor, MPVar/Theta

Finally, 
aspect: ParameterType describes what the parameter models. There are subtypes for each type.
"""

from enum import Enum, auto


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
    CAPACITY = auto()
    """Process or Transport capacity
    """

    def pnamer(self):
        """parameter name generator"""
        return self.name.lower().capitalize()

    def vnamer(self):
        """variable name generator"""
        return self.name.lower()

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum
        """
        return 'Limit'

    @classmethod
    def all(cls) -> str:
        """all members of the Enum"""
        return [i for i in cls]

    @classmethod
    def resource(cls) -> str:
        return [Limit.DISCHARGE, Limit.CONSUME]

    @classmethod
    def process(cls) -> str:
        return [Limit.CAPACITY]

    @classmethod
    def transport(cls) -> str:
        return [Limit.CAPACITY]


class CapBound(Enum):
    """These are capacitated by the realized capacities
    of the component where the Resource is declared
    """
    PRODUCE = auto()
    """Production capacitated by Process capacity
    """
    STORE = auto()
    """Amount stored capacitated by Process capacity
    """
    TRANSPORT = auto()
    """Export capacitated by Transport capacity
    if declared at Transport
    """

    def pnamer(self):
        """parameter name generator"""
        return self.name.lower().capitalize()

    def vnamer(self):
        """variable name generator"""
        return self.name.lower()

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum
        """
        return 'CapBound'

    @classmethod
    def all(cls) -> str:
        """all members of the Enum"""
        return [i for i in cls]

    @classmethod
    def process(cls) -> str:
        return [CapBound.PRODUCE, CapBound.STORE]

    @classmethod
    def transport(cls) -> str:
        return [CapBound.TRANSPORT]


class CashFlow(Enum):
    """Money going towards or being made from
    """
    SELL_COST = auto()
    """Revenue per unit basis of Resource sold
    """
    PURCHASE_COST = auto()
    """Expenditure per unit basis of Resource consumed
    """
    STORE_COST = auto()
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

    def pnamer(self):
        """parameter name generator"""
        return self.name.lower().capitalize()

    def vnamer(self):
        """variable name generator"""
        return self.name.lower()

    @staticmethod
    def tname() -> str:
        return 'CashFlow'

    @classmethod
    def all(cls) -> str:
        """all members of the Enum"""
        return [i for i in cls]

    @classmethod
    def resource(cls) -> list:
        return [getattr(CashFlow, i) for i in ['SELL_COST', 'PURCHASE_COST', 'STORE_COST', 'CREDIT', 'PENALTY']]

    @classmethod
    def process(cls) -> list:
        return [getattr(CashFlow, i) for i in ['CAPEX', 'FOPEX', 'VOPEX', 'INCIDENTAL']]

    @classmethod
    def transport(cls) -> list:
        return cls.process()

    @classmethod
    def location(cls) -> list:
        return [CashFlow.LAND_COST]

    @classmethod
    def network(cls) -> list:
        return cls.location()


class Land(Enum):
    """Land use or available at spatial scale 
    """
    LAND_USE = auto()
    """Exact
    """
    LAND = auto()
    """Upper bound 
    """

    def pnamer(self):
        """parameter name generator"""
        return self.name.lower().capitalize()

    def vnamer(self):
        """variable name generator"""
        return self.name.lower()

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum
        """
        return 'Land'

    @classmethod
    def all(cls) -> str:
        """all members of the Enum"""
        return [i for i in cls]

    @classmethod
    def process(cls) -> list:
        return [Land.LAND_USE]

    @classmethod
    def transport(cls) -> list:
        return cls.process()

    @classmethod
    def location(cls) -> list:
        return [Land.LAND]

    @classmethod
    def network(cls) -> list:
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

    def pnamer(self):
        """parameter name generator"""
        return self.name.lower().capitalize()

    def vnamer(self):
        """variable name generator"""
        return self.name.lower()

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum
        """
        return 'Emission'

    @classmethod
    def all(cls) -> str:
        """all members of the Enum"""
        return [i for i in cls]


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

    def pnamer(self):
        """parameter name generator"""
        return self.name.lower().capitalize()

    def vnamer(self):
        """variable name generator"""
        return self.name.lower()

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum
        """
        return 'Life'

    @classmethod
    def all(cls) -> str:
        """all members of the Enum"""
        return [i for i in cls]


class Loss(Enum):
    """Resource lost during?
    """
    STORE_LOSS = auto()
    TRANSPORT_LOSS = auto()

    def pnamer(self):
        """parameter name generator"""
        return self.name.lower().capitalize()

    def vnamer(self):
        """variable name generator"""
        return self.name.lower()

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum
        """
        return 'Loss'

    @classmethod
    def all(cls) -> str:
        """all members of the Enum"""
        return [i for i in cls]

    @classmethod
    def process(cls) -> list:
        return [Loss.STORE_LOSS]

    @classmethod
    def transport(cls) -> list:
        return [Loss.TRANSPORT_LOSS]


class AspectType(Enum):
    """What kind of behaviour does the parameter describe
    All of these have subclasses
    These are predetermined by me, Rahul Kakodkar. 
    The BDFO of energiapy
    """
    LIMIT = Limit
    """Helps create boundaries for the problem 
    by setting a min/max or Exact limit for flow of Resource.
    """
    CASHFLOW = CashFlow
    """Expenditure/Revenue.
    """
    LAND = Land
    """Describes land use and such
    """
    EMISSION = Emission
    """Is an emission.
    """
    LIFE = Life
    """Describes earliest introduction, retirement, lifetime and such
    """
    LOSS = Loss
    """Amount lost during storage or transport
    """
    CAPACITY = CapBound
    """How much of the capacity can be accessed
    """

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum
        """
        return 'AspectType'

    @classmethod
    def all(cls) -> str:
        """all members of the Enum"""
        return [i.value for i in cls]

    @classmethod
    def matches(cls) -> dict:
        d_ = {i: [j.name.lower() for j in i.all()] for i in cls.all()}
        return {k: getattr(i, k.upper()) for i, j in d_.items() for k in j}

    @classmethod
    def aspects(cls) -> list:
        return list(cls.matches())

    @classmethod
    def match(cls, value: str):
        return cls.matches()[value]
