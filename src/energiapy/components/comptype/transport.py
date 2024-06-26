from enum import Enum, auto
from typing import List


class TransportType(Enum):
    """Transport classification
    """
    NO_MATMODE = auto()
    """Does not use materials
    """
    SINGLE_MATMODE = auto()
    """Has a single material mode
    """
    MULTI_MATMODE = auto()
    """Has multiple material modes
    """
    LINEAR_CAPEX = auto()
    """Consider constant CAPEX
    """
    PWL_CAPEX = auto()
    """Use piece-wise linear CAPEX
    """
    INTERMITTENT = auto()
    """Allowed capacity utilization is not steady
    """
    LAND = auto()
    """requires land to be set up
    """
    EXPENDITURE = auto()
    """Incurs some expenditure [capex, fopex, vopex, incidental]
    """
    READINESS = auto()
    """Readiness defined
    """
    FAILURE = auto()
    """Fails
    """
    EMISSION = auto()
    """Emits 
    """

    # * -------------------------- Update this ----------------------------------------

    @classmethod
    def network_level(cls) -> List[str]:
        """Set at Network level
        """
        return ['INTERMITTENT']

    # * -------------------------- Automated below this ----------------------------------------

    @classmethod
    def all(cls) -> List[str]:
        """All Transport classifications
        """
        return [i.name for i in cls]

    @classmethod
    def transport_level(cls) -> List[str]:
        """Set when Transport is declared
        """
        return list(set(cls.all()) - set(cls.network_level()))
