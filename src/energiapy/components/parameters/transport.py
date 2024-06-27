from enum import Enum, auto
from typing import Set


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
    def readiness(cls) -> Set[str]:
        """These define the temporal aspects of establishing Transport. Factors not provided for these. 
        """
        return {'INTRODUCE', 'RETIRE', 'LIFETIME'}

    @classmethod
    def failure(cls) -> Set[str]:
        """if this Transport can fail
        """
        return {'P_FAIL'}

    @classmethod
    def uncertain(cls) -> Set[str]:
        """Uncertain parameters, can be handled: 
        1. Multiparametrically by defining as multiparametric variables (energiapy.components.parameters.mpvar.MPVar)
        2. By using factors of deterministic data and via multiperiod scenario analysis 
        """
        exclude_ = {'CAP_MIN'}
        return cls.all() - cls.readiness() - cls.failure() - exclude_

    @classmethod
    def uncertain_factor(cls) -> Set[str]:
        """Uncertain parameters for which factors are defined
        """
        exclude_ = {'TRANS_LOSS', 'LAND'}
        return cls.uncertain() - exclude_

    @classmethod
    def at_scenario(cls) -> Set[str]:
        """Additional parameters to include at scenario
        """
        return cls.all() - {'CAPACITY'} | {'RESOURCES', 'MATERIAL_CONS'}

    # * -------------------------- Automated below this ----------------------------------------

    @classmethod
    def all(cls) -> Set[str]:
        """All Transport paramters
        """
        return {i.name for i in cls}
