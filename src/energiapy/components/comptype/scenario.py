from enum import Enum, auto
from typing import List


class ScenarioType(Enum):
    """
    Single location
    """
    SINGLE_LOCATION = auto()
    """
    Multi-location
    """
    MULTI_LOCATION = auto()

    @classmethod
    def all(cls) -> List[str]:
        """All Scenario classifications
        """
        return [i.name for i in cls]
