"""Describes the approach that will be needed to handle the uncertainty in the parameter.
"""

from enum import Enum, auto


class _Certainty(Enum):
    """How is the parameter variability.
    """
    CERTAIN = auto()
    """we know either the exact value or the exact bounds. 
    Subclassed in Bound
    """
    UNCERTAIN = auto()
    """We have some idea of the range, probability, or is accounted by forecasted or historical data.
    Subclassed in Uncertain
    """


class _Approach(Enum):
    """How uncertainty in parameter is handled
    """
    PARAMETRIC = auto()
    """
    (float, float)/Theta i.e. MPVar. Parameteric variable
    """
    DATA = auto()
    """(float, DataFrame)/DataFrame. Uncertain but estimated using a dataset.
    DataFrames are converted to a Factor. A Factor can be provided directly as well. 
    """
    STOCHASTIC = auto()
    """To be worked on  
    """
