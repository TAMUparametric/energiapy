from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict
from warnings import warn
from itertools import product

# *-----------------------Parameter-------------------------------------------------


class ParameterType(Enum):
    """How does a component parameter vary?
    """
    CERTAIN = auto()
    """Is certain. Does not change over the design or scheduling scale
    """
    DETERMINISTIC = auto()
    """Data is provided for the variance as a factor
    """
    UNCERTAIN = auto()
    """Limited data. Need to solve parametrically may be
    """


@dataclass
class Th:
    """Just a convinient way to declare parametric variables
    """
    bounds: tuple


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

# *-----------------------Emission Metric--------------------------------------


@dataclass
class EmissionType(Enum):
    """Type of emission being considered
    """
    GWP = auto()
    """Global Warming Potential
    """
    ODP = auto()
    """Ozone Depletion Potential
    """
    ACD = auto()
    """Acidification Potential
    """
    EUTR = auto()
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
    """Has a single material modes
    """
    HAS_MATMODE = auto()
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
    """Has a capacity 
    """
    EXPENDITURE = auto()
    """Costs to set up
    """

# class VaryingProcess(Enum):
#     """
#     The type of process capacity variability
#     """
#     DETERMINISTIC_CAPACITY = auto()
#     """
#     Utilize deterministic data as parameters for capacity
#     """
#     DETERMINISTIC_EXPENDITURE = auto()
#     """
#     Utilize deterministic data as parameters for expenditure
#     """
#     UNCERTAIN_CAPACITY = auto()
#     """
#     Generate uncertainty variables
#     """
#     UNCERTAIN_EXPENDITURE = auto()
#     """
#     Generate uncertainty variables for expenditure
#     """
#     CERTAIN_CAPACITY = auto()
#     """
#     Use certain parameter for capacity
#     """
#     CERTAIN_EXPENDITURE = auto()
#     """
#     Use certain parameter for expenditure
#     """
#     MULTIMODE = auto()
#     """
#     Has multiple modes of operation
#     """


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
