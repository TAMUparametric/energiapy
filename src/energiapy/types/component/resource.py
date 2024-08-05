from enum import Enum, auto
from typing import Set


class ResourceType(Enum):
    """Class of resource"""

    DISCHARGE = auto()
    """can be dispensed
    """
    CONSUME = auto()
    """can be consumed
    """
    SELL = auto()
    """has a selling price
    """
    PURCHASE = auto()
    """has for a purchase cost (price)
    """
    IMPLICIT = auto()
    """Does not enter or leave the system
    """
    PRODUCE = auto()
    """Produced, updated at the Process level
    """
    STORE = auto()
    """stored in inventory, updated at the Storage level
    """
    SILO = auto()
    """has to pass through a silo, updated at the Storage level
    """
    TRANSPORT = auto()
    """can be transported
    """

    # * ----------------------------------Update this ------------------------------------------

    @staticmethod
    def location_level() -> list:
        """Set when Location is declared"""
        return

    @staticmethod
    def transport_level(cls) -> Set[str]:
        """Set when Transit is declared"""
        return {'TRANSPORT'}

    # * ---------------------------- Automated below this --------------------------------------

    @classmethod
    def all(cls) -> Set[str]:
        """All Resource classifications"""
        return {i.name for i in cls}

    @classmethod
    def resource_level(cls) -> Set[str]:
        """Set when Resource is declared"""
        return cls.all() - cls.location_level() - cls.transport_level()
