from enum import Enum, auto
from dataclasses import dataclass


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



# *-----------------------Process------------------------------------------------
