"""energiapy.components.parameters.paramtype - Type of paramter, factor, multiparameteric variable, localization
"""
from enum import Enum, auto
from typing import List
from ..comptype import ResourceType, ProcessType


# bla = ProcessType.parameters() + ResourceType.parameters()


# class Testa(Enum):
#     pass


# for i in bla:
#     setattr(Testa, i, auto())


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
    SELL_PRICE = auto()
    PURCHASE_PRICE = auto()
    AVAILABILITY = auto()
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
    """ For Transportations (all updated at Network)
    """
    NETWORK_LAND_MAX = auto()

    @classmethod
    def resource(cls) -> List[str]:
        """Resource factors
        """
        return ['PURCHASE_PRICE', 'AVAILABILITY', 'SELL_PRICE', 'DEMAND']

    @classmethod
    def process(cls) -> List[str]:
        """Process factors
        """
        return ['CAPACITY', 'CAPEX', 'FOPEX', 'VOPEX', 'INCIDENTAL', 'CREDIT']

    @classmethod
    def location(cls) -> List[str]:
        """Location factors
        """
        return ['LAND_COST', 'LAND_MAX']

    @classmethod
    def transport(cls) -> List[str]:
        """Transport factors
        """
        return ['TRANS_CAPACITY', 'TRANS_CAPEX', 'TRANS_FOPEX', 'TRANS_VOPEX', 'TRANS_INCIDENTAL']

    @classmethod
    def network(cls) -> List[str]:
        """Network factors
        """
        return ['NETWORK_LAND_MAX']


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

    @classmethod
    def resource(cls) -> List[str]:
        """Resource localizations
        """
        return ['PURCHASE_PRICE', 'AVAILABILITY', 'SELL_PRICE']

    @classmethod
    def process(cls) -> List[str]:
        """Process localizations
        """
        return ['CAP_MAX', 'CAP_MIN', 'CAPEX', 'FOPEX', 'VOPEX', 'INCIDENTAL', 'CREDIT']


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
    CAP_MAX = auto()
    CAP_MIN = auto()
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
    """ For Transports 
    """
    NETWORK_LAND_MAX = auto()
    """ For NETWORK
    """

    @classmethod
    def resource(cls) -> List[str]:
        """Resource parameters
        """
        return ['PURCHASE_PRICE', 'AVAILABILITY', 'SELL_PRICE', 'DEMAND']

    @classmethod
    def process(cls) -> List[str]:
        """Process parameters
        """
        return ['CAP_MAX', 'CAP_MIN', 'CAPEX', 'FOPEX', 'VOPEX', 'INCIDENTAL', 'LAND', 'CREDIT']

    @classmethod
    def location(cls) -> List[str]:
        """Location parameters
        """
        return ['LAND_COST', 'LAND_MAX']

    @classmethod
    def transport(cls) -> List[str]:
        """Transport parameters
        """
        return ['TRANS_CAPACITY', 'TRANS_CAPEX', 'TRANS_FOPEX', 'TRANS_VOPEX', 'TRANS_INCIDENTAL']

    @classmethod
    def network(cls) -> List[str]:
        """Network parameters
        """
        return ['NETWORK_LAND_MAX']
