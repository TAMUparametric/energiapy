from enum import Enum, auto
from typing import List


class NetworkType(Enum):
    """Network classifications
    """
    LAND_MAX = auto()

    @classmethod
    def all(cls) -> List[str]:
        """All Network classifications
        """
        return [i.name for i in cls]
