from enum import Enum, auto


class HorizonType(Enum):
    """Classifies Horizon as having multiple or single scales 
    """
    MULTISCALE = auto()
    """Problem has multiple scales 
    """
    SINGLESCALE = auto()
    """Problem has a single scale  
    """
    NESTED = auto()
    """Disctretizations are nested
    """
    UNNESTED = auto()
    """Discretizations are not nested
    """

    @classmethod
    def all(cls) -> list:
        """All HorizonTypes
        """
        return [i for i in cls]
