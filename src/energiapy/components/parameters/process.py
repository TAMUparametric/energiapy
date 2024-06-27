from enum import Enum, auto
from typing import Set


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
    def readiness(cls) -> Set[str]:
        """These define the temporal aspects of establishing processes. Factors not provided for these. 
        """
        return {'INTRODUCE', 'RETIRE', 'LIFETIME'}

    @classmethod
    def failure(cls) -> Set[str]:
        """if this Process can fail
        """
        return {'P_FAIL'}

    @classmethod
    def process_level_resource(cls) -> Set[str]:
        """Resource parameters that can be declared at Process level
        Do not treat these as Process parameters. 
        In the current list, all of these will be assigned to a STORE type Resource
        """
        return {'STORE_MAX', 'STORE_MIN', 'STORAGE_COST', 'STORE_LOSS'}

    @classmethod
    def location_level(cls) -> Set[str]:
        """Set when Location is declared
        STORAGE_DISCHARGE is assigned when Discharge Process is created at Location level for a STORAGE PROCESS
        """
        return {'CREDIT'}

    @classmethod
    def uncertain(cls) -> Set[str]:
        """Uncertain parameters, can be handled: 
        1. Multiparametrically by defining as multiparametric variables (energiapy.components.parameters.mpvar.MPVar)
        2. By using factors of deterministic data and via multiperiod scenario analysis 
        """
        exclude_ = {'CAP_MIN'}
        return cls.all() - cls.readiness() - cls.failure() - cls.process_level_resource() - exclude_

    @classmethod
    def uncertain_factor(cls) -> Set[str]:
        """Uncertain parameters for which factors are defined
        """
        exclude_ = {'LAND'}
        return cls.uncertain() - exclude_

    @classmethod
    def localize(cls) -> Set[str]:
        """Process parameters than can be localized 
        """
        exclude_ = {'CAPACITY'}
        return cls.process_level() - cls.readiness() - cls.failure() - cls.process_level_resource() - exclude_

    @classmethod
    def at_scenario(cls) -> Set[str]:
        """Additional parameters to include at scenario
        """
        return cls.all() - {'CAPACITY'} | {'CONVERSION', 'MATERIAL_CONS'}

    # *------------------ Automated below this------------------------

    @classmethod
    def process_level_uncertain(cls) -> Set[str]:
        """Uncertain parameters at Process level
        """
        return cls.uncertain() & cls.process_level()

    @classmethod
    def location_level_uncertain(cls) -> Set[str]:
        """Uncertain parameters at Location level
        """
        return cls.uncertain() & cls.location_level()

    @classmethod
    def all(cls) -> Set[str]:
        """All parameters
        """
        return {i.name for i in cls}

    @classmethod
    def process_level(cls) -> Set[str]:
        """Set when Process is declared
        """
        return cls.all() - cls.location_level()
