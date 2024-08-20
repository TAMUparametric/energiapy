"""Type of bound a Parameter Value provides
"""

from enum import Enum, auto
from operator import is_


class VarBnd(Enum):
    """Type of Parameter Bound on Variable"""

    LOWER = auto()
    """Is a certain lower bound
    """
    UPPER = auto()
    """Is a certain upper bound
    """
    EXACT = auto()
    """Is an exact value
    """
    FREE = auto()
    """Is unbounded and free <= BigM
    """



class SpcLmt(Enum):
    """Type of bound on parameteric variable (Theta) space"""

    START = auto()
    END = auto()

