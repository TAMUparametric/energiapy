
from enum import Enum, auto
from typing import List


class ResourceType(Enum):
    """Class of resource
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
    EMISSION = auto()
    """Emits 
    """

    # * ----------------------------------Update this ------------------------------------------

    @classmethod
    def location_level(cls) -> List[str]:
        """Set when Location is declared
        """
        return ['DEMAND']

    @classmethod
    def transport_level(cls) -> List[str]:
        """Set when Transport is declared
        """
        return ['TRANSPORT']

    # * ---------------------------- Automated below this --------------------------------------

    @classmethod
    def all(cls) -> List[str]:
        """All Resource classifications
        """
        return [i.name for i in cls]

    @classmethod
    def resource_level(cls) -> List[str]:
        """Set when Resource is declared
        """
        return list(set(cls.all()) - set(cls.location_level()) - set(cls.transport_level()))
