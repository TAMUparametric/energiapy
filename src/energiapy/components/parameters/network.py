from enum import Enum, auto
from typing import List


class NetworkParamType(Enum):
    """Network Parameters
    """
    LAND_MAX = auto()

    @classmethod
    def all(cls) -> List[str]:
        """All Network paramters
        """
        return [i.name for i in cls]

    @classmethod
    def at_scenario(cls) -> List[str]:
        """Additional parameters to include at scenario
        """
        include_ = {'TRANSPORT_DICT', 'DISTANCE_DICT'}
        return list(set(cls.all()) | include_)
