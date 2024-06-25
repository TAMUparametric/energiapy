""" energiapy.components.comptype - type of component (TemporalScale, Problem, Resource, Emission, Process, Location, Transport, Network, Scenario)
"""
from dataclasses import dataclass
from enum import Enum, auto
from itertools import product
from typing import Dict, List
from warnings import warn

# *-----------------------TemporalScale------------------------------------------------


class ProblemType(Enum):
    """Problem type
    """
    DESIGN = auto()
    """Only design decisions are taken 
    """
    SCHEDULING = auto()
    """Only scheduling decisions are taken 
    """
    DESIGN_AND_SCHEDULING = auto()
    """Design and scheduling decisions are taken simultaneously 
    """


class ScaleType(Enum):
    """Classifies problem as having multiple or single scales  for decision making
    """
    MULTI = auto()
    """Problem has multiple scales 
    """
    SINGLE = auto()
    """Problem has a single scale  
    """

# *-----------------------Resource------------------------------------------------


class ResourceType(Enum):
    """What class a Resource fits into or if a particular parameter is defined 
    """
    # * -------------------- Classifications--------------------------------------
    STORE = auto()
    """stored in inventory 
    """
    PRODUCE = auto()
    """Produced 
    """
    IMPLICIT = auto()
    """Does not enter or leave the system
    """
    DISCHARGE = auto()
    """just dispensed
    """
    SELL = auto()
    """sold to generate revenue (revenue)
    """
    CONSUME = auto()
    """taken for free (availability)
    """
    PURCHASE = auto()
    """bought for a price (price)
    """
    MEET_DEMAND = auto()
    """used to meet a particular set demand at location (demand)
    """
    TRANSPORT = auto()
    """transported
    """
    # * ----------------------Parameters------------------------------------------------
    SELL_PRICE = auto()
    """Revenue generated
    """
    PURCHASE_PRICE = auto()
    """Amount spend to consume
    """
    AVAILABILITY = auto()
    """Alias for cons_max, i.e. maximum consumption allowed
    """
    DEMAND = auto()
    """Demand to be met at Location
    """
    STORE_MAX = auto()
    STORE_MIN = auto()
    STORE_LOSS = auto()
    STORAGE_COST = auto()
    """Inventory parameters 
    """

    # * -------------------------- Classmethods ----------------------------------------
    # Need to define what are parameters, the rest are set to classifications
    # Need to define what is set at the location level and transport level. The rest is calculated

    # * Update this

    @classmethod
    def parameters(cls) -> List[str]:
        """All parameters
        """
        return ['SELL_PRICE', 'PURCHASE_PRICE', 'AVAILABILITY', 'DEMAND', 'STORE_MAX', 'STORE_MIN', 'STORE_LOSS', 'STORAGE_COST']

    @classmethod
    def location_level(cls) -> List[str]:
        """Set when Location is declared
        """
        return ['DEMAND', 'HAS_DEMAND']

    @classmethod
    def transport_level(cls) -> List[str]:
        """Set when Transport is declared
        """
        return ['TRANSPORT']

    @classmethod
    def uncertain(cls) -> List[str]:
        """Uncertain parameters, can be handled: 
        1. Multiparametrically by defining as multiparametric variables (energiapy.components.parameters.mpvar.MPVar)
        2. By using factors of deterministic data and via multiperiod scenario analysis 
        """
        exclude_ = ['STORE_MIN']
        return list(set(cls.parameters()) - set(exclude_))

    # * Automated below this

    @classmethod
    def all(cls) -> List[str]:
        """All Resource paramters and classifications
        """
        return [i.name for i in cls]

    @classmethod
    def classifications(cls) -> List[str]:
        """All classifications
        """
        return list(set(cls.all()) - set(cls.parameters()))

    @classmethod
    def resource_level(cls) -> List[str]:
        """Set when Resource is declared
        """
        return list(set(cls.all()) - set(cls.location_level()) - set(cls.transport_level()))

    @classmethod
    def resource_level_parameters(cls) -> List[str]:
        """Set when Resource is declared, and are associated with actual values, i.e. are non classifiers 
        """
        return list(set(cls.resource_level()) & set(cls.parameters()))

    @classmethod
    def resource_level_classifications(cls) -> List[str]:
        """Set when Resource is declared, and are classifications
        """
        return list(set(cls.resource_level()) & set(cls.classifications()))

    @classmethod
    def location_level_classifications(cls) -> List[str]:
        """Set at Location level, and are classifications
        """
        return list(set(cls.location_level()) & set(cls.classifications()))

    @classmethod
    def location_level_parameters(cls) -> List[str]:
        """Set at Location level and are parameters 
        """
        return list(set(cls.location_level()) & set(cls.parameters()))

    @classmethod
    def transport_level_classifications(cls) -> List[str]:
        """Set at Transport level, and are classifications
        """
        return list(set(cls.transport_level()) & set(cls.classifications()))

    @classmethod
    def transport_level_parameters(cls) -> List[str]:
        """Set at Transport level and are parameters 
        """
        return list(set(cls.transport_level()) & set(cls.parameters()))


# *-----------------------Emission--------------------------------------


class EmissionType(Enum):
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


# *-----------------------Process------------------------------------------------


class ProcessType(Enum):
    """What class a Process fits into or if a particular parameter is defined 
    """
    # * -------------------- Classifications--------------------------------------
    SINGLE_PRODMODE = auto()
    """Only allows one mode
    """
    MULTI_PRODMODE = auto()
    """Allows multiple modes
    """
    NO_MATMODE = auto()
    """Does not use materials
    """
    SINGLE_MATMODE = auto()
    """Has a single material modes
    """
    MULTI_MATMODE = auto()
    """Has multiple material modes
    """
    STORAGE = auto()
    STORAGE_DISCHARGE = auto()
    """Storage type process
    """
    STORAGE_REQ = auto()
    """Storage type process, but storage itself consumes another resource. 
    """
    LINEAR_CAPEX = auto()
    """Consider constant CAPEX
    """
    PWL_CAPEX = auto()
    """Use piece-wise linear CAPEX
    """
    INTERMITTENT = auto()
    """Not strictly intermittent, but experiences some type of variability 
    """
    # * -------------------- Parameters--------------------------------------
    CAP_MAX = auto()
    CAP_MIN = auto()
    """Bounds to capacity expansion
    """
    LAND = auto()
    """If the process requires land 
    """
    CAPEX = auto()
    FOPEX = auto()
    VOPEX = auto()
    INCIDENTAL = auto()
    """Technology costs to set up processes
    """
    CAPACITY = auto()
    """Amount of the established capacity that can be exercised for production
    """
    CREDIT = auto()
    """If the process is eligible for credit 
    """
    INTRODUCE = auto()
    RETIRE = auto()
    LIFETIME = auto()
    """Temporal behaviour 
    """
    P_FAIL = auto()
    """Probability of failure 
    """

    # * -------------------------- Classmethods ----------------------------------------
    # Need to define what are parameters, the rest are set to classifications
    # Need to define what is set at the location level. The rest is calculated

    # * Update this

    @classmethod
    def parameters(cls) -> List[str]:
        """All parameters
        """
        return ['CAP_MAX', 'CAP_MIN', 'CAPEX', 'FOPEX', 'VOPEX', 'INCIDENTAL', 'LAND', 'CREDIT', 'CAPACITY', 'INTRODUCE', 'RETIRE', 'LIFETIME', 'P_FAIL']

    @classmethod
    def temporal_parameters(cls) -> List[str]:
        """These define the temporal aspects of establishing processes. Factors not provided for these. 
        """
        return ['INTRODUCE', 'RETIRE', 'LIFETIME', 'P_FAIL']

    @classmethod
    def process_level_resource_parameters(cls) -> List[str]:
        """Resource parameters that can be declared at Process level
        Do not treat these as Process parameters. 
        In the current list, all of these will be assigned to a STORE type Resource
        """
        return ['STORE_MAX', 'STORE_MIN', 'STORAGE_COST', 'STORE_LOSS']

    @classmethod
    def location_level(cls) -> List[str]:
        """Set when Location is declared
        STORAGE_DISCHARGE is assigned when Discharge Process is created at Location level for a STORAGE PROCESS
        """
        return ['CREDIT', 'STORAGE_DISCHARGE', 'INTERMITTENT', 'CAPACITY']

    @classmethod
    def uncertain(cls) -> List[str]:
        """Uncertain parameters, can be handled: 
        1. Multiparametrically by defining as multiparametric variables (energiapy.components.parameters.mpvar.MPVar)
        2. By using factors of deterministic data and via multiperiod scenario analysis 
        """
        exclude_ = ['CAP_MIN']
        return list(set(cls.parameters()) - set(cls.temporal_parameters()) - set(cls.process_level_resource_parameters()) - set(exclude_))

    # * Automated below this

    @classmethod
    def all(cls) -> List[str]:
        """All Process paramters and classifications
        """
        return [i.name for i in cls]

    @classmethod
    def classifications(cls) -> List[str]:
        """All classifications
        """
        return list(set(cls.all()) - set(cls.parameters()))

    @classmethod
    def process_level(cls) -> List[str]:
        """Set when Process is declared
        """
        return list(set(cls.all()) - set(cls.location_level()))

    @classmethod
    def process_level_parameters(cls) -> List[str]:
        """Set when Process is declared, and are associated with actual values, i.e. are non classifiers 
        """
        return list(set(cls.process_level()) & set(cls.parameters()))

    @classmethod
    def process_level_classifications(cls) -> List[str]:
        """Set when Process is declared, and are classifications
        """
        return list(set(cls.process_level()) & set(cls.classifications()))

    @classmethod
    def location_level_classifications(cls) -> List[str]:
        """Set when Process is declared, and are classifications
        """
        return list(set(cls.location_level()) & set(cls.classifications()))

    @classmethod
    def location_level_parameters(cls) -> List[str]:
        """Set at Location level and are parameters 
        """
        return list(set(cls.location_level()) & set(cls.parameters()))


# *------------------------------Location-------------------------------------------------


class LocationType(Enum):
    """Whether a location is a source or a sink
    """
    SOURCE = auto()
    SINK = auto()
    """Location parameters
    """
    LAND_COST = auto()
    LAND_MAX = auto()

    # * -------------------------- Classmethods ----------------------------------------
    # Need to define what are parameters, the rest are set to classifications
    # Need to define what is set at the network level. The rest is calculated

    # * Update this

    @classmethod
    def parameters(cls) -> List[str]:
        """All parameters
        """
        return ['LAND_COST', 'LAND_MAX']

    @classmethod
    def network_level(cls) -> List[str]:
        """Set at Network level
        """
        return ['SOURCE', 'SINK']

    # * Automated below this

    @classmethod
    def all(cls) -> List[str]:
        """All Location paramters and classifications
        """
        return [i.name for i in cls]

    @classmethod
    def classifications(cls) -> List[str]:
        """All classifications
        """
        return list(set(cls.all()) - set(cls.parameters()))

    @classmethod
    def location_level(cls) -> List[str]:
        """Set when Location is declared
        """
        return list(set(cls.all()) - set(cls.network_level()))

    @classmethod
    def location_level_parameters(cls) -> List[str]:
        """Set when Location is declared and are parameters
        """
        return list(set(cls.location_level()) & set(cls.parameters()))

    @classmethod
    def location_level_classifications(cls) -> List[str]:
        """Set when Location is declared and are locations
        """
        return list(set(cls.location_level()) & set(cls.classifications()))

    @classmethod
    def network_level_parameters(cls) -> List[str]:
        """Set at Network level and are parameters
        """
        return list(set(cls.network_level()) & set(cls.parameters()))

    @classmethod
    def network_level_classifications(cls) -> List[str]:
        """Set at Network level and are classifications
        """
        return list(set(cls.network_level()) & set(cls.classifications()))


# *------------------------------Transport-------------------------------------------------

class TransportType(Enum):
    """Transport classification
    """
    CAPACITY = auto()
    """Transport parameters
    """
    CAP_MAX = auto()
    CAP_MIN = auto()
    CAPEX = auto()
    FOPEX = auto()
    VOPEX = auto()
    INCIDENTAL = auto()

    # * -------------------------- Classmethods ----------------------------------------
    # Need to define what are classification, the rest are set to parameters
    # Need to define what is set at the network level. The rest is calculated

    # * Update this

    @classmethod
    def classifications(cls) -> List[str]:
        """All classifications
        """
        return ['CAPACITY']

    @classmethod
    def network_level(cls) -> List[str]:
        """Set at Network level
        """
        return []

    # * Automated below this

    @classmethod
    def all(cls) -> List[str]:
        """All Transport paramters and classifications
        """
        return [i.name for i in cls]

    @classmethod
    def parameters(cls) -> List[str]:
        """All parameters
        """
        return list(set(cls.all()) - set(cls.classifications()))

    @classmethod
    def network_level_parameters(cls) -> List[str]:
        """Set at Network level and are parameters
        """
        return list(set(cls.network_level()) & set(cls.parameters()))

    @classmethod
    def network_level_classifications(cls) -> List[str]:
        """Set at Network level and are locations
        """
        return list(set(cls.network_level()) & set(cls.classifications()))

    @classmethod
    def transport_level(cls) -> List[str]:
        """Set when Location is declared
        """
        return list(set(cls.all()) - set(cls.network_level()))

    @classmethod
    def transport_level_parameters(cls) -> List[str]:
        """Set when Location is declared and are parameters
        """
        return list(set(cls.transport_level()) & set(cls.parameters()))

    @classmethod
    def transport_level_classifications(cls) -> List[str]:
        """Set when Location is declared and are classifications
        """
        return list(set(cls.transport_level()) & set(cls.classifications()))


# *------------------------------Network-------------------------------------------------


class NetworkType(Enum):
    """Network Parameters
    """
    LAND_MAX = auto()

    # * -------------------------- Classmethods ----------------------------------------
    # Need to define what are classification, the rest are set to parameters

    # * Update this

    @classmethod
    def parameters(cls) -> List[str]:
        """All parameters
        """
        return ['LAND_MAX']

    # * Automated below this

    @classmethod
    def all(cls) -> List[str]:
        """All Network paramters and classifications
        """
        return [i.name for i in cls]

    @classmethod
    def classifications(cls) -> List[str]:
        """All classifications
        """
        return list(set(cls.all()) - set(cls.parameters()))


# *------------------------------Scenario-------------------------------------------------


class ScenarioType(Enum):
    """
    Single location
    """
    SINGLE_LOCATION = auto()
    """
    Multi-location
    """
    MULTI_LOCATION = auto()


# *----------------------------TBD---------------------------------------------

@dataclass
class ProcessRamp:
    modes: list
    cap_pwl: Dict
    rates: Dict
    sequence: Dict

    def __post_init__(self):
        sequence_fix = {i: False for i in [
            k for k in product(self.modes, self.modes)]}
        rates_fix = {i: 0 for i in [
            k for k in product(self.modes, self.modes)]}

        for i in sequence_fix.keys():
            if i in self.sequence.keys():
                sequence_fix[i[::-1]] = self.sequence[i]
                sequence_fix[i] = self.sequence[i]
            if i[0] == i[1]:
                sequence_fix[i] = True
        self.sequence = sequence_fix

        for i in rates_fix.keys():
            if i in self.rates.keys():
                rates_fix[i] = self.rates[i]
        self.rates = rates_fix

        if list(self.cap_pwl.keys()) != self.modes:
            warn(
                'The Piece Wise Linear bounds for capacities should match the declared modes')


# *------------------------------Depreciated -------------------------------------------------

class VaryingResource(Enum):
    """
    Whether the demand or price are varying
    """
    DETERMINISTIC_DEMAND = auto()
    """
    Utilize deterministic demand data as parameters
    """
    DETERMINISTIC_PRICE = auto()
    """
    Utilize deterministic price data as parameters
    """
    DETERMINISTIC_AVAILABILITY = auto()
    """
    Utilize deterministic resource availability as parameters
    """
    DETERMINISTIC_REVENUE = auto()
    """
    Utilize deterministic resource revenues as parameters
    """
    UNCERTAIN_DEMAND = auto()
    """
    Generate uncertainty variables for demand
    """
    UNCERTAIN_PRICE = auto()
    """
    Generate uncertainty variables for price
    """
    UNCERTAIN_AVAILABILITY = auto()
    """
    Generate uncertainty variables for resource availability
    """
    UNCERTAIN_REVENUE = auto()
    """
    Generate uncertainty variables for resource revenue
    """
    CERTAIN_DEMAND = auto()
    """Use exact parameter for demand 
    """
    CERTAIN_PRICE = auto()
    """Use exact parameter for price
    """
    CERTAIN_AVAILABILITY = auto()
    """Use exact parameter for availability
    """
    CERTAIN_REVENUE = auto()
    """Use exact parameter for revenue
    """
    IMPLICIT = auto()
    """Produced and utilized implicitly
    """
    STORED = auto()
    """Implicitly generated stored resource
    """


class CostDynamics(Enum):
    """
    To consider the dynamics of CAPEX
    """
    CONSTANT = auto()
    """
    Consider constance CAPEX
    """
    PWL = auto()
    """
    Use piece-wise linear CAPEX
    """


class ProcessMode(Enum):
    """
    Mode for process
    """
    SINGLE = auto()
    """
    Only allows one mode
    """
    MULTI = auto()
    """
    Allows multiple modes
    """
    STORAGE = auto()
    """
    Storage type process
    """


class MaterialMode(Enum):
    """
    Mode for materials 
    """
    SINGLE = auto()
    """
    Allows only single material 
    """
    MULTI = auto()
    """
    Can use multiple material combinations 
    """


class VaryingProcess(Enum):
    """
    The type of process capacity variability
    """
    DETERMINISTIC_CAPACITY = auto()
    """
    Utilize deterministic data as parameters for capacity
    """
    DETERMINISTIC_EXPENDITURE = auto()
    """
    Utilize deterministic data as parameters for expenditure
    """
    UNCERTAIN_CAPACITY = auto()
    """
    Generate uncertainty variables
    """
    UNCERTAIN_EXPENDITURE = auto()
    """
    Generate uncertainty variables for expenditure
    """
    CERTAIN_CAPACITY = auto()
    """
    Use certain parameter for capacity
    """
    CERTAIN_EXPENDITURE = auto()
    """
    Use certain parameter for expenditure
    """
    MULTIMODE = auto()
    """
    Has multiple modes of operation
    """


class VaryingTransport(Enum):
    """whether the Transport capacity and costs are varying or certain
    """
    DETERMINISTIC_CAPACITY = auto()
    """
    Utilize deterministic data as parameters for capacity
    """
    CERTAIN_CAPACITY = auto()
    """
    Use certain parameter for capacity
    """
    UNCERTAIN_CAPACITY = auto()
    """
    Use uncertain parameter for capacity
    """
    DETERMINISTIC_CAPEX = auto()
    """
    Utilize deterministic data as parameters for capex
    """
    CERTAIN_CAPEX = auto()
    """
    Use certain parameter for capex
    """
    UNCERTAIN_CAPEX = auto()
    """
    Use uncertain parameter for capex
    """
    DETERMINISTIC_VOPEX = auto()
    """
    Utilize deterministic data as parameters for vopex
    """
    CERTAIN_VOPEX = auto()
    """
    Use certain parameter for vopex
    """
    UNCERTAIN_VOPEX = auto()
    """
    Use uncertain parameter for vopex
    """
    DETERMINISTIC_FOPEX = auto()
    """
    Utilize deterministic data as parameters for fopex
    """
    CERTAIN_FOPEX = auto()
    """
    Use certain parameter for fopex
    """
    UNCERTAIN_FOPEX = auto()
    """
    Use uncertain parameter for fopex
    """
