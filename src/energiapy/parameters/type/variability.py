from enum import Enum, auto
from typing import List


class VariabilityType(Enum):
    """How is the parameter variability accounted for.
    """
    CERTAIN = auto()
    """we know either the exact value or the exact bounds. 
    Subclassed in CertaintyType
    """
    UNCERTAIN = auto()
    """We have some idea of the range, probability, or is accounted by forecasted or historical data.
    Subclassed in UncertaintyType
    """


class CertaintyType(Enum):
    """subclass of ParameterType.Bound
    """
    BOUNDED = auto()
    """ [float, float]. Has a certain upper and lower bound 
    """
    LOWERBOUND = auto()
    """ [float, BigM]. Has a certain lower bound 
    """
    UPPERBOUND = auto()
    """ [0, float]. Has a certain upper bound 
    """
    UNBOUNDED = auto()
    """ [0, BigM]. Has no restricted upper bound
    """
    EXACT = auto()
    """ float. Has a exact value 
    """


class UncertaintyType(Enum):
    """How uncertainty in parameter is handled
    """
    PARAMETRIC = auto()
    """
    (float, float)/Theta i.e. MPVar. Parameteric variable
    """
    DETERMINISTIC = auto()
    """(float, DataFrame)/DataFrame. Uncertain but estimated using a dataset.
    DataFrames are converted to a Factor. A Factor can be provided directly as well. 
    """
    STOCHASTIC = auto()
    """To be worked on  
    """