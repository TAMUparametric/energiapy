from enum import Enum, auto
from typing import List


class TransportType(Enum):
    """Transport classification
    """
    INTERMITTENT = auto()
    """What cost it incurs
    """
    CAPEX = auto()
    FOPEX = auto()
    VOPEX = auto()
    INCIDENTAL = auto()
    TRANS_LOSS = auto()
    INTRODUCE = auto()
    RETIRE = auto()
    LIFETIME = auto()
    """Temporal behaviour 
    """

    # * -------------------------- Update this ----------------------------------------

    @classmethod
    def all(cls) -> List[str]:
        """All Transport classifications
        """
        return [i.name for i in cls]

    @classmethod
    def network_level(cls) -> List[str]:
        """Set at Network level
        """
        return ['INTERMITTENT']

    # * -------------------------- Automated below this ----------------------------------------

    @classmethod
    def transport_level(cls) -> List[str]:
        """Set when Transport is declared
        """
        return list(set(cls.all()) - set(cls.network_level()))
