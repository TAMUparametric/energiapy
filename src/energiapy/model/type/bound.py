from enum import Enum, auto


class Bound(Enum):
    """Type of boundon parameter
    """
    UNBOUNDED = auto()
    """[SmallM, BigM]. Is unbounded  
    """
    LOWER = auto()
    """[number, BigM]. Has a certain lower bound 
    """
    UPPER = auto()
    """[SmallM, number]. Has a certain upper bound 
    """
    EXACT = auto()
    """number. Has a exact value 
    """
    PARAMETRIC = auto()
    """lies in a range (number, number) or is a Theta object
    """