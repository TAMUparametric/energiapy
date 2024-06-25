from enum import Enum, auto
from typing import List


class ResourceParamType(Enum):
    """Resource Parameters  
    """
    SELL_PRICE = auto()
    """Revenue generated
    """
    PURCHASE_PRICE = auto()
    """Amount spend to consume
    """
    AVAILABILITY = auto()
    """Alias for cons_max, i.e. maximum consumption allowed
    """
    DEMAND = auto()
    """Demand to be met at Location
    """
    STORE_MAX = auto()
    STORE_MIN = auto()
    STORE_LOSS = auto()
    STORAGE_COST = auto()
    """Inventory parameters 
    """

    # * -------------------------- Update this ----------------------------------------

    @classmethod
    def location_level(cls) -> List[str]:
        """Set when Location is declared
        """
        return ['DEMAND']

    @classmethod
    def transport_level(cls) -> List[str]:
        """Set when Transport is declared
        """
        return []

    @classmethod
    def uncertain(cls) -> List[str]:
        """Uncertain parameters, can be handled: 
        1. Multiparametrically by defining as multiparametric variables (energiapy.components.parameters.mpvar.MPVar)
        2. By using factors of deterministic data and via multiperiod scenario analysis 
        """
        exclude_ = ['STORE_MIN']
        return list(set(cls.all()) - set(exclude_))

    @classmethod
    def uncertain_factor(cls) -> List[str]:
        """Uncertain parameters for which factors are defined
        """
        exclude_ = []
        return list(set(cls.uncertain()) - set(exclude_))

    # * -------------------------- Automated below this ----------------------------------------

    @classmethod
    def all(cls) -> List[str]:
        """All Resource paramters
        """
        return [i.name for i in cls]

    @classmethod
    def resource_level(cls) -> List[str]:
        """Set when Resource is declared
        """
        return list(set(cls.all()) - set(cls.location_level()) - set(cls.transport_level()))

    @classmethod
    def localize(cls) -> List[str]:
        """Resource parameters than can be localized 
        """
        return list(set(cls.resource_level()))
