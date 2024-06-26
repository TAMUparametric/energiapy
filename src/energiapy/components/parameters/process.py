from enum import Enum, auto
from typing import List


class ProcessParamType(Enum):
    """Process parameters
    """
    CAP_MAX = auto()
    CAP_MIN = auto()
    """Bounds to capacity expansion
    """
    LAND = auto()
    """If the Process requires land 
    """
    CAPEX = auto()
    FOPEX = auto()
    VOPEX = auto()
    INCIDENTAL = auto()
    """Technology costs to set up Processes
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
    """Readiness 
    """
    P_FAIL = auto()
    """Probability of failure 
    """

    # *---------------------- Update this -----------------------------------------

    @classmethod
    def readiness(cls) -> List[str]:
        """These define the temporal aspects of establishing processes. Factors not provided for these. 
        """
        return ['INTRODUCE', 'RETIRE', 'LIFETIME']

    @classmethod
    def failure(cls) -> List[str]:
        """if this Process can fail
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
        return ['CREDIT']

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
    def localize(cls) -> List[str]:
        """Process parameters than can be localized 
        """
        exclude_ = ['CAPACITY']
        return list(set(cls.process_level()) - set(cls.readiness()) - set(cls.failure()) - set(cls.process_level_resource()) - set(exclude_))

    # *------------------ Automated below this------------------------

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
