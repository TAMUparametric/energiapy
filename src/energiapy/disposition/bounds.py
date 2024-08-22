"""Type of bound a Parameter Value provides
"""

from enum import Enum


class VarBnd(Enum):
    """Type of Parameter Bound on Variable"""

    LB = 'min'
    """Is a certain lower bound
    """
    UB = 'max'
    """Is a certain upper bound
    """
    EQ = ''
    """Is an exact value
    """
    NB = ''
    """Is unbounded and free <= BigM
    """


class SpcLmt(Enum):
    """Type of bound on parameteric variable (Theta) space"""

    START = '('
    END = ')'
