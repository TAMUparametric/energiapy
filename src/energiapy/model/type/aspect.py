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

from dataclasses import dataclass
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
        """parameter name generator
        """
        return self.name.lower().capitalize()

    def vnamer(self):
        """variable name generator
        """
        return self.name.lower()

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum
        """
        return 'Limit'

    @staticmethod
    def resource() -> str:
        return [Limit.DISCHARGE, Limit.CONSUME]

    @staticmethod
    def process() -> str:
        return [Limit.CAPACITY]

    @staticmethod
    def transport() -> str:
        return [Limit.CAPACITY]

    @classmethod
    def all(cls) -> str:
        """all members of the Enum
        """
        return [i for i in cls]


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
        """parameter name generator
        """
        return self.name.lower().capitalize()

    def vnamer(self):
        """variable name generator
        """
        return self.name.lower()

    @classmethod
    def all(cls):
        """all members of the Enum
        """
        return [i for i in cls]

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum
        """
        return 'CapBound'

    @staticmethod
    def process():
        return [CapBound.PRODUCE]

    @staticmethod
    def storage():
        return [CapBound.STORE]

    @staticmethod
    def transport():
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
        """parameter name generator
        """
        return self.name.lower().capitalize()

    def vnamer(self):
        """variable name generator
        """
        return self.name.lower()

    @staticmethod
    def tname() -> str:
        return 'CashFlow'

    @staticmethod
    def resource() -> list:
        return [getattr(CashFlow, i) for i in ['SELL_COST', 'PURCHASE_COST', 'STORE_COST', 'CREDIT', 'PENALTY']]

    @staticmethod
    def process() -> list:
        return [getattr(CashFlow, i) for i in ['CAPEX', 'FOPEX', 'VOPEX', 'INCIDENTAL']]

    @staticmethod
    def transport() -> list:
        return [getattr(CashFlow, i) for i in ['CAPEX', 'FOPEX', 'VOPEX', 'INCIDENTAL']]

    @staticmethod
    def location() -> list:
        return [CashFlow.LAND_COST]

    @classmethod
    def all(cls) -> str:
        """all members of the Enum
        """
        return [i for i in cls]


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
        """parameter name generator
        """
        return self.name.lower().capitalize()

    def vnamer(self):
        """variable name generator
        """
        return self.name.lower()

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum
        """
        return 'Land'

    @staticmethod
    def process() -> list:
        return [Land.LAND_USE]

    @staticmethod
    def transport() -> list:
        return [Land.LAND_USE]

    @staticmethod
    def location() -> list:
        return [Land.LAND]

    @staticmethod
    def network() -> list:
        return [Land.LAND]

    @classmethod
    def all(cls) -> str:
        """all members of the Enum
        """
        return [i for i in cls]


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
        """parameter name generator
        """
        return self.name.lower().capitalize()

    def vnamer(self):
        """variable name generator
        """
        return self.name.lower()

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum
        """
        return 'Emission'

    @classmethod
    def all(cls) -> str:
        """all members of the Enum
        """
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
    TRL = auto()
    """Technology Readiness Level
    """

    def pnamer(self):
        """parameter name generator
        """
        return self.name.lower().capitalize()

    def vnamer(self):
        """variable name generator
        """
        return self.name.lower()

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum
        """
        return 'Life'

    @classmethod
    def all(cls) -> str:
        """all members of the Enum
        """
        return [i for i in cls]


class Loss(Enum):
    """Resource lost during?
    """
    STORE_LOSS = auto()
    TRANSPORT_LOSS = auto()

    def pnamer(self):
        """parameter name generator
        """
        return self.name.lower().capitalize()

    def vnamer(self):
        """variable name generator
        """
        return self.name.lower()

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum
        """
        return 'Loss'

    @staticmethod
    def storage() -> list:
        return [Loss.STORE_LOSS]

    @staticmethod
    def transport() -> list:
        return [Loss.TRANSPORT_LOSS]

    @classmethod
    def all(cls) -> str:
        """all members of the Enum
        """
        return [i for i in cls]


@dataclass(frozen=True)
class Aspects:
    resource = Limit.resource() + CashFlow.resource() + \
        Emission.all() + CapBound.all()
    process = Limit.process() + Land.process() + CashFlow.process() + Emission.all() + Life.all()
    storage = Loss.storage()
    transport = Limit.transport() + CashFlow.transport() + \
        Land.transport() + Loss.transport() + Emission.all() + Life.all()
    location = Land.location() + CashFlow.location()
    network = Land.network()
