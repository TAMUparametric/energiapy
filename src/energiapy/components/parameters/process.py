from enum import Enum, auto
from typing import List


class ProcessParamType(Enum):
    """What class a Procss parameter fit in 
    """
    CAP_MAX = auto()
    CAP_MIN = auto()
    """Bounds to capacity expansion
    """
    LAND = auto()
    """If the process requires land 
    """
    CAPEX = auto()
    FOPEX = auto()
    VOPEX = auto()
    INCIDENTAL = auto()
    """Technology costs to set up processes
    """
    CAPACITY = auto()
    """Amount of the established capacity that can be exercised for production
    """
    CREDIT = auto()
    """If the process is eligible for credit 
    """
    INTRODUCE = auto()
    RETIRE = auto()
    LIFETIME = auto()
    """Temporal behaviour 
    """
    P_FAIL = auto()
    """Probability of failure 
    """

    # *---------------------- Update this -----------------------------------------

    @classmethod
    def readiness(cls) -> List[str]:
        """These define the temporal aspects of establishing processes. Factors not provided for these. 
        """
        return ['INTRODUCE', 'RETIRE', 'LIFETIME', 'P_FAIL']

    @classmethod
    def failure(cls) -> List[str]:
        """if this process can fail
        """
        return ['P_FAIL']

    @classmethod
    def process_level_resource(cls) -> List[str]:
        """Resource parameters that can be declared at Process level
        Do not treat these as Process parameters. 
        In the current list, all of these will be assigned to a STORE type Resource
        """
        return ['STORE_MAX', 'STORE_MIN', 'STORAGE_COST', 'STORE_LOSS']

    @classmethod
    def location_level(cls) -> List[str]:
        """Set when Location is declared
        STORAGE_DISCHARGE is assigned when Discharge Process is created at Location level for a STORAGE PROCESS
        """
        return ['CREDIT', 'CAPACITY']

    @classmethod
    def uncertain(cls) -> List[str]:
        """Uncertain parameters, can be handled: 
        1. Multiparametrically by defining as multiparametric variables (energiapy.components.parameters.mpvar.MPVar)
        2. By using factors of deterministic data and via multiperiod scenario analysis 
        """
        exclude_ = ['CAP_MIN']
        return list(set(cls.all()) - set(cls.readiness()) - set(cls.failure()) - set(cls.process_level_resource()) - set(exclude_))

    @classmethod
    def uncertain_factor(cls) -> List[str]:
        """Uncertain parameters for which factors are defined
        """
        exclude_ = ['LAND']
        return list(set(cls.uncertain()) - set(exclude_))

    @classmethod
    def process_level_uncertain(cls) -> List[str]:
        """Uncertain parameters at Process level
        """
        return list(set(cls.uncertain()) & set(cls.process_level()))

    @classmethod
    def location_level_uncertain(cls) -> List[str]:
        """Uncertain parameters at Location level
        """
        return list(set(cls.uncertain()) & set(cls.location_level()))

    # *------------------ Automated below this------------------------

    @classmethod
    def all(cls) -> List[str]:
        """All parameters
        """
        return [i.name for i in cls]

    @classmethod
    def process_level(cls) -> List[str]:
        """Set when Process is declared
        """
        return list(set(cls.all()) - set(cls.location_level()))

    @classmethod
    def localize(cls) -> List[str]:
        """Process parameters than can be localized 
        """
        return list(set(cls.process_level()) - set(cls.readiness()) - set(cls.failure()) - set(cls.process_level_resource()))
