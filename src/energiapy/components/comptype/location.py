from enum import Enum, auto
from typing import List


class LocationType(Enum):
    """Location classifications
    """
    SOURCE = auto()
    SINK = auto()
    """Whether this is a source or sink
    """
    LAND = auto()
    """Whether land max or land cost has been defined
    """

    # * -------------------------- Update this ----------------------------------------

    @classmethod
    def location_level(cls) -> List[str]:
        """Set when Location is declared
        """
        return ['LAND']

    # * -------------------------- Automated below this ----------------------------------------

    @classmethod
    def all(cls) -> List[str]:
        """All Location classifications
        """
        return [i.name for i in cls]

    @classmethod
    def network_level(cls) -> List[str]:
        """Set at Network level
        """
        return list(set(cls.all()) - set(cls.location_level()))