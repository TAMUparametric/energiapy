from enum import Enum, auto
from typing import List


class Condition(Enum):
    """Rule for constraint generation
    """
    BIND = auto()
    """Binds a variable to parameter bounds
    var <= ub or var >= lb 
    """
    CAPACITATE = auto()
    """Limits variable to capacity of Process or Transport
    """
    CALCULATE = auto()
    """Finds variable value by multiplying a parameter with another variable
    var = param * var2
    """
    SUMOVER = auto()
    """Finds variable value by summing associated variable over time, space, or mode
    """
    BALANCE = auto()
    """Balances multiple variables
    var1(c,s,t) + var2(c,s,t) - var3(c,s,t) = 0 
    """

class RightHandSide(Enum):
    """Binds a variable to a(n)
    Can be multiplicative, e.g.: var <= param * var2 
    """
    PARAMETER = auto()
    """parameter
    """
    CONTINUOUS = auto()
    """continuous variable
    """
    INTEGER = auto()
    """integer variable
    """
    

class SumOver(Enum):
    """Sum type
    """
    TIME = auto()
    """Finds variable value by summing associated variable over time
    var(s,t) = sum(var(s,t-1))
    """
    SPACE = auto()
    """Finds variable value by summing associated variable over space
    var(s,t) = sum(var(s-1,t))
    """
    MODE = auto()
    """Balances binary modes
    x(0,1) + x(0,2) + x(0,3) = x(0)
    """
    
