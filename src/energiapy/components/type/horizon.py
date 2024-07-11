from enum import Enum, auto
from typing import List


class HorizonType(Enum):
    """Classifies Horizon as having multiple or single scales 
    """
    MULTI = auto()
    """Problem has multiple scales 
    """
    SINGLE = auto()
    """Problem has a single scale  
    """

    @classmethod
    def all(cls) -> List['HorizonType']:
        """All HorizonTypes
        """
        return [i for i in cls]
