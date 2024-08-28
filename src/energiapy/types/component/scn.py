from enum import Enum, auto
from typing import Set


class ScenarioType(Enum):
    SINGLE_LOCATION = auto()
    """
    Single location
    """
    MULTI_LOCATION = auto()
    """
    Multi-location
    """
    REDUCED = auto()

    @classmethod
    def all(cls) -> Set[str]:
        """All Scenario classifications"""
        return {i.name for i in cls}
