from enum import Enum, auto
from typing import List
from operator import is_


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
    T0 = auto()
    T1 = auto()
    T2 = auto()
    T3 = auto()
    T4 = auto()
    T5 = auto()
    T6 = auto()
    T7 = auto()
    T8 = auto()
    T9 = auto()
    T10 = auto()
    T10PLUS = auto()

    @classmethod
    def get_tdisp(cls, scale_name: str):
        return [i for i in cls.all() if is_(i.name, scale_name.upper())][0]

    @classmethod
    def all(cls) -> List[str]:
        return [i for i in cls]
