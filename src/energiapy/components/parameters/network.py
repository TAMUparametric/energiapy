from enum import Enum, auto
from typing import List


class NetworkParamType(Enum):
    """Network Parameters
    """
    LAND_MAX = auto()

    @classmethod
    def all(cls) -> List[str]:
        """All Network paramters
        """
        return [i.name for i in cls]

    @classmethod
    def uncertain(cls) -> List[str]:
        """Uncertain parameters, can be handled: 
        1. Multiparametrically by defining as multiparametric variables (energiapy.components.parameters.mpvar.MPVar)
        2. By using factors of deterministic data and via multiperiod scenario analysis 
        """
        exclude_ = []
        return list(set(cls.all()) - set(exclude_))

    @classmethod
    def uncertain_factor(cls) -> List[str]:
        """Uncertain parameters for which factors are defined
        """
        exclude_ = []
        return list(set(cls.uncertain()) - set(exclude_))
