from enum import Enum, auto
from typing import List


class LocationType(Enum):
    """Location classifications
    """
    SOURCE = auto()
    SINK = auto()

    # * -------------------------- Update this ----------------------------------------

    @classmethod
    def network_level(cls) -> List[str]:
        """Set at Network level
        """
        return []


    # * -------------------------- Automated below this ----------------------------------------

    @classmethod
    def all(cls) -> List[str]:
        """All Location classifications
        """
        return [i.name for i in cls]

    @classmethod
    def location_level(cls) -> List[str]:
        """Set when Location is declared
        """
        return list(set(cls.all()) - set(cls.network_level()))
