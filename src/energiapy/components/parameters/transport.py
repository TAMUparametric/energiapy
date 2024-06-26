from enum import Enum, auto
from typing import List


class TransportParamType(Enum):
    """Transport parameters
    """
    CAP_MAX = auto()
    CAP_MIN = auto()
    """Bounds to capacity expansion
    """
    LAND = auto()
    """If the Transport requires land 
    """
    CAPEX = auto()
    FOPEX = auto()
    VOPEX = auto()
    INCIDENTAL = auto()
    """Technology costs to set up Transports
    """
    CAPACITY = auto()
    """Amount of the established capacity that can be exercised for transportation
    """
    TRANS_LOSS = auto()
    """If Resource is lost during transportation
    """
    INTRODUCE = auto()
    RETIRE = auto()
    LIFETIME = auto()
    """Readiness 
    """
    P_FAIL = auto()
    """Probability of failure 
    """
    # * -------------------------- Update this ----------------------------------------

    @classmethod
    def readiness(cls) -> List[str]:
        """These define the temporal aspects of establishing Transport. Factors not provided for these. 
        """
        return ['INTRODUCE', 'RETIRE', 'LIFETIME']

    @classmethod
    def failure(cls) -> List[str]:
        """if this Transport can fail
        """
        return ['P_FAIL']

    @classmethod
    def uncertain(cls) -> List[str]:
        """Uncertain parameters, can be handled: 
        1. Multiparametrically by defining as multiparametric variables (energiapy.components.parameters.mpvar.MPVar)
        2. By using factors of deterministic data and via multiperiod scenario analysis 
        """
        exclude_ = ['CAP_MIN']
        return list(set(cls.all()) - set(cls.readiness()) - set(cls.failure()) - set(exclude_))

    @classmethod
    def uncertain_factor(cls) -> List[str]:
        """Uncertain parameters for which factors are defined
        """
        exclude_ = ['TRANS_LOSS', 'LAND']
        return list(set(cls.uncertain()) - set(exclude_))

    # * -------------------------- Automated below this ----------------------------------------

    @classmethod
    def all(cls) -> List[str]:
        """All Transport paramters
        """
        return [i.name for i in cls]


