from enum import Enum, auto
from typing import Set


class HasModes(Enum):
    """If the Operation has modes"""

    PRODUCTION = auto()
    """Process Conversion
    """
    CHARGING = auto()
    """Again a Process within Storage
    """
    FREIGHT = auto()
    """Transit Mode
    """
    EXPENDITURE = auto()
    """Capital investment
    """
    USE = auto()
    """Material requirements
    """
    TRL = auto()
    """Technology Readiness Level
    """


class Is(Enum):
    """What class a Process fits into or if a particular parameter is defined"""

    CHARGING = auto()

    STORAGE = auto()
    STORAGE_DISCHARGE = auto()
    """Storage type process
    """
    STORAGE_REQ = auto()
    """Storage type process, but storage itself consumes another resource.
    """
    INTERMITTENT = auto()
    """Not strictly intermittent, but experiences some type of variability
    """
    CREDIT = auto()
    """Incurs credits
    """
    LAND = auto()
    """If the process requires land
    """
    EXPENDITURE = auto()
    """Whether it incurs expenditure [capex, fopex, vopex, incidental]
    """
    READINESS = auto()
    """Whether the temporal behavior has been defined [introduce, retire, lifetime]
    """
    FAILURE = auto()
    """If a p_fail is provided
    """
    EMISSION = auto()
    """Emits
    """

    # *------------------------- Update this ---------------------------------

    @classmethod
    def location_level(cls) -> Set[str]:
        """Set when Location is declared
        STORAGE_DISCHARGE is assigned when Discharge Process is created at Location level for a STORAGE PROCESS
        """
        return {'CREDIT', 'STORAGE_DISCHARGE', 'INTERMITTENT'}

    # *--------------------------- Automated below this ----------------------

    @classmethod
    def all(cls) -> Set[str]:
        """All Process classifications"""
        return {i.name for i in cls}

    @classmethod
    def process_level(cls) -> Set[str]:
        """Set when Process is declared"""
        return cls.all() - cls.location_level()
