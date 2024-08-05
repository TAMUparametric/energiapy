from enum import Enum, auto
from typing import Set


class NetworkType(Enum):
    """Network classifications"""

    LAND = auto()

    @classmethod
    def all(cls) -> Set[str]:
        """All Network classifications"""
        return {i.name for i in cls}
