""" energiapy.Location - A set of Processes create a Location, required Resources and Materials are inferred 
"""
# TODO - Land MAX constraints
# TODO - Handle materials

# TODO - fix param dict and comp subset


import operator
import uuid
from dataclasses import dataclass
from functools import reduce
from itertools import product
from random import sample
from typing import Dict, List, Set, Tuple, Union

from pandas import DataFrame

from .comptype.location import LocationType
from .comptype.process import ProcessType
from .comptype.resource import ResourceType
from .material import Material
from .parameters.factor import Factor
from .parameters.localization import Localization
from .parameters.location import LocationParamType
from .parameters.mpvar import Theta, create_mpvar
from .parameters.paramtype import (FactorType, LocalizationType, MPVarType,
                                   ParameterType)
from .parameters.process import ProcessParamType
from .parameters.resource import ResourceParamType
from .process import Process
from .resource import Resource
from .temporal_scale import TemporalScale


@dataclass
class Location:
    """Location is essentially a set of processes. 

    If using deterministic data to account for variability in Process, Resource, or Location parameters
    appropriate factors can be provided. A Factor object is created which set the scale by matching the length to an available scale type 

    Resources which have a specific demand at Location can also be provided as a dict {Resource: float}

    Factors for Resource include: demand, purchase_price, sell_price, availability (varies cons_max)
                Process include: capacity, expenditures (capex, fopex, vopex, incidental), credit 
                Location include: land_cost

    For a multiscale problem capacity_factor will be applied to the decision variable Cap_P (capacity of Process)

    Localizations can be also be provided for all the parameters above. Note that for capacity, cap_max and cap_min are are different

    Land cost can also be provided, as well as a factor to vary it

    Credits earned by Process based on the production can be provided as {Process: float}. Be careful to use the emission Resource as the basis
    A credit factor can also be provided 

    Args:
        name (str): name of the location. Enter None to randomly assign a name.
        processes (Set[Process]): set of processes (Process objects) to include at location
        scales (TemporalScale): temporal scales of the problem
        land_max (Union[float, Tuple[float], Theta], optional): land available. Defaults to None.
        land_cost (Union[float, Tuple[float], Theta], optional): cost of land. Defaults to None.
        land_max_factor (DataFrame, optional): factor for changing land availability. Defaults to None. 
        land_cost_factor (DataFrame, optional): factor for changing land cost. Defaults to None. 
        demand (Dict[Resource, Union[float, Tuple[float], Theta]]): demand for resources at location. Defaults to None.
        sell_price_factor (Dict[Resource, DataFrame], optional): Factor for varying resource revenue. Defaults to None.
        purchase_price_factor (Dict[Resource, DataFrame], optional): Factor for varying cost. Defaults to None.
        cons_max_factor (Dict[Resource, DataFrame], optional): Factor for varying resource availability. Defaults to None.
        demand_factor (Dict[Resource, DataFrame], optional): Factor for varying demand. Defaults to None.
        store_max_factor (Dict[Resource, DataFrame], optional): Factor for maximum inventory capacity. Defaults to None.
        store_loss_factor (Dict[Resource, DataFrame], optional): Factor for loss of resource in inventory. Defaults to None.
        storage_cost_factor (Dict[Resource, DataFrame], optional): Factor for cost of maintaining inventory. Defaults to None.
        credit (Dict[Process, float], optional): credit earned by process per unit basis. Defaults to None.
        capacity_factor (Dict[Process, DataFrame], optional):  Factor for varying capacity in schedule.Defaults to None.
        cap_max_factor (Dict[Process, DataFrame], optional):  Factor for maximum allowed capacity expansion.Defaults to None.
        capex_factor (Dict[Process, DataFrame], optional):  Factor for varying capital expenditure. Defaults to None.
        vopex_factor (Dict[Process, DataFrame], optional):  Factor for varying variable operational expenditure. Defaults to None.
        fopex_factor (Dict[Process, DataFrame], optional):  Factor for varying fixed operational expenditure. Defaults to None.
        incidental_factor (Dict[Process, DataFrame], optional):  Factor for varying incidental expenditure. Defaults to None.
        credit_factor (Dict[Process, DataFrame], optional): factor for credit. Defaults to None.        
        sell_price_localize (Dict[Resource, Tuple[float, int]] , optional): Localization factor for selling price. Defaults to None.
        purchase_price_localize (Dict[Resource, Tuple[float, int]] , optional): Localization factor for purchase price. Defaults to None.
        cons_max_localize (Dict[Resource, Tuple[float, int]] , optional): Localization factor for availability. Defaults to None.
        store_max_localize (Dict[Resource, DataFrame], optional): Localization factor for maximum inventory capacity. Defaults to None.
        store_min_localize (Dict[Resource, DataFrame], optional): Localization factor for minimum inventory capacity. Defaults to None.
        store_loss_localize (Dict[Resource, DataFrame], optional): Localization factor for loss of resource in inventory. Defaults to None.
        storage_cost_localize (Dict[Resource, DataFrame], optional): Localization factor for cost of maintaining inventory. Defaults to None.
        cap_max_localize (Dict[Process, Tuple[float, int]] , optional): Localization factor for maximum capacity. Defaults to None.
        cap_min_localize (Dict[Process, Tuple[float, int]] , optional): Localization factor for minimum capacity. Defaults to None.
        capex_localize (Dict[Process, Tuple[float, int]] , optional): Localization factor for capex. Defaults to None.
        vopex_localize (Dict[Process, Tuple[float, int]] , optional): Localization factor for vopex. Defaults to None.
        fopex_localize (Dict[Process, Tuple[float, int]] , optional): Localization factor for fopex. Defaults to None.
        incidental_localize(Dict[Process, Tuple[float, int]] , optional): Localization factor for incidental. Defaults to None.
        incidental_localize(Dict[Process, Tuple[float, int]] , optional): Localization factor for land. Defaults to None.
        basis (str, optional): unit in which land area is measured. Defaults to None.
        block (Union[str, list, dict], optional): block to which it belong. Convinient to set up integer cuts. Defaults to None.
        label (str, optional): used while generating plots. Defaults to None.
        citation (str, optional): can provide citations for your data sources. Defaults to None.
        ctype (List[LocationType], optional): Location type. Defaults to None.
        ptype (Dict[LocationParamType, ParameterType], optional): paramater type of declared values. Defaults to None.
        ftype (Dict[LocationParamType, FactorType], optional): factor type of declared factors. Defaults to None.
        factors (Dict[LocationParamType, Factor], optional): collection of factors defined at Location. Defaults to None.

    Examples:
        Locations need a set of processes and the scale levels for demand, capacity, and cost, and if applicable demand factors, price_factors, capacity factors

        >>> Goa= Location(name='Goa', processes= {Process1, Process2}, demand_scale_level=2, capacity_scale_level= 2, price_scale_level= 1, demand_factor= {Resource1: DataFrame,}, price_factor = {Resource2: DataFrame}, capacity_factor = {Process1: DataFrame}, scales= TemporalScale object, label='Home')
    """

    name: str
    # Primary attributes
    processes: Set[Process]
    scales: TemporalScale
    land_max: Union[float, Tuple[float], Theta] = None
    land_cost: Union[float, Tuple[float], Theta] = None
    land_max_factor: DataFrame = None
    land_cost_factor: DataFrame = None
    # Resource parameters declared at Location
    demand: Dict[Resource, Union[float, Tuple[float], Theta]] = None
    # Factors for Resource parameter variability. cons_max_factor has alias availability_factor
    sell_price_factor: Dict[Resource, DataFrame] = None
    purchase_price_factor: Dict[Resource, DataFrame] = None
    cons_max_factor: Dict[Resource, DataFrame] = None
    demand_factor: Dict[Resource, DataFrame] = None
    store_max_factor: Dict[Resource, DataFrame] = None
    store_loss_factor: Dict[Resource, DataFrame] = None
    storage_cost_factor: Dict[Resource, DataFrame] = None
    # Process parameters declared at Location
    credit: Dict[Process, Union[float, Tuple[float], Theta]] = None
    # Factors for Process parameter variability
    capacity_factor: Dict[Process, DataFrame] = None
    cap_max_factor: Dict[Process, DataFrame] = None
    capex_factor: Dict[Process, DataFrame] = None
    vopex_factor: Dict[Process, DataFrame] = None
    fopex_factor: Dict[Process, DataFrame] = None
    incidental_factor: Dict[Process, DataFrame] = None
    credit_factor: Dict[Process, DataFrame] = None
    # Localizations for Resource parameters.
    sell_price_localize: Dict[Resource, Tuple[float, int]] = None
    purchase_price_localize: Dict[Resource, Tuple[float, int]] = None
    cons_max_localize: Dict[Resource, Tuple[float, int]] = None
    store_max_localize: Dict[Resource, Tuple[float, int]] = None
    store_min_localize: Dict[Resource, Tuple[float, int]] = None
    store_loss_localize: Dict[Resource, Tuple[float, int]] = None
    storage_cost_localize: Dict[Resource, Tuple[float, int]] = None
    # Localizations for Process parameters
    cap_max_localize: Dict[Process, Tuple[float, int]] = None
    cap_min_localize: Dict[Process, Tuple[float, int]] = None
    capex_localize: Dict[Process, Tuple[float, int]] = None
    vopex_localize: Dict[Process, Tuple[float, int]] = None
    fopex_localize: Dict[Process, Tuple[float, int]] = None
    incidental_localize: Dict[Process, Tuple[float, int]] = None
    land_localize: Dict[Process, Tuple[float, int]] = None
    # Details
    basis: str = None
    block: str = None
    label: str = None
    citation: str = None
    # Types
    ctype: List[LocationType] = None
    ptype: Dict[LocationParamType, ParameterType] = None
    ftype: Dict[LocationParamType, FactorType] = None
    # Collections
    factors: Dict[LocationParamType, Factor] = None
    # Depreciated
    demand_scale_level: int = None
    price_scale_level: int = None
    capacity_scale_level: int = None
    expenditure_scale_level: int = None
    availability_scale_level: int = None
    price_factor: dict = None
    revenue_factor: dict = None

    def __post_init__(self):

        # *-----------------Set ctype (LocationType)---------------------------------

        if not self.ctype:
            self.ctype = list()
            
        # update ctype if land aspects are defined
        if any([self.land_max, self.land_cost]):
            self.ctype.append(LocationType.LAND)

        # *-----------------Set ptype (ParameterType) ---------------------------------
        # ptypes of declared parameters are set to .UNCERTAIN if a MPVar Theta or a tuple of bounds is provided,
        # .CERTAIN otherwise
        # If empty Theta is provided, the bounds default to (0, 1)

        self.ptype = dict()

        for i in self.ptypes():
            self.update_location_parameter(parameter=i)

        # *-----------------Set ftype (FactorType) ---------------------------------

        self.ftype, self.factors = dict(), dict()

        for i in self.ptypes():
            self.update_location_factor(parameter=i)

        # * ---------------Collect Components (Processes, Resources, Materials) -----------------------
        # Resources and Materials are collected based on Process(es) provided

        self.processes = self.processes.union({self.create_storage_process(
            i) for i in self.processes if ProcessType.STORAGE in i.ctype})
        
        self.resources = reduce(operator.or_, (i.resources for i in self.processes), set())
        
        self.materials = reduce(operator.or_, (i.materials for i in self.processes), set())
        
        # * -------------------------- Update Processes ----------------------------------------
        # checks if new process parameters have been declared
        # Sets new attributes:
        #   subsets based on Process.ctype
        #   dictionaries with prod_modes, material_modes, etc.

        # Update Process parameters provided at Location level
        if self.credit is not None:
            for i in self.credit:
                i.ctype.append((self, ProcessType.CREDIT))

        if self.capacity_factor is not None:
            for i in self.capacity_factor:
                i.ctype.append((self, ProcessType.INTERMITTENT))

        for i in self.location_level_process_parameters():
            self.update_component_parameter_declared_at_location(
                parameter=i, parameter_type=ProcessParamType)

        # set Process subsets as Location attributes
        for i in self.process_classifications():
            self.make_component_subset(parameter= i, parameter_type=ProcessType, component_set= 'processes')

        # update process factors
        for i in self.process_factors():
            self.update_component_factor(i, ProcessParamType)

        # update process localizations
        for i in self.process_localizations():
            self.update_component_localization(i, ProcessParamType)

        # * -------------------------- Update Resources ----------------------------------------
        # check if new resource parameters have been declared
        # Sets new attributes:
        #   subsets based on Resource.ctype
        #   dictionaries with parameter values

        if self.demand is not None:
            for i in self.demand:
                i.ctype.append((self, ResourceType.DEMAND))

        for i in self.location_level_resource_parameters():
            self.update_component_parameter_declared_at_location(
                parameter=i, parameter_type=ResourceParamType)

        # set Resource subsets as Location attributes
        for i in self.resource_classifications():
            self.make_component_subset(parameter= i, parameter_type=ResourceType, component_set= 'resources')

        # update resource factors
        for i in self.resource_factors():
            self.update_component_factor(i, ResourceParamType)

        # update resource localizations
        for i in self.resource_localizations():
            self.update_component_localization(i, ResourceParamType)

        # *----------------- Generate Random Name -------------------------------------------
        # A random name is generated if self.name = None
        if self.name is None:
            self.name = f'{self.class_name()}_{uuid.uuid4().hex}'

        # *----------------- Depreciation Warnings------------------------------------------

        if self.demand_scale_level is not None:
            raise ValueError(
                f'{self.name}: demand_scale_level is depreciated. scale for meeting demand can be provided in formulate')
        if self.price_scale_level is not None:
            raise ValueError(
                f'{self.name}: price_scale_level is depreciated. scale levels determined from factor data now')
        if self.capacity_scale_level is not None:
            raise ValueError(
                f'{self.name}: capacity_scale_level is depreciated. scale levels determined from factor data now')
        if self.expenditure_scale_level is not None:
            raise ValueError(
                f'{self.name}: expenditure_scale_level is depreciated. scale levels determined from factor data now')
        if self.availability_scale_level is not None:
            raise ValueError(
                f'{self.name}: availability_scale_level is depreciated. scale levels determined from factor data now')
        if self.price_factor is not None:
            raise ValueError(
                f'{self.name}: price_factor is depreciated, use purchase_price_factor instead')
        if self.revenue_factor is not None:
            raise ValueError(
                f'{self.name}: revenue_factor_scale_level is depreciated, use sell_price_factor instead')

    # *----------------- Properties ---------------------------------

    @property
    def availability_factor(self):
        """Sets alias for cons_max_factor
        """
        return self.cons_max_factor

    @property
    def availability_localize(self):
        """Sets alias for cons_max_localize
        """
        return self.cons_max_localize

    # *----------------- Class Methods -------------------------------------

    @classmethod
    def class_name(cls) -> List[str]:
        """Returns class name 
        """
        return cls.__name__

    # * Location parameters

    @classmethod
    def ptypes(cls) -> List[str]:
        """All Location paramters
        """
        return LocationParamType.all()

    # * Location classifications

    @classmethod
    def ctypes(cls) -> List[str]:
        """All Location classes
        """
        return LocationType.all()

    @classmethod
    def location_level_classifications(cls) -> List[str]:
        """Set when Location is declared
        """
        return LocationType.location_level()

    @classmethod
    def network_level_classifications(cls) -> List[str]:
        """Set when Location is declared
        """
        return LocationType.network_level()

    # * Component Parameters

    @classmethod
    def resource_parameters(cls) -> List[str]:
        """All Resource paramters
        """
        return ResourceParamType.all()

    @classmethod
    def process_parameters(cls) -> List[str]:
        """All Process paramters
        """
        return ProcessParamType.all()

    # * Location level component classifications

    @classmethod
    def resource_classifications(cls) -> List[str]:
        """All Resource classes
        """
        return ResourceType.all()

    @classmethod
    def process_classifications(cls) -> List[str]:
        """All Process classes
        """
        return ProcessType.all()

    # * Location level component parameters

    @classmethod
    def location_level_process_parameters(cls) -> List[str]:
        """Process parameters updated at Location
        """
        return ProcessParamType.location_level()

    @classmethod
    def location_level_resource_parameters(cls) -> List[str]:
        """Resource parameters updated at Location
        """
        return ResourceParamType.location_level()

    # * component factors

    @classmethod
    def process_factors(cls) -> List[str]:
        """Process factors updated at Location
        """
        return ProcessParamType.uncertain_factor()

    @classmethod
    def resource_factors(cls) -> List[str]:
        """Resource factors updated at Location
        """
        return ResourceParamType.uncertain_factor()

    # * component localizations

    @classmethod
    def process_localizations(cls) -> List[str]:
        """Process localizations 
        """
        return ProcessParamType.localize()

    @classmethod
    def resource_localizations(cls) -> List[str]:
        """Resource localizations 
        """
        return ResourceParamType.localize()

    # *----------------- Functions-------------------------------------

    def update_location_parameter(self, parameter: str):
        """updates parameter, sets ptype

        Args:
            parameter (str): parameter to update 
        """
        attr_ = getattr(self, parameter.lower())
        if attr_ is not None:
            ptype_ = getattr(LocationParamType, parameter)
            if isinstance(attr_, (tuple, Theta)):
                self.ptype[ptype_] = ParameterType.UNCERTAIN
                mpvar_ = create_mpvar(value=attr_, component=self, ptype=getattr(
                    MPVarType, f'{self.class_name()}_{parameter}'.upper()))
                setattr(self, parameter.lower(), mpvar_)
            else:
                self.ptype[ptype_] = ParameterType.CERTAIN

    def update_location_factor(self, parameter: str):
        """updates factor, sets ftype

        Args:
            parameter (str): parameter to update 
        """
        attr_ = getattr(self, f'{parameter}_factor'.lower())
        if attr_ is not None:
            ptype_ = getattr(LocationParamType, parameter)
            ftype_ = getattr(
                FactorType, f'{self.class_name()}_{parameter}'.upper())
            self.ftype[ptype_] = ftype_
            factor_ = Factor(component=self, data=attr_,
                             ftype=ftype_, scales=self.scales)
            setattr(self, f'{parameter}_factor'.lower(), factor_)
            self.factors[f'{parameter}_factor'.lower()] = factor_

    def update_component_parameter_declared_at_location(self, parameter: str, parameter_type: Union[ResourceParamType, ProcessParamType]):
        """Update the ctype and ptype of component if parameters declared at Location
        Note that the ptype and ctype are updated with a tuples, i.e (Location, ____)
        Args:
            parameter (str): new paramter that has been declared 
            component_type (Union[ResourceType, ProcessType]): Type of component
        """
        attr_ = getattr(self, parameter.lower())
        if attr_ is not None:
            for i in attr_:  # for each component
                if not hasattr(i, parameter.lower()): # make new attribute in componet to collect data defined at location
                    setattr(i, parameter.lower(), dict())
                comp_attr_ = getattr(i, parameter.lower())
                ptype_ = getattr(parameter_type, parameter)
                if isinstance(attr_[i], (tuple, Theta)):
                    append_ = (self, ParameterType.UNCERTAIN)
                    mpvar_ = create_mpvar(value=attr_[
                                          i], component=i, ptype=getattr(MPVarType, f'{i.class_name()}_{parameter}'.upper()), location=self)
                    attr_[i] = mpvar_
                    comp_attr_[self] = mpvar_
                else:
                    append_ = (self, ParameterType.CERTAIN)
                    comp_attr_[self] = attr_[i]
                if ptype_ in i.ptype:  # check if already exists, if yes append
                    i.ptype[ptype_].append(append_)
                else:  # or create new list with tuple
                    i.ptype[ptype_] = [append_]

    def update_component_factor(self, parameter: str, parameter_type: Union[ResourceParamType, ProcessParamType]):
        """Checks if a factor for a component has been provided
        Creates a Factor from DataFrame data
        Updates Componet.factors and Component.ftype

        Args:
            parameter (str): name of parameter
            parameter_type (Union[ResourceParamType, ProcessParamType]): Component parameter type
        """

        factor_name_ = f'{parameter}_factor'.lower()
        attr_ = getattr(self, factor_name_)
        # if factor defined at location
        if attr_ is not None:
            # for each component provided
            ptype_ = getattr(parameter_type, parameter)
            for j in attr_:
                ftype_ = getattr(
                    FactorType, f'{j.class_name()}_{parameter}'.upper())
                # create the factor
                factor_ = Factor(component=j, data=attr_[
                    j], ftype=ftype_, scales=self.scales, location=self)
                # replace the DataFrame with a Factor
                attr_[j] = factor_
                # component.ftype and .factors are declared as dict().
                # if encountering for the first time, create key and list with the tuple (Location, FactorType/Factor)
                if not j.ftype:
                    j.ftype, j.factors = dict(), dict()
                    j.ftype[ptype_] = [(self, ftype_)] 
                    j.factors[factor_name_] = dict()
                    j.factors[factor_name_][self] = factor_
                # if a particular factor for the same component has been declared in another location, then append [(Loc1, ..), (Loc2, ..)]
                else:
                    if ptype_ in j.ftype:
                        # the if statements are to avoid multiple entries if people run the location again
                        if (self, ftype_) not in j.ftype[ptype_]:
                            j.ftype[ptype_].append((self, ftype_))
                        j.factors[factor_name_][self] = factor_
                    # if this is a new ctype_ being considered, create key and list with tuple (Location, FactorType/Factor)
                    else:
                        j.ftype[ptype_] = [(self, ftype_)]
                        if factor_name_ not in j.factors:  
                            j.factors[factor_name_] = dict()
                        j.factors[factor_name_][self] = factor_
                    

    def update_component_localization(self,  parameter: str, parameter_type: Union[ResourceParamType, ProcessParamType]):
        """Check if a localization has been provided
        Creates Localize from data 
        Updates Component.ltype and Component.localizations

        Args:
            parameter (str): name of parameter
            parameter_type (Union[ResourceParamType, ProcessParamType]): Component parameter type
        """
        localization_name_ = f'{parameter}_localize'.lower()
        attr_ = getattr(self, localization_name_)
        # if localize defined at location
        if attr_ is not None:
            ptype_ = getattr(parameter_type, parameter)
            # for each component provided
            for j in attr_:
                ltype_ = getattr(LocalizationType,
                                 f'{j.class_name()}_{parameter}'.upper())

                # calculate localize from data
                localization_ = Localization(
                    attr_[j], component=j, ltype=ltype_, location=self)

                # replace value with Localize object
                attr_[j] = localization_

                # component.ltype and .localizations are declared as dict()
                # if encountering for the first time, create key and list with the tuple (Location, FactorType/Factor)
                if not j.ltype:
                    j.ltype, j.localizations = dict(), dict()
                    j.ltype = dict()
                    j.ltype[ptype_] = [(self, ltype_)]
                    j.localizations[localization_name_] = dict()
                    j.localizations[localization_name_][self] = localization_
                # if a particular factor for the same component has been declared in another location, then append [(Loc1, ..), (Loc2, ..)]
                else:
                    if ptype_ in j.ltype:
                        # the if statements are to avoid multiple entries if people run the location again
                        if (self, ltype_) not in j.ltype[ptype_]:
                            j.ltype[ptype_].append((self, ltype_))
                        j.localizations[localization_name_][self] = localization_  
                
                    # if this is a new ctype_ being considered, create key and list with tuple (Location, FactorType/Factor)
                    else:
                        j.ltype[ptype_] = [(self, ltype_)]
                        if localization_name_ not in j.localizations:
                            j.localizations[localization_name_] = dict()
                        j.localizations[localization_name_][self] = localization_ 


    def make_component_subset(self, parameter: str, parameter_type: Union[ProcessType, ResourceType], component_set: str):
        """makes a subset of component based on provided ctype
        sets the subset as an attribute of the location
        if empty set, sets None

        Args:
            parameter (str): component type 
            parameter_type (Union[ProcessType, ResourceType]): component classification
            component_set (str): set of Processes or Resources
        """
        ctype_ = getattr(parameter_type, parameter)
        component_set_ = getattr(self, component_set)
        subset_ = {i for i in component_set_ if ctype_ in i.ctype}
        if subset_:
            setattr(self, f'{component_set}_{parameter}'.lower(), subset_)
        else:
            subset_ = {i for i in component_set_ if ctype_ in [j[1] for j in i.ctype if (isinstance(j, tuple)) and (j[0] == self)]}
            if subset_:
                setattr(self, f'{component_set}_{parameter}'.lower(), subset_)
            else:
                setattr(self, f'{component_set}_{parameter}'.lower(), None)


    def get_cap_bounds(self) -> Union[dict, dict]:
        """
        makes dictionaries with maximum and minimum capacity bounds
        """
        cap_max_dict = {}
        cap_min_dict = {}
        for i in self.processes:
            if ProcessType.MULTI_MATMODE in i.ctype:
                cap_max_dict[i.name] = {j: None for j in self.scales.scale[0]}
                cap_min_dict[i.name] = {j: None for j in self.scales.scale[0]}
                for j in self.scales.scale[0]:
                    cap_max_dict[i.name][j] = i.cap_max
                    cap_min_dict[i.name][j] = i.cap_min
            else:
                if ProcessType.MULTI_PRODMODE in i.ctype:
                    cap_max_dict[i.name] = i.cap_max
                    cap_min_dict[i.name] = i.cap_min
                else:
                    cap_max_dict[i.name] = {
                        j: None for j in self.scales.scale[0]}
                    cap_min_dict[i.name] = {
                        j: None for j in self.scales.scale[0]}
                    for j in self.scales.scale[0]:
                        cap_max_dict[i.name][j] = i.cap_max
                        cap_min_dict[i.name][j] = i.cap_min
        return cap_max_dict, cap_min_dict

    def create_storage_process(self, process) -> Process:
        """Creates a discharge process for discharge of stored resource

        Args:
            process (Process): STORAGE type process
        Returns:
            Process: Discharge Process 
        """
        if process.capex is None:
            capex = None
        else:
            capex = 0
        if process.fopex is None:
            fopex = None
        else:
            fopex = 0
        if process.vopex is None:
            vopex = None
        else:
            vopex = 0
        if process.incidental is None:
            incidental = None
        else:
            incidental = 0

        return Process(name=process.name+'_discharge', conversion=process.conversion_discharge, cap_min=process.cap_min,
                       cap_max=process.cap_max, introduce=process.introduce, retire=process.retire, capex=capex, vopex=vopex, fopex=fopex,
                       incidental=incidental, lifetime=process.lifetime, label=f'{process.label} (Discharge)', material_cons=None, ctype=[ProcessType.STORAGE_DISCHARGE])

    # *----------- Hashing --------------------------------

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
