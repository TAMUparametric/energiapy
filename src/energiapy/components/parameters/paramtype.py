"""energiapy.components.parameters.paramtype - Type of paramter, factor, multiparameteric variable, localization
"""
from enum import Enum, auto
from typing import List

from .location import LocationParamType
from .network import NetworkParamType
from .process import ProcessParamType
from .resource import ResourceParamType
from .transport import TransportParamType


# *-----------------------Parameter-------------------------------------------------


class ParameterType(Enum):
    """How does a component parameter vary?
    """
    CERTAIN = auto()
    """Is certain. Does not change over the design or scheduling scale
    """
    UNCERTAIN = auto()
    """Declared as a parametric variable (energiapy.components.parameters.mpvars.Theta)
    or provided as a range using tuple
    """

# # *-----------------------Factor------------------------------------------------


resource_factors = [
    f'RESOURCE_{i}' for i in ResourceParamType.uncertain_factor()]
process_factors = [f'PROCESS_{i}' for i in ProcessParamType.uncertain_factor()]
location_factors = [
    f'LOCATION_{i}' for i in LocationParamType.uncertain_factor()]
transport_factors = [
    f'TRANSPORT_{i}' for i in TransportParamType.uncertain_factor()]
network_factors = [f'NETWORK_{i}' for i in NetworkParamType.uncertain_factor()]

factors = resource_factors + process_factors + \
    location_factors + transport_factors + network_factors


class FactorType(Enum):
    """Type of factor declared to account for uncertainty in Component parameter
    """

    @classmethod
    def all(cls) -> List[str]:
        """All factors
        """
        return factors

    @classmethod
    def resource_factors(cls) -> List[str]:
        """Resource factors
        """
        return resource_factors

    @classmethod
    def process_factors(cls) -> List[str]:
        """Process factors
        """
        return process_factors

    @classmethod
    def location_factors(cls) -> List[str]:
        """Location factors
        """
        return location_factors

    @classmethod
    def transport_factors(cls) -> List[str]:
        """Transport factors
        """
        return transport_factors

    @classmethod
    def network_factors(cls) -> List[str]:
        """Network factors
        """
        return network_factors


for i in factors:
    setattr(FactorType, i, auto())

# *-----------------------Localization ------------------------------------------------

resource_localizations = [
    f'RESOURCE_{i}' for i in ResourceParamType.localize()]
process_localizations = [f'PROCESS_{i}' for i in ProcessParamType.localize()]

localizations = resource_localizations + process_localizations


class LocalizationType(Enum):
    """Localization factor for  Resource and Process provided at Location
    """
    @classmethod
    def all(cls) -> List[str]:
        """All localizations
        """
        return localizations

    @classmethod
    def resource_localizations(cls) -> List[str]:
        """Resource localizations
        """
        return resource_localizations

    @classmethod
    def process_localizations(cls) -> List[str]:
        """Process localizations
        """
        return process_localizations


for i in localizations:
    setattr(LocalizationType, i, auto())

# *-----------------------Multiparametric Var-----------------------------------------------


resource_uncertain_params = [
    f'RESOURCE_{i}' for i in ResourceParamType.uncertain()]
process_uncertain_params = [
    f'PROCESS_{i}' for i in ProcessParamType.uncertain()]
location_uncertain_params = [
    f'LOCATION_{i}' for i in LocationParamType.uncertain()]
transport_uncertain_params = [
    f'TRANSPORT_{i}' for i in TransportParamType.uncertain()]
network_uncertain_params = [
    f'NETWORK_{i}' for i in NetworkParamType.uncertain()]

uncertain_params = resource_uncertain_params + process_uncertain_params + \
    location_uncertain_params + transport_uncertain_params + network_uncertain_params


class MPVarType(Enum):
    """ Type of multiparametric variable created
    """

    @classmethod
    def all(cls) -> List[str]:
        """All uncertain parameters
        """
        return uncertain_params

    @classmethod
    def resource_uncertain_params(cls) -> List[str]:
        """Resource uncertain parameters
        """
        return resource_uncertain_params

    @classmethod
    def process_uncertain_params(cls) -> List[str]:
        """Process uncertain parameters
        """
        return process_uncertain_params

    @classmethod
    def location_uncertain_params(cls) -> List[str]:
        """Location uncertain parameters
        """
        return location_uncertain_params

    @classmethod
    def transport_uncertain_params(cls) -> List[str]:
        """Transport uncertain parameters
        """
        return transport_uncertain_params

    @classmethod
    def network_uncertain_params(cls) -> List[str]:
        """Network uncertain parameters
        """
        return network_uncertain_params


for i in uncertain_params:
    setattr(MPVarType, i, auto())
