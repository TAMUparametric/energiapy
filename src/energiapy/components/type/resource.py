
from enum import Enum, auto
from typing import Set


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
    def location_level(cls) -> Set[str]:
        """Set when Location is declared
        """
        return {'DEMAND'}

    @classmethod
    def transport_level(cls) -> Set[str]:
        """Set when Transport is declared
        """
        return {'TRANSPORT'}

    # * ---------------------------- Automated below this --------------------------------------

    @classmethod
    def all(cls) -> Set[str]:
        """All Resource classifications
        """
        return {i.name for i in cls}

    @classmethod
    def resource_level(cls) -> Set[str]:
        """Set when Resource is declared
        """
        return cls.all() - cls.location_level() - cls.transport_level()
