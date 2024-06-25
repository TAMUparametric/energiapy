from enum import Enum, auto
from typing import List


class TransportParamType(Enum):
    """Transport parameters
    """
    CAP_MAX = auto()
    CAP_MIN = auto()
    CAPEX = auto()
    FOPEX = auto()
    VOPEX = auto()
    INCIDENTAL = auto()
    CAPACITY = auto()
    TRANS_LOSS = auto()
    LAND = auto()
    INTRODUCE = auto()
    RETIRE = auto()
    LIFETIME = auto()
    """Temporal behaviour 
    """
    # * -------------------------- Update this ----------------------------------------

    @classmethod
    def all(cls) -> List[str]:
        """All Transport paramters
        """
        return [i.name for i in cls]

    @classmethod
    def network_level(cls) -> List[str]:
        """Set at Network level
        """
        return ['CAPACITY']

    @classmethod
    def temporal(cls) -> List[str]:
        """These define the temporal aspects of establishing processes. Factors not provided for these. 
        """
        return ['INTRODUCE', 'RETIRE', 'LIFETIME']

    @classmethod
    def uncertain(cls) -> List[str]:
        """Uncertain parameters, can be handled: 
        1. Multiparametrically by defining as multiparametric variables (energiapy.components.parameters.mpvar.MPVar)
        2. By using factors of deterministic data and via multiperiod scenario analysis 
        """
        exclude_ = ['CAP_MIN']
        return list(set(cls.all()) - set(cls.temporal()) - set(exclude_))

    @classmethod
    def uncertain_factor(cls) -> List[str]:
        """Uncertain parameters for which factors are defined
        """
        exclude_ = ['TRANS_LOSS', 'LAND']
        return list(set(cls.uncertain()) - set(exclude_))

    # * -------------------------- Automated below this ----------------------------------------

    @classmethod
    def transport_level(cls) -> List[str]:
        """Set when Transport is declared
        """
        return list(set(cls.all()) - set(cls.network_level()))

    @classmethod
    def transport_level_uncertain(cls) -> List[str]:
        """Set when Transport is declared
        """
        return list(set(cls.uncertain()) - set(cls.network_level()))

    @classmethod
    def network_level_uncertain(cls) -> List[str]:
        """Set when Network is declared
        """
        return list(set(cls.uncertain()) - set(cls.transport_level()))
