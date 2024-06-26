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