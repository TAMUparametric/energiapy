from dataclasses import dataclass
from enum import Enum, auto
from itertools import product
from typing import Dict
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
    """Can the resource be _____ ? (and varies in terms of)
    """
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
    DEMAND = auto()
    """used to meet a particular set demand at location (demand)
    """
    TRANSPORT = auto()
    """transported
    """


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
    """Whether a process is production or storage type
    """
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
    """
    Storage type process
    """
    STORAGE_REQ = auto()
    """
    Storage type process, but storage itself consumes another resource. 
    """
    LINEAR_CAPEX = auto()
    """
    Consider constant CAPEX
    """
    PWL_CAPEX = auto()
    """
    Use piece-wise linear CAPEX
    """
    CAPACITY = auto()
    CAP_MAX = auto()
    CAP_MIN = auto()
    """Has a capacity 
    """
    CAPEX = auto()
    FOPEX = auto()
    VOPEX = auto()
    INCIDENTAL = auto()
    """ Technology costs to set up processes
    """
    CREDIT = auto()
    """If the process is eligible for credit 
    """
    LAND = auto()
    """If the process requires land 
    """


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

# *------------------------------Location-------------------------------------------------


class LocationType(Enum):
    """Whether a location is a source or a sink
    """
    SOURCE = auto()
    SINK = auto()
    LAND_COST = auto()


# *------------------------------Transport-------------------------------------------------

class TransportType(Enum):
    """
    """
    CAPACITY = auto()
    CAPEX = auto()
    FOPEX = auto()
    VOPEX = auto()
    INCIDENTAL = auto()

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
