from enum import Enum, auto
from typing import List


class ScaleType(Enum):
    """Classifies problem as having multiple or single scales  for decision making
    """
    MULTI = auto()
    """Problem has multiple scales 
    """
    SINGLE = auto()
    """Problem has a single scale  
    """

    @classmethod
    def all(cls) -> List[str]:
        """All Temporal classifications
        """
        return [i.name for i in cls]
