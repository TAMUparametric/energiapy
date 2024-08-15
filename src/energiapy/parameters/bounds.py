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
    PARAMETRIC = auto()
    """Is a parametric variable
    """
    FREE = auto()
    """Is unbounded and free <= BigM
    """

    def namer(self):
        """gives out a string to put in the name of the parameter"""
        if is_(self, VarBnd.LOWER):
            return ':L'
        elif is_(self, VarBnd.UPPER):
            return ':U'
        else:
            return ''


class SpcLmt(Enum):
    """Type of bound on parameteric variable (Theta) space"""

    START = auto()
    END = auto()

    def namer(self):
        """gives out a string to put in the name of the parameter"""
        if is_(self, SpcLmt.START):
            return ':l'
        if is_(self, SpcLmt.END):
            return ':u'
