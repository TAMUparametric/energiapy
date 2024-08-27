"""Type of bound a Parameter Value provides
"""

from enum import Enum


class VarBnd(Enum):
    """Type of Parameter Bound on Variable"""

    LB = '^min'
    """Is a certain lower bound
    """
    UB = '^max'
    """Is a certain upper bound
    """
    EQ = ''
    """Is an exact value
    """


class SpcLmt(Enum):
    """Type of bound on parameteric variable (Theta) space"""

    START = '^lb'
    END = '^ub'
    NOT = ''
