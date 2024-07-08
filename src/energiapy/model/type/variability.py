from enum import Enum, auto


class Variability(Enum):
    """How is the parameter variability accounted for.
    """
    CERTAIN = auto()
    """we know either the exact value or the exact bounds. 
    Subclassed in Bound
    """
    UNCERTAIN = auto()
    """We have some idea of the range, probability, or is accounted by forecasted or historical data.
    Subclassed in Uncertain
    """

class Uncertain(Enum):
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
