"""energiapy.components.parameters.paramtype - 

These are enums for the type and subtypes of parameters

Each parameter has a spatiotemporal disposition 
spatial: SpatialDisposition is determined from the Component where the parameter is defined
temporal: TemporalDisposition needs to be provided using the _scale attributes

The parameter could either certain or uncertain (vtype: VariabilityType)
vtypes have substypes:
Certainty subtypes are either some combination of bounds or an exact value
Uncertainty subtypes are parametric, deterministic, stochastic

Special parameters are actual dataclasses: BigM, SmallM, Factor, MPVar/Theta

Finally, 
ptype: ParameterType describes what the parameter models. There are subtypes for each type.
"""

from enum import Enum, auto
# from typing import Set

# from .location import LocationParamType
# from .network import NetworkParamType
# from .process import ProcessParamType
# from .resource import ResourceParamType
# from .transport import TransportParamType

#*-----SpatioTemporal Disposition--------------

class SpatialDisp(Enum):
    """What spatial scale describes the parameter
    Infered from the Component in which the resource
    parameter is declared
    """
    NETWORK = auto()
    LINKAGE = auto()
    TRANSPORT = auto()
    LOCATION = auto()
    PROCESS = auto()


class TemporalDisp(Enum):
    """What temporal scale describes the parameter
    Either inferred from length of deterministic data 
    or needs to be provided
    """
    HORIZON = auto()
    ABOVEDESIGN = auto()
    DESIGN = auto()
    ABOVESCHEDULING = auto()
    SCHEDULING = auto()
    BELOWSCHEDULING = auto()


#*-----Variability------------------


class VariabilityType(Enum):
    """How is the parameter variability accounted for.
    """
    CERTAIN = auto()
    """we know either the exact value or the exact bounds. 
    Subclassed in CertaintyType
    """
    UNCERTAIN = auto()
    """We have some idea of the range, probability, or is accounted by forecasted or historical data.
    Subclassed in UncertaintyType
    """


class CertaintyType(Enum):
    """subclass of ParameterType.Bound
    """
    BOUNDED = auto()
    """ [float, float]. Has a certain upper and lower bound 
    """
    LOWERBOUND = auto()
    """ [float, BigM]. Has a certain lower bound 
    """
    UPPERBOUND = auto()
    """ [0, float]. Has a certain upper bound 
    """
    UNBOUNDED = auto()
    """ [0, BigM]. Has no restricted upper bound
    """
    EXACT = auto()
    """ float. Has a exact value 
    """


class UncertaintyType(Enum):
    """How uncertainty in parameter is handled
    """
    PARAMETRIC = auto()
    """
    (float, float)/Theta i.e. MPVar. Parameteric variable
    """
    DETERMINISTIC = auto()
    """(float, DataFrame)/DataFrame. Uncertain but estimated using a dataset.
    DataFrames are converted to a Factor. A Factor can be provided directly as well. 
    """
    STOCHASTIC = auto()
    """To be worked on  
    """

#*-----Special------------------


class SpecialParamterType(Enum):
    """Some special types of parameters
    Generally handled internally. But,
    Can be created externally and given as paramter values
    """
    BigM = auto()
    """When a certain parameter is unbounded
    """
    SmallM = auto()
    """Used to prevent solution values from blowing up
    """
    FACTOR = auto()
    """Created when deterministic data is provided to handle variability
    """
    MPVar = auto()
    """Created when uncertainty is handle using a parametric variable 
    """

#*-----Paramter types and subtypes------------------


class ParamterType(Enum):
    """What kind of behaviour does the parameter describe
    All of these have subclasses
    These are predetermined by me, Rahul Kakodkar. 
    The BDFO of energiapy
    """
    LIMIT = auto()
    """Helps create boundaries for the problem 
    by setting a min/max or exact limit for flow of Resource.
    """
    CASHFLOW = auto()
    """Expenditure/Revenue.
    """
    LAND = auto()
    """Describes land use and such
    """
    EMISSION = auto()
    """Is an emission.
    """
    LIFE = auto()
    """Describes earliest introduction, retirement, lifetime and such
    """
    LOSS = auto()
    """Amount lost during storage or transport
    """


class LimitType(Enum):
    """What Resource flow is being limited 
    at some spatiotemporal disposition 
    """
    DISCHARGE = auto()
    """Outflow.
    Only lower bound by default
    """
    CONSUME = auto()
    """Inflow 
    """
    STORE = auto()
    """Inventory size 
    """
    CAPACITY = auto()
    """Production capacity
    Set at Process
    """
    TRANSPORT = auto()
    """Export capacity
    Set at Transport
    """


class CashFlowType(Enum):
    """Money going towards or being made from
    """
    SELL_PRICE = auto()
    """Revenue per unit basis of Resource sold
    """
    PURCHASE_PRICE = auto()
    """Expenditure per unit basis of Resource consumed
    """
    STORAGE_COST = auto()
    """Cost of maintaining Resource inventory
    """
    CREDIT = auto()
    """Credit earned from production of Resource
    """
    PENALTY = auto()
    """For unmet demand
    """
    CAPEX = auto()
    FOPEX = auto()
    """Capital and fixed operational expenditure. Scales by Process/Transport capacity
    """
    VOPEX = auto()
    """Variable operational expenditure. Scales by total production from Process/Transport
    """
    INCIDENTAL = auto()
    """Needs to be spent irrespective of Process/Transport capacity
    """
    LAND_COST = auto()
    """Expenditure on acquiring land
    """


class LandType(Enum):
    """Land use or available at spatial scale 
    """
    USE = auto()
    """Exact
    """
    AVAILABLE = auto()
    """Upper bound 
    """


class EmissionType(Enum):
    """Type of emission being considered
    """
    GWP = auto()
    """Global Warming Potential
    """
    ODP = auto()
    """Ozone Depletion Potential
    """
    ACID = auto()
    """Acidification Potential
    """
    EUTT = auto()
    """Terrestrial Eutrophication Potential
    """
    EUTF = auto()
    """Freshwater Eutrophication Potential
    """
    EUTM = auto()
    """Marine Eutrophication Potential
    """


class LifeType(Enum):
    """Constrictes the life of a Process or Transport 
    """
    INTRODUCE = auto()
    """Earliest setup 
    """
    RETIRE = auto()
    """Threshold on keeping active
    """
    LIFETIME = auto()
    """Length of use. Upper bound
    """
    PFAIL = auto()
    """Chance of failure
    """

class LossType(Enum):
    """Resource lost during?
    """
    STORAGE = auto()
    TRANSPORT = auto()

# # # *-----------------------Factor------------------------------------------------

# resource_factors = {
#     f'RESOURCE_{i}' for i in ResourceParamType.uncertain_factor()}
# process_factors = {f'PROCESS_{i}' for i in ProcessParamType.uncertain_factor()}
# location_factors = {
#     f'LOCATION_{i}' for i in LocationParamType.all()}
# transport_factors = {
#     f'TRANSPORT_{i}' for i in TransportParamType.uncertain_factor()}
# network_factors = {f'NETWORK_{i}' for i in NetworkParamType.all()}

# factors = resource_factors | process_factors | \
#     location_factors | transport_factors | network_factors


# class FactorType(Enum):
#     """Type of factor declared to account for uncertainty in Component parameter
#     """

#     @classmethod
#     def all(cls) -> Set[str]:
#         """All factors
#         """
#         return factors

#     @classmethod
#     def resource(cls) -> Set[str]:
#         """Resource factors
#         """
#         return resource_factors

#     @classmethod
#     def process(cls) -> Set[str]:
#         """Process factors
#         """
#         return process_factors

#     @classmethod
#     def location(cls) -> Set[str]:
#         """Location factors
#         """
#         return location_factors

#     @classmethod
#     def transport(cls) -> Set[str]:
#         """Transport factors
#         """
#         return transport_factors

#     @classmethod
#     def network(cls) -> Set[str]:
#         """Network factors
#         """
#         return network_factors


# for i in factors:
#     setattr(FactorType, i, i)


# # *-----------------------Localization ------------------------------------------------

# resource_localizations = {
#     f'RESOURCE_{i}' for i in ResourceParamType.localize()}
# process_localizations = {f'PROCESS_{i}' for i in ProcessParamType.localize()}

# localizations = resource_localizations | process_localizations


# class LocalizationType(Enum):
#     """Localization factor for  Resource and Process provided at Location
#     """
#     @classmethod
#     def all(cls) -> Set[str]:
#         """All localizations
#         """
#         return localizations

#     @classmethod
#     def resource(cls) -> Set[str]:
#         """Resource localizations
#         """
#         return resource_localizations

#     @classmethod
#     def process(cls) -> Set[str]:
#         """Process localizations
#         """
#         return process_localizations


# for i in localizations:
#     setattr(LocalizationType, i, i)


# # *-----------------------Multiparametric Var-----------------------------------------------


# resource_uncertain_params = {
#     f'RESOURCE_{i}' for i in ResourceParamType.uncertain()}
# process_uncertain_params = {
#     f'PROCESS_{i}' for i in ProcessParamType.uncertain()}
# location_uncertain_params = {
#     f'LOCATION_{i}' for i in LocationParamType.all()}
# transport_uncertain_params = {
#     f'TRANSPORT_{i}' for i in TransportParamType.uncertain()}
# network_uncertain_params = {
#     f'NETWORK_{i}' for i in NetworkParamType.all()}

# uncertain_params = resource_uncertain_params | process_uncertain_params | \
#     location_uncertain_params | transport_uncertain_params | network_uncertain_params


# class MPVarType(Enum):
#     """ Type of multiparametric variable created
#     """

#     @classmethod
#     def all(cls) -> Set[str]:
#         """All uncertain parameters
#         """
#         return uncertain_params

#     @classmethod
#     def resource(cls) -> Set[str]:
#         """Resource uncertain parameters
#         """
#         return resource_uncertain_params

#     @classmethod
#     def process(cls) -> Set[str]:
#         """Process uncertain parameters
#         """
#         return process_uncertain_params

#     @classmethod
#     def location(cls) -> Set[str]:
#         """Location uncertain parameters
#         """
#         return location_uncertain_params

#     @classmethod
#     def transport(cls) -> Set[str]:
#         """Transport uncertain parameters
#         """
#         return transport_uncertain_params

#     @classmethod
#     def network(cls) -> Set[str]:
#         """Network uncertain parameters
#         """
#         return network_uncertain_params


# for i in uncertain_params:
#     setattr(MPVarType, i, i)
