"""energiapy.components.model.paramtype - 

These are enums for the type and subtypes of parameters

Each parameter has a spatiotemporal disposition 
spatial: SpatialDisposition is determined from the Component where the parameter is defined
temporal: TemporalDisposition needs to be provided using the _scale attributes

The parameter could either certain or uncertain (vtype: Variability)
vtypes have substypes:
Certainty subtypes are either some combination of bounds or an exact value
Uncertainty subtypes are parametric, deterministic, stochastic

Special parameters are actual dataclasses: BigM, SmallM, Factor, MPVar/Theta

Finally, 
aspect: ParameterType describes what the parameter models. There are subtypes for each type.
"""

from enum import Enum, auto
from typing import List, TypeVar, Union, Dict
from pandas import DataFrame

Big = TypeVar('Big', bound='BigM')

exact = Union[float, int]
unbound = Union[bool, 'BigM']
parametric = Union[tuple, 'Theta']
dataset = Union[DataFrame, 'DataSet']

direct = Union[exact, unbound, parametric, dataset]
bounds = List[Union[exact, unbound, dataset]]
dict_data = Dict[str, Union[direct, bounds]]


class AspectType(Enum):
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
    @classmethod
    def class_name(cls) -> str:
        """Returns class name 
        """
        return cls.__name__


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
    TRANSPORT = auto()
    """Resource export
    pegged to Transport capacity
    if declared at Transport
    """
    CAPACITY = auto()
    """Process or Transport capacity
    """

    @classmethod
    def class_name(cls) -> str:
        """Returns class name 
        """
        return cls.__name__

    @classmethod
    def all(cls) -> List[str]:
        return [i for i in cls]

    @classmethod
    def resource(cls) -> List[str]:
        return list(set(cls.all()) - set([Limit.CAPACITY]))

    @classmethod
    def process(cls) -> List[str]:
        return [Limit.CAPACITY]

    @classmethod
    def transport(cls) -> List[str]:
        return [Limit.CAPACITY]

    @classmethod
    def types(cls) -> List:
        return Union[direct, bounds, dict_data]


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

    @classmethod
    def class_name(cls) -> str:
        """Returns class name 
        """
        return cls.__name__

    @classmethod
    def resource(cls) -> List[str]:
        return [getattr(CashFlow, i) for i in ['SELL_COST', 'PURCHASE_COST', 'STORE_COST', 'CREDIT', 'PENALTY']]

    @classmethod
    def process(cls) -> List[str]:
        return [getattr(CashFlow, i) for i in ['CAPEX', 'FOPEX', 'VOPEX', 'INCIDENTAL']]

    @classmethod
    def transport(cls) -> List[str]:
        return cls.process()

    @classmethod
    def location(cls) -> List[str]:
        return [CashFlow.LAND_COST]

    @classmethod
    def network(cls) -> List[str]:
        return cls.location()

    @classmethod
    def types(cls) -> List:
        return Union[direct, dict_data]


class Land(Enum):
    """Land use or available at spatial scale 
    """
    LAND_USE = auto()
    """Exact
    """
    LAND = auto()
    """Upper bound 
    """

    @classmethod
    def class_name(cls) -> str:
        """Returns class name 
        """
        return cls.__name__

    @classmethod
    def process(cls) -> List[str]:
        return [Land.LAND_USE]

    @classmethod
    def transport(cls) -> List[str]:
        return cls.process()

    @classmethod
    def location(cls) -> List[str]:
        return [Land.LAND]

    @classmethod
    def network(cls) -> List[str]:
        return cls.location()

    @classmethod
    def types(cls) -> List:
        return Union[direct, dict_data]


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
    def class_name(cls) -> str:
        """Returns class name 
        """
        return cls.__name__

    @classmethod
    def all(cls) -> List[str]:
        return [i for i in cls]

    @classmethod
    def types(cls) -> List:
        return Union[direct, dict_data]


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
    def class_name(cls) -> str:
        """Returns class name 
        """
        return cls.__name__

    @classmethod
    def all(cls) -> List[str]:
        return [i for i in cls]

    @classmethod
    def types(cls) -> List:
        return Union[direct, dict_data]


class Loss(Enum):
    """Resource lost during?
    """
    STORE_LOSS = auto()
    TRANSPORT_LOSS = auto()

    @classmethod
    def class_name(cls) -> str:
        """Returns class name 
        """
        return cls.__name__

    @classmethod
    def resource(cls) -> List[str]:
        return [Loss.STORE_LOSS]

    @classmethod
    def transport(cls) -> List[str]:
        return [Loss.TRANSPORT_LOSS]

    @classmethod
    def types(cls) -> List:
        return Union[direct, dict_data]
