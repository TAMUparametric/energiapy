from enum import Enum, auto
from operator import is_


class Bound(Enum):
    """Type of bound on parameter
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

    def namer(self):
        """gives out a string to put in the name of the parameter
        """
        if is_(self, Bound.LOWER):
            return '_lb'
        elif is_(self, Bound.UPPER):
            return '_ub'
        else:
            return ''
