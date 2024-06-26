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
    def include_at_scenario(cls) -> List[str]:
        """Additional parameters to include at scenario
        """
        return {'TRANSPORT_DICT', 'DISTANCE_DICT'}
