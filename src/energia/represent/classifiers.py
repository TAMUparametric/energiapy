"""Model classifiers"""

from enum import Enum


class Uncertainty(Enum):
    """Model uncertainty"""

    DETERMINISTIC = "Deterministic (certain inputs)"
    STOCHASTIC = "Stochastic (random inputs)"
    PARAMETRIC = "Parametric (uncertain parameters)"


class Structure(Enum):
    """Model Mathematical Structure/Order/Variable Types"""

    LINEAR = "Linear"
    NONLINEAR = "Nonlinear"
    INTEGER = "Integer"
    MIXED_INTEGER = "Mixed-Integer"


class Scale(Enum):
    """Model Scale/Order"""

    MULTI = "Multi"
    SINGLE = "Single"


class Paradigm(Enum):
    """Modeling Paradigm"""

    DESIGN = "Design"
    SCHEDULING = "Scheduling"
    CONTROL = "Control"
