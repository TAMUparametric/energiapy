from enum import Enum, auto
from typing import Set


class LocationParamType(Enum):
    """Location parameters
    """
    LAND_COST = auto()
    LAND_MAX = auto()

    @classmethod
    def all(cls) -> Set[str]:
        """All Location paramters
        """
        return {i.name for i in cls}


