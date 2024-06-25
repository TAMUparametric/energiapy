
from enum import Enum, auto
from typing import List


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
    CREDIT = auto()
    """Incurs credits 
    """
    LAND = auto()
    """If the process requires land 
    """
    CAPEX = auto()
    FOPEX = auto()
    VOPEX = auto()
    INCIDENTAL = auto()
    """What Technology costs have been specified 
    """
    INTRODUCE = auto()
    RETIRE = auto()
    LIFETIME = auto()
    """What Temporal behaviour has been specified 
    """
    FAILURE = auto()
    """If a p_fail is provided 
    """

    # *------------------------- Update this ----------------------------------------

    @classmethod
    def location_level(cls) -> List[str]:
        """Set when Location is declared
        STORAGE_DISCHARGE is assigned when Discharge Process is created at Location level for a STORAGE PROCESS
        """
        return ['CREDIT', 'STORAGE_DISCHARGE', 'INTERMITTENT']

    # *--------------------------- Automated below this -----------------------------------------

    @classmethod
    def all(cls) -> List[str]:
        """All Process classifications
        """
        return [i.name for i in cls]

    @classmethod
    def process_level(cls) -> List[str]:
        """Set when Process is declared
        """
        return list(set(cls.all()) - set(cls.location_level()))
