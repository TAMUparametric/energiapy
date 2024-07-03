from enum import Enum, auto
from typing import List


class SpatialDisp(Enum):
    """What spatial scale describes the parameter
    Infered from the Component in which the resource
    parameter is declared
    """
    NETWORK = auto()
    LINKAGE = auto()
    TRANSPORT = auto()
    LOCATION = auto()
    PROCESS = auto()


class TemporalDisp(Enum):
    """What temporal scale describes the parameter
    Either inferred from length of deterministic data 
    or needs to be provided
    """
    HORIZON = auto()
    ONE = auto()
    TWO = auto()
    THREE = auto()
    FOUR = auto()
    FIVE = auto()
    SIX = auto()
    SEVEN = auto()
    EIGHT = auto()
    NINE = auto()
    TEN = auto()
    ABOVETEN = auto()

    @classmethod
    def all(cls) -> List[str]:
        return [i for i in cls]
