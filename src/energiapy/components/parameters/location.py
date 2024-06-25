from enum import Enum, auto
from typing import List


class LocationParamType(Enum):
    """Location parameters
    """
    LAND_COST = auto()
    LAND_MAX = auto()

    # * -------------------------- Update this ----------------------------------------

    @classmethod
    def network_level(cls) -> List[str]:
        """Set at Network level
        """
        return []

    @classmethod
    def uncertain(cls) -> List[str]:
        """Uncertain parameters, can be handled: 
        1. Multiparametrically by defining as multiparametric variables (energiapy.components.parameters.mpvar.MPVar)
        2. By using factors of deterministic data and via multiperiod scenario analysis 
        """
        exclude_ = []
        return list(set(cls.all()) - set(exclude_))

    # * -------------------------- Automated below this ----------------------------------------

    @classmethod
    def all(cls) -> List[str]:
        """All Location paramters
        """
        return [i.name for i in cls]

    @classmethod
    def location_level(cls) -> List[str]:
        """Set when Location is declared
        """
        return list(set(cls.all()) - set(cls.network_level()))
