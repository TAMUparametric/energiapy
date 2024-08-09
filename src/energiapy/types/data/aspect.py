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


class AspectMixin:
    """common methods for all Aspect enums"""

    def pname(self):
        """Parameter name generator"""
        return getattr(self, 'name').lower().capitalize()

    def vname(self):
        """Variable name generator"""
        return getattr(self, 'name').lower()

    @classmethod
    def aname(cls):
        """Returns the name of the Enum"""
        return cls.__name__

    @classmethod
    def all(cls) -> str:
        """All members of the Enum"""
        return [i for i in cls]


class CapBound(AspectMixin, Enum):
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
    """Export capacitated by Transit capacity
    if declared at Transit
    """

    @staticmethod
    def at_process():
        return [CapBound.PRODUCE]

    @staticmethod
    def at_storage():
        return [CapBound.STORE]

    @staticmethod
    def at_transport():
        return [CapBound.TRANSPORT]

    # for i in operations,:
    # PRODUCE - Process/Storage, (Location, Process/Storage), Transit, (Linkage, Transit)


class CashFlow(AspectMixin, Enum):
    """Money going towards or being made from"""

    SELL_COST = auto()
    """Revenue per unit basis of Resource sold
    """
    PURCHASE_COST = auto()
    """Expenditure per unit basis of Resource consumed
    """
    CREDIT = auto()
    """Credit earned from production of Resource
    """
    PENALTY = auto()
    """For unmet demand
    """
    STORE_COST = auto()
    """Cost of maintaining Resource inventory
    """
    CAPEX = auto()
    FOPEX = auto()
    """Capital and fixed operational expenditure. Scales by Process/Transit capacity
    """
    VOPEX = auto()
    """Variable operational expenditure. Scales by total production from Process/Transit
    """
    INCIDENTAL = auto()
    """Needs to be spent irrespective of Process/Transit capacity
    """
    LAND_COST = auto()
    """Expenditure on acquiring land
    """

    @staticmethod
    def resource() -> list:
        return [
            getattr(CashFlow, i)
            for i in ['SELL_COST', 'PURCHASE_COST', 'STORE_COST', 'CREDIT', 'PENALTY']
        ]

    @staticmethod
    def operation() -> list:
        return [getattr(CashFlow, i)
                for i in ['CAPEX', 'FOPEX', 'VOPEX', 'INCIDENTAL']]

    @staticmethod
    def spatial() -> list:
        return [CashFlow.LAND_COST]

    # Resource, Process, Resource, Locatiom,


class Impact(AspectMixin, Enum):
    """Type of emission being considered"""

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
    # Commodity, Operation; Bound Spatial


class LandStat(AspectMixin, Enum):
    """Land use or available at spatial scale"""

    LAND_USE = auto()
    """Exact
    """
    LAND_CAP = auto()
    """Upper bound
    """

    @staticmethod
    def operation() -> list:
        return [LandStat.LAND_USE]

    @staticmethod
    def spatial() -> list:
        return [LandStat.LAND_USE]


class Life(AspectMixin, Enum):
    """Constrictes the life of a Process or Transit"""

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
    # Operation


class Limit(AspectMixin, Enum):
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
    """Process or Storage or Transit capacity
    """

    @staticmethod
    def resource() -> str:
        return [Limit.DISCHARGE, Limit.CONSUME]

    @staticmethod
    def operation() -> str:
        return [Limit.CAPACITY]


# DISCHARGE, CONSUME - Process, Location, (Location, Process)
# CAPACITY - Process, Storage, Transit, (Location, Operation)


class Loss(AspectMixin, Enum):
    """Resource lost during?"""

    STORE_LOSS = auto()
    TRANSPORT_LOSS = auto()

    @staticmethod
    def during_storage() -> list:
        return [Loss.STORE_LOSS]

    @staticmethod
    def during_transport() -> list:
        return [Loss.TRANSPORT_LOSS]

    # Resource, Storage/ Transit. (Location/Linkage, Storage/Transit),
