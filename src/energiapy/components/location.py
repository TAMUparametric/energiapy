""" energiapy.Location - A set of Processes create a Location, required Resources and Materials are inferred 
"""
# TODO - Land MAX constraints
# TODO - Handle materials


import uuid
from dataclasses import dataclass
from itertools import product
from random import sample
from typing import Dict, List, Set, Tuple, Union

from pandas import DataFrame

from .comptype import LocationType, ProcessType, ResourceType
from .material import Material
from .parameters.factor import Factor
from .parameters.localize import Localize
from .parameters.mpvar import Theta, create_mpvar
from .parameters.paratype import (FactorType, LocalizeType, MPVarType,
                                  ParameterType)
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
        credit (Dict[Process, float], optional): credit earned by process per unit basis. Defaults to None.
        demand_factor (Dict[Resource, DataFrame], optional): Factor for varying demand. Defaults to None.
        credit_factor (Dict[Process, DataFrame], optional): factor for credit. Defaults to None.
        purchase_price_factor (Dict[Resource, DataFrame], optional): Factor for varying cost. Defaults to None.
        availability_factor (Dict[Resource, DataFrame], optional): Factor for varying resource availability. Defaults to None.
        sell_price_factor (Dict[Resource, DataFrame], optional): Factor for varying resource revenue. Defaults to None.
        capacity_factor (Dict[Process, DataFrame], optional):  Factor for varying capacity.Defaults to None.
        capex_factor (Dict[Process, DataFrame], optional):  Factor for varying capital expenditure. Defaults to None.
        vopex_factor (Dict[Process, DataFrame], optional):  Factor for varying variable operational expenditure. Defaults to None.
        fopex_factor (Dict[Process, DataFrame], optional):  Factor for varying fixed operational expenditure. Defaults to None.
        incidental_factor (Dict[Process, DataFrame], optional):  Factor for varying incidental expenditure. Defaults to None.
        purchase_price_localize (Dict[Resource, Tuple[float, int]] , optional): Localization factor for purchase price. Defaults to None.
        cons_max_localize (Dict[Resource, Tuple[float, int]] , optional): Localization factor for availability. Defaults to None.
        sell_price_localize (Dict[Resource, Tuple[float, int]] , optional): Localization factor for selling price. Defaults to None.
        cap_max_localize (Dict[Process, Tuple[float, int]] , optional): Localization factor for maximum capacity. Defaults to None.
        cap_min_localize (Dict[Process, Tuple[float, int]] , optional): Localization factor for minimum capacity. Defaults to None.
        capex_localize (Dict[Process, Tuple[float, int]] , optional): Localization factor for capex. Defaults to None.
        vopex_localize (Dict[Process, Tuple[float, int]] , optional): Localization factor for vopex. Defaults to None.
        fopex_localize (Dict[Process, Tuple[float, int]] , optional): Localization factor for fopex. Defaults to None.
        incidental_localize(Dict[Process, Tuple[float, int]] , optional): Localization factor for incidental. Defaults to None.
        basis (str, optional): unit in which land area is measured. Defaults to None .
        block (Union[str, list, dict], optional): block to which it belong. Convinient to set up integer cuts. Defaults to None.
        label (str, optional): used while generating plots. Defaults to None.
        citation (str, optional): can provide citations for your data sources. Defaults to None.
        ctype (List[LandType], optional): Location type. Defaults to None.
        ptype (Dict[LandType, ParameterType], optional): paramater type of declared values. Defaults to None.
        ftype (Dict[LandType, FactorType], optional): factor type of declared factors. Defaults to None.

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
    # Component parameters declared at Location
    demand: Dict[Resource, Union[float, Tuple[float], Theta]] = None
    credit: Dict[Process, Union[float, Tuple[float], Theta]] = None
    # Factors for component parameter variability
    demand_factor: Dict[Resource, DataFrame] = None
    credit_factor: Dict[Process, DataFrame] = None
    purchase_price_factor: Dict[Resource, DataFrame] = None
    availability_factor: Dict[Resource, DataFrame] = None
    sell_price_factor: Dict[Resource, DataFrame] = None
    capacity_factor: Dict[Process, DataFrame] = None
    capex_factor: Dict[Process, DataFrame] = None
    vopex_factor: Dict[Process, DataFrame] = None
    fopex_factor: Dict[Process, DataFrame] = None
    incidental_factor: Dict[Process, DataFrame] = None
    # Localizations for paramters provided at component level
    purchase_price_localize: Dict[Resource, Tuple[float, int]] = None
    cons_max_localize: Dict[Resource, Tuple[float, int]] = None
    sell_price_localize: Dict[Resource, Tuple[float, int]] = None
    cap_max_localize: Dict[Process, Tuple[float, int]] = None
    cap_min_localize: Dict[Process, Tuple[float, int]] = None
    capex_localize: Dict[Process, Tuple[float, int]] = None
    vopex_localize: Dict[Process, Tuple[float, int]] = None
    fopex_localize: Dict[Process, Tuple[float, int]] = None
    incidental_localize: Dict[Process, Tuple[float, int]] = None
    # Details
    basis: str = None
    block: str = None
    label: str = None
    citation: str = None
    # Types
    ctype: List[LocationType] = None
    ptype: Dict[LocationType, ParameterType] = None
    ftype: Dict[LocationType, FactorType] = None
    # Depreciated
    demand_scale_level: int = None
    price_scale_level: int = None
    capacity_scale_level: int = None
    expenditure_scale_level: int = None
    availability_scale_level: int = None
    price_factor: dict = None
    revenue_factor: dict = None

    def __post_init__(self):

        # *----------------- Update Location parameters and factors ---------------------------------
        
        if self.ctype is None:
            self.ctype = []
        self.ptype, self.ftype = dict(), dict()

        # Currently only includes land_cost, land_max
        # If MPVar Theta or a tuple is provided as bounds ptype UNCERTAIN
        # if factors are provided a Factor is generated and ftype is updated
        # or else, parameter is treated as CERTAIN parameter
        for i in ['land_cost', 'land_max']:
            self.update_location_params_and_factors(i)

        # * ---------------Collect Componets (Processes, Resources, Materials) -----------------------
        # Resources and Materials are collected based on Process(es) provided

        self.processes = self.processes.union({self.create_storage_process(
            i) for i in self.processes if ProcessType.STORAGE in i.ctype})
        self.resources = set().union(*[i.resource_req for i in self.processes])
        self.materials = set().union(
            *[i.material_req for i in self.processes if (ProcessType.SINGLE_MATMODE in i.ctype) or (ProcessType.MULTI_MATMODE in i.ctype)])

        # * -------------------------- Handle Processes ----------------------------------------
        # checks if new process parameters have been declared
        # Sets new attributes:
        #   subsets based on Process.ctype
        #   dictionaries with prod_modes, material_modes, etc.

        # Update Process parameters provided at Location level
        for i in ['credit']:
            self.update_comp_params_declared_at_location(
                parameter=i, component_type=ProcessType)

        # set Process subsets as Location attributes
        for i in ['SINGLE_PRODMODE', 'MULTI_PRODMODE', 'NO_MATMODE', 'SINGLE_MATMODE', 'MULTI_MATMODE',
                  'STORAGE', 'STORAGE_REQ', 'LINEAR_CAPEX', 'PWL_CAPEX', 'CAPACITY', 'CAP_MAX', 'CAP_MIN',
                  'CAPEX', 'FOPEX', 'VOPEX', 'INCIDENTAL', 'CREDIT', 'LAND']:
            self.make_component_subset(ctype=getattr(
                ProcessType, i), component_set='processes', tag=f'processes_{i.lower()}')

        # collect Process parameters and set dicts as Location attrs
        for i in ['cap_max', 'cap_min', 'introduce', 'retire', 'lifetime', 'trl', 'p_fail',  'capex', 'fopex', 'vopex', 'incidental', 'land']:
            self.make_parameter_dict(parameter=i, component_set='processes')

        # Collect capacity and capex segments for each Process with PWL capex
        if getattr(self, 'processes_pwl_capex') is not None:
            self.capacity_segments = {i:
                                      i.capacity_segments for i in getattr(self, 'processes_pwl_capex')}
            self.capex_segments = {i:
                                   i.capex_segments for i in getattr(self, 'processes_pwl_capex')}

        # TODO ------ This adds a dummy mode to cap_max ------ See if can be avoided -----------
        # dicitionary of capacity bounds
        # self.cap_max, self.cap_min = self.get_cap_bounds()

        # gets the production modes
        if getattr(self, 'processes_multi_prodmode') is not None:
            self.prod_modes = {
                i: i.prod_modes for i in getattr(self, 'processes_multi_prodmode')}

        # gets the material modes
        if getattr(self, 'processes_multi_matmode') is not None:
            self.material_modes = {
                i: i.material_modes for i in getattr(self, 'processes_multi_matmode')}

        # fetch all processes with failure rates set
        self.failure_processes = self.get_failure_processes()
        self.fail_factor = self.make_fail_factor()

        # * -------------------------- Handle Resources ----------------------------------------
        # check if new resource parameters have been declared
        # Sets new attributes:
        #   subsets based on Resource.ctype
        #   dictionaries with parameter values

        # Update Resource parameters provided at Location level
        for i in ['demand']:
            self.update_comp_params_declared_at_location(
                parameter=i, component_type=ResourceType)

        # set Resource subsets as Location attributes
        for i in ['STORE', 'PRODUCE', 'IMPLICIT', 'DISCHARGE', 'SELL', 'CONSUME', 'PURCHASE', 'DEMAND']:
            self.make_component_subset(ctype=getattr(
                ResourceType, i), component_set='resources', tag=f'resources_{i.lower()}')

        # collect Resource parameters and set dicts as Location attrs
        for i in ['purchase_price', 'sell_price', 'cons_max', 'store_max', 'store_min', 'storage_cost']:
            self.make_parameter_dict(parameter=i, component_set='resources')

        # * -------- Update Component (Resource and Process) Factors and Localizations -------------

        # Create Factors from DataFrame
        # Update Component.ptype and Component.factors
        for i in ['capacity', 'fopex', 'vopex', 'incidental',  'credit', 'purchase_price', 'demand', 'availability', 'sell_price']:
            self.update_comp_factor(i)

        # Create Localize from data
        # Update Component.ltype and Component.localizations
        for i in ['purchase_price', 'cons_max', 'sell_price', 'cap_max', 'cap_min', 'capex', 'fopex', 'vopex', 'incidental']:
            self.update_comp_localize(i)

        # * ---------------- Collect Emission Data ------------------------------------------
        # Get emission data from components
        for i in ['resources', 'materials', 'processes']:
            setattr(self, f'{i}_emissions', {
                    j: j.emissions for j in getattr(self, i)})

        # *----------------- Generate Random Name ------------------------
        # A random name is generated if self.name = None
        if self.name is None:
            self.name = f'{self.__class__.__name__}_{uuid.uuid4().hex}'

        # *----------------- Depreciation Warnings-----------------------------

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

    # *----------------- Functions-------------------------------------

    def update_location_params_and_factors(self, parameter: str):
        """Updated ctype based on type of parameter provide.
        Creates MPVar if Theta or tuple of bounds
        also updates ftype if factors provides and puts Factor in place of DataFrame

        Args:
            parameter (str): land parameters
        """

        if getattr(self, parameter) is not None:
            # Update ctype
            ctype_ = getattr(LocationType, parameter.upper())
            self.ctype.append(ctype_)
            # Update ptype
            if isinstance(getattr(self, parameter), (tuple, Theta)):
                self.ptype[ctype_] = ParameterType.UNCERTAIN
                mpvar_ = create_mpvar(value=getattr(
                    self, parameter), component=self, ptype=getattr(MPVarType, parameter.upper()))
                setattr(self, parameter, mpvar_)
            else:
                self.ptype[ctype_] = ParameterType.CERTAIN

        if getattr(self, f'{parameter}_factor') is not None:
            # Update ftype
            ftype_ = getattr(FactorType, parameter.upper())
            self.ftype[ctype_] = ftype_
            factor_ = Factor(component=self, data=getattr(
                self, f'{parameter}_factor'), ftype=ftype_, scales=self.scales, location=self)
            setattr(self, f'{parameter}_factor', factor_)

    def update_comp_params_declared_at_location(self, parameter: str, component_type: Union[ResourceType, ProcessType]):
        """Update the ctype and ptype of component if parameters declared at Location
        Note that the ptype and ctype are updated with a tuples, i.e (Location, ____)
        Args:
            parameter (str): new paramter that has been declared 
            component_type (Union[ResourceType, ProcessType]): Type of component
        """
        if getattr(self, parameter) is not None:
            for i in getattr(self, parameter):
                ctype_ = getattr(component_type, parameter.upper())
                i.ctype.append((self, ctype_))
                if isinstance(getattr(self, parameter)[i], (tuple, Theta)):
                    ptype_ = (self, ParameterType.UNCERTAIN)
                    mpvar_ = create_mpvar(value=getattr(self, parameter)[
                                          i], component=i, ptype=getattr(MPVarType, parameter.upper()))
                    getattr(self, parameter)[i] = mpvar_
                else:
                    ptype_ = (self, ParameterType.CERTAIN)
                if ctype_ in i.ptype:  # check if already exists, if yes append
                    i.ptype[ctype_].append(ptype_)
                else:  # or create new list with tuple
                    i.ptype[ctype_] = [ptype_]

    def update_comp_factor(self, factor_name: str):
        """Checks if a factor for a component has been provided
        Creates a Factor from DataFrame data
        Updates Componet.factors and Component.ftype

        Args:
            factor_name (str): name of the factor without '_factor'
        """

        # This dictionary has a combination of paramter type for each comp and thier related variable factor
        type_dict = {'capacity': (ProcessType.CAPACITY, FactorType.CAPACITY),
                     'fopex': (ProcessType.FOPEX, FactorType.FOPEX),
                     'vopex': (ProcessType.VOPEX, FactorType.VOPEX),
                     'incidental': (ProcessType.INCIDENTAL, FactorType.INCIDENTAL),
                     'credit': (ProcessType.CREDIT, FactorType.CREDIT),
                     'purchase_price': (ResourceType.PURCHASE, FactorType.PURCHASE_PRICE),
                     'demand': (ResourceType.DEMAND, FactorType.DEMAND),
                     'availability': (ResourceType.CONSUME, FactorType.AVAILABILITY),
                     'sell_price': (ResourceType.SELL, FactorType.SELL_PRICE)}

        # if factor defined at location
        if getattr(self, f'{factor_name}_factor') is not None:
            # for each component provided
            for j in getattr(self, f'{factor_name}_factor'):
                # component type, basically what parameter
                ctype_ = type_dict[factor_name][0]
                # factor related to the parameter
                ftype_ = type_dict[factor_name][1]

                # create the factor
                factor_ = Factor(component=j, data=getattr(self, f'{factor_name}_factor')[
                    j], ftype=ftype_, scales=self.scales, location=self)

                # replace the DataFrame with a Factor
                getattr(self, f'{factor_name}_factor')[j] = factor_

                # component.ftype and .factors are declared as dict().
                # if encountering for the first time, create key and list with the tuple (Location, FactorType/Factor)
                if not j.ftype:
                    j.ftype[ctype_] = [(self, ftype_)]
                    j.factors[ctype_] = [(self, factor_)]
                # if a particular factor for the same component has been declared in another location, then append [(Loc1, ..), (Loc2, ..)]
                else:
                    if ctype_ in j.ftype:
                        j.ftype[ctype_].append((self, ftype_))
                        j.factors[ctype_].append((self, factor_))
                    # if this is a new ctype_ being considered, create key and list with tuple (Location, FactorType/Factor)
                    else:
                        j.ftype[ctype_] = [(self, ftype_)]
                        j.factors[ctype_] = [(self, factor_)]

    def update_comp_localize(self, localize_name: str):
        """Check if a localization has been provided
        Creates Localize from data 
        Updates Component.ltype and Component.localizations

        Args:
            localize_name (str): name of what localization provided     
        """

        type_dict = {'sell_price': 'SELL',
                     'cons_max': 'CONSUME', 'purchase_price': 'PURCHASE'}

        # if localize defined at location
        if getattr(self, f'{localize_name}_localize') is not None:
            # for each component provided
            for j in getattr(self, f'{localize_name}_localize'):
                # find component parameter type
                if localize_name in ['purchase_price', 'cons_max', 'sell_price']:
                    ctype_ = getattr(ResourceType, type_dict[localize_name])
                else:
                    ctype_ = getattr(ProcessType, localize_name.upper())
                # find LocalizeType
                ltype_ = getattr(LocalizeType, localize_name.upper())

                # calculate localize from data
                localize_ = Localize(value=getattr(
                    self, f'{localize_name}_localize')[j], component=j, ltype=ltype_, location=self)

                # replace value with Localize object
                getattr(self, f'{localize_name}_localize')[j] = localize_
                # component.ltype and .localizations are declared as dict()
                # if encountering for the first time, create key and list with the tuple (Location, FactorType/Factor)
                if not j.ltype:
                    j.ltype[ctype_] = [(self, ltype_)]
                    j.localizations[ctype_] = [(self, localize_)]
                # if a particular factor for the same component has been declared in another location, then append [(Loc1, ..), (Loc2, ..)]
                else:
                    if ctype_ in j.ltype:
                        j.ltype[ctype_].append((self, ltype_))
                        j.localizations[ctype_].append((self, localize_))
                    # if this is a new ctype_ being considered, create key and list with tuple (Location, FactorType/Factor)
                    else:
                        j.ltype[ctype_] = [(self, ltype_)]
                        j.localizations[ctype_] = [(self, localize_)]

    def make_parameter_dict(self, parameter: str, component_set: str):
        """Makes a dict with components and thier paramter values
        set the dictionary as an attribute
        if parameter undefined then sets None

        Args:
            parameter (str): what parameters 
            component_set (str): component set of Resource or Process
        """
        param_dict_ = {i: getattr(i, parameter) for i in getattr(
            self, component_set) if getattr(i, parameter) is not None}

        if param_dict_:
            setattr(self, parameter, param_dict_)
        else:
            setattr(self, parameter, None)

    def make_component_subset(self, ctype: Union[ProcessType, ResourceType], component_set: str, tag: str):
        """makes a subset of component based on provided ctype
        sets the subset as an attribute of the location
        if empty set, sets None

        Args:
            ctype (str): component type 
            component_set (str): set of Processes or Resources
            tag (str) : what to call the new location attribute
        """
        subset_ = {i for i in getattr(
            self, component_set) if ctype in i.ctype}
        if subset_:
            setattr(self, tag, subset_)
        else:
            setattr(self, tag, None)

    def get_failure_processes(self):
        """get processes with failure rates

        Returns:
            Set[Process]: set of resources with failure rates
        """
        return {i for i in self.processes if i.p_fail is not None}

    def make_fail_factor(self) -> dict:
        """samples randomly from a probablity distribution to generate timeperiods in the scheduling scale that fail

        Returns:
            dict: temporal horizon with certain days at the scheduling level failing
        """
        if self.failure_processes == set():
            return None

        scale_iter = list(product(*self.scales.scale))
        return {process_.name: {(scale_): sample([0] * int(process_.p_fail * 100) + [1] * int(
            (1 - process_.p_fail) * 100), 1)[0] for scale_ in scale_iter} for process_ in self.failure_processes}

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

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
