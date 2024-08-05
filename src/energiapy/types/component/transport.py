from enum import Enum, auto
from typing import Set


class TransitType(Enum):
    """Transit classification"""

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
    def network_level(cls) -> Set[str]:
        """Set at Network level"""
        return {'INTERMITTENT'}

    # * -------------------------- Automated below this ----------------------------------------

    @classmethod
    def all(cls) -> Set[str]:
        """All Transit classifications"""
        return {i.name for i in cls}

    @classmethod
    def transport_level(cls) -> Set[str]:
        """Set when Transit is declared"""
        return cls.all() - cls.network_level()
