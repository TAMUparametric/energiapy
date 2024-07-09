from enum import Enum, auto
from typing import List


class SpecialParameter(Enum):
    """Some special types of parameters
    Generally handled internally. But,
    Can be created externally and given as paramter values
    """
    UNBOUND = auto()
    """When a certain parameter is unbounded
    """
    FACTOR = auto()
    """Created when deterministic data is provided to handle variability
    """
    MPVAR = auto()
    """Created when uncertainty is handle using a parametric variable 
    """
