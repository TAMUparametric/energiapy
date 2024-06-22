from dataclasses import dataclass
from enum import Enum, auto

# *-----------------------Parameter-------------------------------------------------


class ParameterType(Enum):
    """How does a component parameter vary?
    """
    CERTAIN = auto()
    """Is certain. Does not change over the design or scheduling scale
    """
    UNCERTAIN = auto()
    """Declared as a parametric variable (energiapy.components.parameters.mpvars.Theta)
    or provided as a range using tuple
    """

# *-----------------------Factor------------------------------------------------


class FactorType(Enum):
    """ Type of deterministic data factor
    """
    PURCHASE_PRICE = auto()
    AVAILABILITY = auto()
    SELL_PRICE = auto()
    """ For Resources
    """
    DEMAND = auto()
    """ For Resources (declared at Location level)
    """
    CAPACITY = auto()
    CAPEX = auto()
    FOPEX = auto()
    VOPEX = auto()
    INCIDENTAL = auto()
    """ For Processes
    """
    CREDIT = auto()
    """ For Processes (provided at Location level)
    """
    LAND_COST = auto()
    LAND_MAX = auto()
    """ For Locations
    """
    TRANS_CAPACITY = auto()
    TRANS_CAPEX = auto()
    TRANS_FOPEX = auto()
    TRANS_VOPEX = auto()
    TRANS_INCIDENTAL = auto()
    """ For Transportations
    """

# *-----------------------Localization ------------------------------------------------


class LocalizeType(Enum):
    """Localization factor for parameter values declared at Resource or Process level
    """
    PURCHASE_PRICE = auto()
    CONS_MAX = auto()
    SELL_PRICE = auto()
    """ For Resources
    """
    CAP_MAX = auto()
    CAP_MIN = auto()
    CAPEX = auto()
    FOPEX = auto()
    VOPEX = auto()
    INCIDENTAL = auto()
    """ For Processes
    """


# *-----------------------Multiparametric Var-----------------------------------------------

class MPVarType(Enum):
    """ Type of deterministic data factor
    """
    PURCHASE_PRICE = auto()
    AVAILABILITY = auto()
    SELL_PRICE = auto()
    """ For Resources
    """
    DEMAND = auto()
    """ For Resources (declared at Location level)
    """
    CAPACITY = auto()
    CAPEX = auto()
    FOPEX = auto()
    VOPEX = auto()
    INCIDENTAL = auto()
    LAND = auto()
    """ For Processes
    """
    CREDIT = auto()
    """ For Processes (provided at Location level)
    """
    LAND_COST = auto()
    LAND_MAX = auto()
    """ For Locations
    """
    TRANS_CAPACITY = auto()
    TRANS_CAPEX = auto()
    TRANS_FOPEX = auto()
    TRANS_VOPEX = auto()
    TRANS_INCIDENTAL = auto()
    """ For Transportations
    """
