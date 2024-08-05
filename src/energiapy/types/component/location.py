from enum import Enum, auto
from typing import Set


class LocationType(Enum):
    """Location classifications"""

    SOURCE = auto()
    SINK = auto()
    """Whether this is a source or sink
    """
    LAND = auto()
    """Whether land max or land cost has been defined
    """

    # * -------------------------- Update this ----------------------------------------

    @classmethod
    def location_level(cls) -> Set[str]:
        """Set when Location is declared"""
        return {'LAND'}

    # * -------------------------- Automated below this ----------------------------------------

    @classmethod
    def all(cls) -> Set[str]:
        """All Location classifications"""
        return {i.name for i in cls}

    @classmethod
    def network_level(cls) -> Set[str]:
        """Set at Network level"""
        return cls.all() - cls.location_level()
