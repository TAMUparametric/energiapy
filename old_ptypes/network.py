from enum import Enum, auto
from typing import Set


class NetworkParamType(Enum):
    """Network Parameters
    """
    LAND_MAX = auto()

    @classmethod
    def all(cls) -> Set[str]:
        """All Network parameters
        """
        return {i.name for i in cls}

    @classmethod
    def at_scenario(cls) -> Set[str]:
        """Additional parameters to include at scenario
        """
        include_ = {'TRANSPORT_DICT', 'DISTANCE_DICT'}
        return cls.all() | include_
