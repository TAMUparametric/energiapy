""" energiapy.Location - A set of Processes create a Location, required Resources and Materials are inferred 
"""
# TODO - Land MAX constraints
# TODO - Handle materials

# TODO - fix param dict and comp subset


# import operator
# import uuid
from dataclasses import dataclass

# from functools import reduce
# from itertools import product
# from random import sample
# from typing import Dict, List, Set, Tuple, Union

# from pandas import DataFrame

# from .material import Material
# from .process import Process
# from .resource import Resource
# from .temporal_scale import TemporalScale
# from .type.location import LocationType
# from .type.process import ProcessType
# from .type.resource import ResourceType


@dataclass
class Location:
    pass

    # name: str
    # # Primary attributes
    # processes: Set[Process]
    # scales: TemporalScale
    # land: Union[float, Tuple[float], Theta, bool, 'Big'] = None
    # land_cost: Union[float, Tuple[float], Theta] = None
    # # Resource parameters declared at Location
    # discharge: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
    #                  DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    # discharge_over: int = None
    # consume: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
    #                DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    # consume_over: int = None
    # store: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
    #              DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    # store_over: int = None
    # store_loss: Union[float, Tuple[float], Theta] = None
    # store_loss_over: int = None
    # capacity: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
    #                 DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    # transport:  Union[float, bool, 'BigM', List[Union[float, 'BigM']],
    #                   DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    # transport_over: int = None
    # # CashFlowType
    # sell_cost: Union[float, Theta, DataFrame,
    #                  Tuple[Union[float, DataFrame, Factor]]] = None
    # purchase_cost: Union[float, Theta, DataFrame,
    #                      Tuple[Union[float, DataFrame, Factor]]] = None
    # store_cost: Union[float, Theta, DataFrame,
    #                   Tuple[Union[float, DataFrame, Factor]]] = None
    # credit: Union[float, Theta, DataFrame,
    #               Tuple[Union[float, DataFrame, Factor]]] = None
    # penalty: Union[float, Theta, DataFrame,
    #                Tuple[Union[float, DataFrame, Factor]]] = None
    # # Process Parameters
    # conversion: Union[Dict[Union[int, str], Dict[Resource, float]],
    #                   Dict[Resource, float]] = None
    # material_cons: Union[Dict[Union[int, str],
    #                           Dict[Material, float]], Dict[Material, float]] = None
    # capex: Union[float, dict, Tuple[float], Theta] = None
    # pwl: dict = None  # piece wise linear capex
    # fopex: Union[float, Tuple[float], Theta] = None
    # vopex: Union[float, Tuple[float], Theta] = None
    # incidental: Union[float, Tuple[float], Theta] = None
    # land_use: float = None  # Union[float, Tuple[float], Theta]
    # # Details
    # basis: str = None
    # block: str = None
    # label: str = None
    # citation: str = None
    # # Types
    # ctype: List[LocationType] = None
    # # Optional
    # make_subsets: bool = True
    # # Depreciated
    # demand_scale_level: int = None
    # price_scale_level: int = None
    # capacity_scale_level: int = None
    # expenditure_scale_level: int = None
    # availability_scale_level: int = None
    # price_factor: dict = None
    # revenue_factor: dict = None

    # def __post_init__(self):

    #     # *-----------------Set ctype (LocationType)---------------------------------

    #     if not self.ctype:
    #         self.ctype = []

    #     # update ctype if land aspects are defined
    #     if any([self.land, self.land_cost]):
    #         self.ctype.append(LocationType.LAND)

    #     # *-----------------Set aspect (ParameterType) ---------------------------------
    #     # aspects of declared parameters are set to .UNCERTAIN if a MPVar Theta or a tuple of bounds is provided,
    #     # .CERTAIN otherwise
    #     # If empty Theta is provided, the bounds default to (0, 1)

    #     for i in self.aspects():
    #         self.update_location_parameter(parameter=i)

    #     # *-----------------Set ftype (FactorType) ---------------------------------

    #     for i in self.aspects():
    #         self.update_location_factor(parameter=i)

    #     # * ---------------Collect Components (Processes, Resources, Materials) -----------------------
    #     # Resources and Materials are collected based on Process(es) provided

    #     self.processes = self.processes.union({self.create_storage_process(
    #         i) for i in self.processes if ProcessType.STORAGE in i.ctype})

    #     self.resources = reduce(
    #         operator.or_, (i.resources for i in self.processes), set())

    #     self.materials = reduce(
    #         operator.or_, (i.materials for i in self.processes), set())

    #     # * -------------------------- Update Processes ----------------------------------------
    #     # checks if new process parameters have been declared
    #     # Sets new attributes:
    #     #   subsets based on Process.ctype
    #     #   dictionaries with prod_modes, material_modes, etc.

    #     # Update Process parameters provided at Location level
    #     for i in self.location_level_process_parameters():
    #         self.update_component_parameter_declared_at_location(
    #             parameter=i, parameter_type=ProcessParamType)

    #     # update process factors
    #     for i in self.process_factors():
    #         self.update_component_factor(parameter=i)

    #     # update process localizations
    #     for i in self.process_localizations():
    #         self.update_component_localization(i)

    #     # set Process subsets as Location attributes
    #     if self.make_subsets:
    #         for i in self.process_classifications():
    #             self.make_component_subset(
    #                 parameter=i, parameter_type=ProcessType, component_set='processes')

    #     # * -------------------------- Update Resources ----------------------------------------
    #     # check if new resource parameters have been declared
    #     # Sets new attributes:
    #     #   subsets based on Resource.ctype
    #     #   dictionaries with parameter values

    #     # Update Resource ctypes based on information provided at Location

    #     for i in self.location_level_resource_parameters():
    #         self.update_component_parameter_declared_at_location(
    #             parameter=i, parameter_type=ResourceParamType)

    #     # update resource factors
    #     for i in self.resource_factors():
    #         self.update_component_factor(parameter=i)

    #     # update resource localizations
    #     for i in self.resource_localizations():
    #         self.update_component_localization(i)

    #     # set Resource subsets as Location attributes
    #     if self.make_subsets:
    #         for i in self.resource_classifications():
    #             self.make_component_subset(
    #                 parameter=i, parameter_type=ResourceType, component_set='resources')

    #     # *----------------- Depreciation Warnings------------------------------------------

    #     if self.demand_scale_level:
    #         raise ValueError(
    #             f'{self.name}: demand_scale_level is depreciated. scale for meeting demand can be provided in formulate')
    #     if self.price_scale_level:
    #         raise ValueError(
    #             f'{self.name}: price_scale_level is depreciated. scale levels determined from factor data now')
    #     if self.capacity_scale_level:
    #         raise ValueError(
    #             f'{self.name}: capacity_scale_level is depreciated. scale levels determined from factor data now')
    #     if self.expenditure_scale_level:
    #         raise ValueError(
    #             f'{self.name}: expenditure_scale_level is depreciated. scale levels determined from factor data now')
    #     if self.availability_scale_level:
    #         raise ValueError(
    #             f'{self.name}: availability_scale_level is depreciated. scale levels determined from factor data now')
    #     if self.price_factor:
    #         raise ValueError(
    #             f'{self.name}: price_factor is depreciated, use purchase_cost_factor instead')
    #     if self.revenue_factor:
    #         raise ValueError(
    #             f'{self.name}: revenue_factor_scale_level is depreciated, use sell_cost_factor instead')

    # # *----------------- Class Methods -------------------------------------

    # @classmethod
    # def class_name(cls) -> str:
    #     """Returns class name
    #     """
    #     return cls.__name__

    # # * Location parameters

    # @classmethod
    # def aspects(cls) -> Set[str]:
    #     """All Location parameters
    #     """
    #     return LocationParamType.all()

    # # * Location classifications

    # @classmethod
    # def ctypes(cls) -> Set[str]:
    #     """All Location classes
    #     """
    #     return LocationType.all()

    # @classmethod
    # def location_level_classifications(cls) -> Set[str]:
    #     """Set when Location is declared
    #     """
    #     return LocationType.location_level()

    # @classmethod
    # def network_level_classifications(cls) -> Set[str]:
    #     """Set when Location is declared
    #     """
    #     return LocationType.network_level()

    # # * Component Parameters

    # @classmethod
    # def resource_parameters(cls) -> Set[str]:
    #     """All Resource parameters
    #     """
    #     return ResourceParamType.all()

    # @classmethod
    # def process_parameters(cls) -> Set[str]:
    #     """All Process parameters
    #     """
    #     return ProcessParamType.all()

    # # * Location level component classifications

    # @classmethod
    # def resource_classifications(cls) -> Set[str]:
    #     """All Resource classes
    #     """
    #     return ResourceType.resource_level() | ResourceType.location_level()

    # @classmethod
    # def process_classifications(cls) -> Set[str]:
    #     """All Process classes
    #     """
    #     return ProcessType.all()

    # # * Location level component parameters

    # @classmethod
    # def location_level_process_parameters(cls) -> Set[str]:
    #     """Process parameters updated at Location
    #     """
    #     return ProcessParamType.location_level()

    # @classmethod
    # def location_level_resource_parameters(cls) -> Set[str]:
    #     """Resource parameters updated at Location
    #     """
    #     return ResourceParamType.location_level()

    # # * component factors

    # @classmethod
    # def process_factors(cls) -> Set[str]:
    #     """Process factors updated at Location
    #     """
    #     return ProcessParamType.uncertain_factor()

    # @classmethod
    # def resource_factors(cls) -> Set[str]:
    #     """Resource factors updated at Location
    #     """
    #     return ResourceParamType.uncertain_factor()

    # # * component localizations

    # @classmethod
    # def process_localizations(cls) -> Set[str]:
    #     """Process localizations
    #     """
    #     return ProcessParamType.localize()

    # @classmethod
    # def resource_localizations(cls) -> Set[str]:
    #     """Resource localizations
    #     """
    #     return ResourceParamType.localize()

    # # *----------------- Functions-------------------------------------

    # def update_location_parameter(self, parameter: str):
    #     """updates parameter, sets aspect

    #     Args:
    #         parameter (str): parameter to update
    #     """
    #     attr_ = getattr(self, parameter.lower())
    #     if attr_:
    #         aspect_ = getattr(LocationParamType, parameter)
    #         if not self.aspect:
    #             self.aspect = dict()
    #         if isinstance(attr_, (tuple, Theta)):
    #             self.aspect[aspect_] = ParameterType.UNCERTAIN
    #             theta_ = birth_theta(value=attr_, component=self, aspect=getattr(
    #                 MPVarType, f'{self.cname()}_{parameter}'.upper()))
    #             setattr(self, parameter.lower(), theta_)
    #         elif isinstance(attr_, Big) or attr_ is True:
    #             self.aspect[aspect_] = ParameterType.BIGM
    #             if attr_ is True:
    #                 setattr(self, parameter.lower(), BigM)
    #         else:
    #             self.aspect[aspect_] = ParameterType.CERTAIN

    # def update_location_factor(self, parameter: str):
    #     """updates factor, sets ftype

    #     Args:
    #         parameter (str): parameter to update
    #     """
    #     attr_ = getattr(self, f'{parameter}_factor'.lower())
    #     if attr_ is not None:
    #         # aspect_ = getattr(LocationParamType, parameter)
    #         ftype_ = getattr(
    #             FactorType, f'{self.cname()}_{parameter}'.upper())

    #         if not self.ftype:
    #             self.ftype = set()
    #             self.factors = dict()

    #         self.ftype.add(ftype_)
    #         factor_ = Factor(component=self, data=attr_,
    #                          ftype=ftype_, scales=self.scales)
    #         setattr(self, f'{parameter}_factor'.lower(), factor_)
    #         self.factors[ftype_] = factor_

    # def update_component_parameter_declared_at_location(self, parameter: str, parameter_type: Union[ResourceParamType, ProcessParamType]):
    #     """Update the ctype and aspect of component if parameters declared at Location
    #     Note that the aspect and ctype are updated with a tuples, i.e (Location, ____)
    #     Args:
    #         parameter (str): new paramter that has been declared
    #         component_type (Union[ResourceType, ProcessType]): Type of component
    #     """
    #     location_attr = getattr(self, parameter.lower())
    #     if location_attr:
    #         for component in location_attr:  # for each component
    #             # make new attribute in componet to collect data defined at location
    #             if not hasattr(component, parameter.lower()):
    #                 setattr(component, parameter.lower(), dict())
    #             comp_location_attr = getattr(component, parameter.lower())
    #             aspect_ = getattr(parameter_type, parameter)
    #             if isinstance(location_attr[component], (tuple, Theta)):
    #                 append_ = {self: ParameterType.UNCERTAIN}
    #                 theta_ = birth_theta(value=location_attr[
    #                     component], component=component, aspect=getattr(MPVarType, f'{component.class_name()}_{parameter}'.upper()), location=self)
    #                 location_attr[component] = theta_
    #                 comp_location_attr[self] = theta_
    #             else:
    #                 append_ = {self: ParameterType.UNCERTAIN}
    #                 comp_location_attr[self] = location_attr[component]
    #             if not component.aspect:
    #                 component.aspect = dict()
    #             if aspect_ in component.aspect:  # check if already exists, if yes append
    #                 component.aspect[aspect_].update(append_)
    #             else:  # or create new list with tuple
    #                 component.aspect[aspect_] = append_

    # def update_component_ctype_at_location(self, attr: str, ctype: Union[ResourceType, ProcessType]):
    #     """updates ctypes of components based on parameters or factors declared at location

    #     Args:
    #         attr (str): Location attribute name with the required data. Usually a Dict[Component, Union[DataFrame, float, tuple]]
    #         ctype (Union[ResourceType, ProcessType]): the Component type associated with the attr
    #     """
    #     location_attr = getattr(self, attr)
    #     if location_attr:
    #         for component in location_attr:
    #             ctype_dict = [ctype_ for ctype_ in component.ctype if isinstance(
    #                 ctype_, dict) and list(ctype_)[0] == ctype]  # get a list of ctypes that are dictionaries and match the ctype
    #             # if already defined, add Location
    #             if ctype_dict:
    #                 ctype_dict[0][ctype] = ctype_dict[0][ctype] | {
    #                     self}
    #             else:  # else, make a new dictionary for the ctype
    #                 component.ctype.append({ctype: {self}})

    # def update_component_factor(self, parameter: str):
    #     """Checks if a factor for a component has been provided
    #     Creates a Factor from DataFrame data
    #     Updates Componet.factors and Component.ftype

    #     Args:
    #         parameter (str): name of parameter
    #         parameter_type (Union[ResourceParamType, ProcessParamType]): Component parameter type
    #     """
    #     factor_name_ = f'{parameter}_factor'.lower()
    #     attr_ = getattr(self, f'{factor_name_}')
    #     # if factor defined at location
    #     if attr_:
    #         # for each component provided
    #         for j in attr_:
    #             ftype_ = getattr(
    #                 FactorType, f'{j.class_name()}_{parameter}'.upper())
    #             # create the factor
    #             factor_ = Factor(component=j, data=attr_[
    #                 j], ftype=ftype_, scales=self.scales, location=self)
    #             # replace the DataFrame with a Factor
    #             attr_[j] = factor_
    #             # component.ftype and .factors are declared as dict().
    #             # if encountering for the first time, create key and list with the tuple (Location, FactorType/Factor)
    #             if not j.ftype:
    #                 j.ftype, j.factors = dict(), dict()
    #                 j.ftype[ftype_] = {self}
    #                 j.factors[ftype_] = dict()
    #                 j.factors[ftype_][self] = factor_
    #             # if a particular factor for the same component has been declared in another location, then append [(Loc1, ..), (Loc2, ..)]
    #             else:
    #                 if ftype_ in j.ftype:
    #                     # the if statements are to avoid multiple entries if people run the location again
    #                     if self not in j.ftype:
    #                         j.ftype[ftype_].add(self)
    #                     j.factors[ftype_][self] = factor_
    #                 # if this is a new ctype_ being considered, create key and list with tuple (Location, FactorType/Factor)
    #                 else:
    #                     j.ftype[ftype_] = {self}
    #                     if ftype_ not in j.factors:
    #                         j.factors[ftype_] = dict()
    #                     j.factors[ftype_][self] = factor_

    # def update_component_localization(self,  parameter: str):
    #     """Check if a localization has been provided
    #     Creates Localize from data
    #     Updates Component.ltype and Component.localizations

    #     Args:
    #         parameter (str): name of parameter
    #         parameter_type (Union[ResourceParamType, ProcessParamType]): Component parameter type
    #     """
    #     localization_name_ = f'{parameter}_localize'.lower()
    #     attr_ = getattr(self, localization_name_)
    #     # if localize defined at location
    #     if attr_:
    #         # for each component provided
    #         for j in attr_:
    #             ltype_ = getattr(LocalizationType,
    #                              f'{j.class_name()}_{parameter}'.upper())

    #             # calculate localize from data
    #             localization_ = Localization(
    #                 attr_[j], component=j, ltype=ltype_, location=self)

    #             # replace value with Localize object
    #             attr_[j] = localization_

    #             # component.ltype and .localizations are declared as dict()
    #             # if encountering for the first time, create key and list with the tuple (Location, FactorType/Factor)
    #             if not j.ltype:
    #                 j.ltype, j.localizations = dict(), dict()
    #                 j.ltype = dict()
    #                 j.ltype[ltype_] = {self}
    #                 j.localizations[ltype_] = dict()
    #                 j.localizations[ltype_][self] = localization_
    #             # if a particular factor for the same component has been declared in another location, then append [(Loc1, ..), (Loc2, ..)]
    #             else:
    #                 if ltype_ in j.ltype:
    #                     # the if statements are to avoid multiple entries if people run the location again
    #                     if self not in j.ltype:
    #                         j.ltype[ltype_].add(self)
    #                     j.localizations[ltype_][self] = localization_

    #                 # if this is a new ctype_ being considered, create key and list with tuple (Location, FactorType/Factor)
    #                 else:
    #                     j.ltype[ltype_] = {self}
    #                     if ltype_ not in j.localizations:
    #                         j.localizations[ltype_] = dict()
    #                     j.localizations[ltype_][self] = localization_

    # def make_component_subset(self, parameter: str, parameter_type: Union[ResourceType, ProcessType], component_set: str):
    #     """makes a subset of component based on provided ctype
    #     sets the subset as an attribute of the location
    #     if empty set, sets None

    #     Args:
    #         parameter (str): component type
    #         parameter_type (Union[ResourceType, ProcessType]): component classification
    #         component_set (str): set of Processes or Resources
    #     """
    #     ctype_ = getattr(parameter_type, parameter)
    #     component_set_ = getattr(self, component_set)
    #     subset_ = {i for i in component_set_ if ctype_ in i.ctype}
    #     if subset_:
    #         setattr(self, f'{component_set}_{parameter}'.lower(), subset_)
    #     else:
    #         subset_ = {i for i in component_set_ if ctype_ in [
    #             list(j)[0] for j in i.ctype if (isinstance(j, dict))]}
    #         if subset_:
    #             setattr(self, f'{component_set}_{parameter}'.lower(), subset_)

    # def get_cap_bounds(self) -> Union[dict, dict]:
    #     """
    #     makes dictionaries with maximum and minimum capacity bounds
    #     """
    #     cap_max_dict = {}
    #     cap_min_dict = {}
    #     for i in self.processes:
    #         if ProcessType.MULTI_MATMODE in i.ctype:
    #             cap_max_dict[i.name] = {j: None for j in self.scales.scale[0]}
    #             cap_min_dict[i.name] = {j: None for j in self.scales.scale[0]}
    #             for j in self.scales.scale[0]:
    #                 cap_max_dict[i.name][j] = i.cap_max
    #                 cap_min_dict[i.name][j] = i.cap_min
    #         else:
    #             if ProcessType.MULTI_PRODMODE in i.ctype:
    #                 cap_max_dict[i.name] = i.cap_max
    #                 cap_min_dict[i.name] = i.cap_min
    #             else:
    #                 cap_max_dict[i.name] = {
    #                     j: None for j in self.scales.scale[0]}
    #                 cap_min_dict[i.name] = {
    #                     j: None for j in self.scales.scale[0]}
    #                 for j in self.scales.scale[0]:
    #                     cap_max_dict[i.name][j] = i.cap_max
    #                     cap_min_dict[i.name][j] = i.cap_min
    #     return cap_max_dict, cap_min_dict

    # def create_storage_process(self, process) -> Process:
    #     """Creates a discharge process for discharge of stored resource

    #     Args:
    #         process (Process): STORAGE type process
    #     Returns:
    #         Process: Discharge Process
    #     """
    #     if process.capex is None:
    #         capex = None
    #     else:
    #         capex = 0
    #     if process.fopex is None:
    #         fopex = None
    #     else:
    #         fopex = 0
    #     if process.vopex is None:
    #         vopex = None
    #     else:
    #         vopex = 0
    #     if process.incidental is None:
    #         incidental = None
    #     else:
    #         incidental = 0

    #     return Process(name=process.name+'_discharge', conversion=process.conversion_discharge, cap_min=process.cap_min,
    #                    cap_max=process.cap_max, introduce=process.introduce, retire=process.retire, capex=capex, vopex=vopex, fopex=fopex,
    #                    incidental=incidental, lifetime=process.lifetime, label=f'{process.label} (Discharge)', material_cons=None, ctype=[ProcessType.STORAGE_DISCHARGE])

    # # *----------- Hashing --------------------------------

    # def __repr__(self):
    #     return self.name

    # def __hash__(self):
    #     return hash(self.name)

    # def __eq__(self, other):
    #     return self.name == other.name
