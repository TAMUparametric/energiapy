from enum import Enum, auto
from typing import Set


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
    def location_level(cls) -> Set[str]:
        """Set when Location is declared
        """
        return {'DEMAND'}

    @classmethod
    def transport_level(cls) -> Set[str]:
        """Set when Transport is declared
        """
        return set()

    @classmethod
    def uncertain(cls) -> Set[str]:
        """Uncertain parameters, can be handled: 
        1. Multiparametrically by defining as multiparametric variables (energiapy.components.parameters.mpvar.MPVar)
        2. By using factors of deterministic data and via multiperiod scenario analysis 
        """
        exclude_ = {'STORE_MIN'}
        return cls.all() - set(exclude_)

    @classmethod
    def uncertain_factor(cls) -> Set[str]:
        """Uncertain parameters for which factors are defined
        """
        exclude_ = set()
        return cls.uncertain() - set(exclude_)

    @classmethod
    def localize(cls) -> Set[str]:
        """Resource parameters than can be localized 
        """
        exclude_ = set()
        return cls.resource_level() - set(exclude_)

    # * -------------------------- Automated below this ----------------------------------------

    @classmethod
    def all(cls) -> Set[str]:
        """All Resource paramters
        """
        return {i.name for i in cls}

    @classmethod
    def resource_level(cls) -> Set[str]:
        """Set when Resource is declared
        """
        return cls.all() - cls.location_level() - cls.transport_level()
