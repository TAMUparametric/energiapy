""" Need to do here:

    figure out scale of factors
    whether specific demand is met for a resource that can be sold at this location
    Add localization factors for prices and such 
    DEMAND var for resource
    EXP Var for process 
"""

from dataclasses import dataclass
from itertools import product
from random import sample
from typing import Dict, Set, Union
from warnings import warn
import uuid
from pandas import DataFrame
from .material import Material
from .process import Process
from .resource import Resource
from .temporal_scale import TemporalScale
from .factor import Factor
from .comptype import ProcessType, ResourceType, FactorType, ParameterType
from ..utils.scale_utils import scale_changer


@dataclass
class Location:
    """Location is essentially a set of processes. Factors for varying capacity, cost, and demand can be provided as dictionary.
    The scale levels of capacity, cost, and demand need to be provided as well

    Args:
        name (str): name of the location, short ones are better to deal with.
        processes (Set[Process]): set of processes (Process objects) to include at location
        scales (TemporalScale): temporal scales of the problem
        demand (Dict[Resource, float]): demand for resources at location. Defaults to None.
        demand_factor (Union[float, Dict[Resource, DataFrame]), optional): Factor for varying demand, scale changer normalizes.Defaults to None
        purchase_price_factor (Union[float, Dict[Resource, DataFrame]), optional): Factor for varying cost, scale changer normalizes. Defaults to None
        capacity_factor (Union[float, Dict[Process, DataFrame]), optional):  Factor for varying capacity, scale changer normalizes.Defaults to None
        capex_factor (Union[float, Dict[Process, DataFrame]), optional):  Factor for varying capital expenditure, scale changer normalizes. Defaults to None
        vopex_factor (Union[float, Dict[Process, DataFrame]), optional):  Factor for varying variable operational expenditure, scale changer normalizes. Defaults to None
        fopex_factor (Union[float, Dict[Process, DataFrame]), optional):  Factor for varying fixed operational expenditure, scale changer normalizes. Defaults to None
        incidental_factor (Union[float, Dict[Process, DataFrame]), optional):  Factor for varying incidental expenditure, scale changer normalizes. Defaults to None
        availability_factor (Union[float, Dict[Resource, DataFrame]), optional): Factor for varying resource availability, scale changer normalizes. Defaults to None
        sell_price_factor (Union[float, Dict[Resource, DataFrame]), optional): Factor for varying resource revenue, scale changer normalizes. Defaults to None
        land_cost (float, optional): cost of land. Defaults to 0
        credit (Dict[Process, float], optional): credit earned by process per unit basis. Defaults to None.
        label(str, optional):Longer descriptive label if required. Defaults to ''

    Examples:
        Locations need a set of processes and the scale levels for demand, capacity, and cost, and if applicable demand factors, price_factors, capacity factors

        >>> Goa= Location(name='Goa', processes= {Process1, Process2}, demand_scale_level=2, capacity_scale_level= 2, price_scale_level= 1, demand_factor= {Resource1: DataFrame,}, price_factor = {Resource2: DataFrame}, capacity_factor = {Process1: DataFrame}, scales= TemporalScale object, label='Home')
    """

    processes: Set[Process]
    scales: TemporalScale
    name: str = None
    demand: Dict[Resource, float] = None
    demand_factor: Union[float, Dict[Resource, float]] = None
    purchase_price_factor: Union[float, Dict[Resource, float]] = None
    capacity_factor: Union[float, Dict[Process, float]] = None
    capex_factor: Union[float, Dict[Process, float]] = None
    vopex_factor: Union[float, Dict[Process, float]] = None
    fopex_factor: Union[float, Dict[Process, float]] = None
    incidental_factor: Union[float, Dict[Process, float]] = None
    availability_factor: Union[float, Dict[Resource, float]] = None
    sell_price_factor: Union[float, Dict[Resource, float]] = None
    land_cost: float = 0
    credit: Dict[Process, float] = None
    label: str = ''

    def __post_init__(self):
        """Sets and stuff generated insitu

        Args:
            resources (Set[Resource]): set of resources. Get resources fetches these using the processes
            materials (Set[Resource]): set of materials. Get materials fetches these using the processes
            scale_levels (int): the levels of scales involved
            varying_capacity (Set): processes with varying capacities
            varying_price (Set): resources with varying purchase price
            varying_demand (Set): resources with varying demands
            price (Dict): dictionary with the purchase cost of resources.
            failure_processes (Set): set of processes with failure rates
            fail_factor (Dict[Process, float]): creates a dictionary with failure points on a temporal scale
        """

        self.processes = self.processes.union({self.create_storage_process(
            i) for i in self.processes if ProcessType.STORAGE in i.ctype})
        self.resources = set().union(*[i.resource_req for i in self.processes])
        self.materials = set().union(
            *[i.material_req for i in self.processes if ProcessType.HAS_MATMODE in i.ctype])

        self.capacity_segments = {
            i.capacity_segments for i in self.processes if ProcessType.PWL_CAPEX in i.ctype}
        self.capex_segments = {
            i.capex_segments for i in self.processes if ProcessType.PWL_CAPEX in i.ctype}

        self.scale_levels = self.scales.scale_levels
        # dicitionary of capacity bounds

        self.cap_max, self.cap_min = self.get_cap_bounds()

        # gets the modes for all processes
        self.prod_modes = {
            i: i.prod_modes for i in self.processes if ProcessType.MULTI_PRODMODE in i.ctype}

        # fetch all processes with failure rates set
        self.failure_processes = self.get_failure_processes()
        self.fail_factor = self.make_fail_factor()
        # self.emission_dict = {i: i.emission_dict for i in self.processes}
        self.storage_cost_dict = {
            i.resource_storage.name: i.storage_cost for i in self.processes if ProcessType.STORAGE in i.ctype}

        if self.demand is not None:
            for i in self.demand.keys():
                i.ctype.append(ResourceType.DEMAND)

        for i in ['purchase_price', 'sell_price', 'cons_max', 'store_max', 'store_min']:
            self.comp_attr_dict(attr=i, component_set='resources')

        for i in ['STORE', 'PRODUCE', 'IMPLICIT', 'DISCHARGE', 'SELL', 'CONSUME', 'PURCHASE', 'DEMAND']:
            self.comp_attr_set(comp_type=getattr(
                ResourceType, i), component_set='resources', tag=f'resources_{i.lower()}')

        for i in ['capacity', 'fopex', 'vopex', 'incidental', 'purchase_price', 'demand', 'availability', 'sell_price']:
            self.handle_factor(i)

        if self.name is None:
            self.name = f"Location_{uuid.uuid4().hex}"

    def handle_factor(self, factor_name):
        type_dict = {'capacity': (ProcessType.CAPACITY, FactorType.CAPACITY),
                     'fopex': (ProcessType.FOPEX, FactorType.FOPEX),
                     'vopex': (ProcessType.VOPEX, FactorType.VOPEX),
                     'incidental': (ProcessType.INCIDENTAL, FactorType.INCIDENTAL),
                     'purchase_price': (ResourceType.PURCHASE, FactorType.PURCHASE_PRICE),
                     'demand': (ResourceType.DEMAND, FactorType.DEMAND),
                     'availability': (ResourceType.CONSUME, FactorType.AVAILABILITY),
                     'sell_price': (ResourceType.SELL, FactorType.SELL_PRICE)}

        if getattr(self, f'{factor_name}_factor') is not None:
            for j in getattr(self, f'{factor_name}_factor'):
                j.ptype[type_dict[factor_name][0]
                        ] = ParameterType.DETERMINISTIC_DATA
                getattr(self, f'{factor_name}_factor')[j] = Factor(component=j, data=getattr(self, f'{factor_name}_factor')[
                    j], ctype=type_dict[factor_name][1], scales=self.scales)

    def comp_attr_dict(self, attr: str, component_set: str):
        """makes a dict of the type {comp: attr}

        Args:
            attr (str): attribute
            component_set (str): components such as resources
        """
        setattr(self, attr, {getattr(i, 'name'): getattr(i, attr) for i in getattr(
            self, component_set) if getattr(i, attr) is not None})

    def comp_attr_set(self, comp_type: Union[ProcessType, ResourceType], component_set: str, tag: str):
        """makes a dict of the type {comp: attr}

        Args:
            attr (str): attribute
            component_set (str): components such as resources
            tag (str) : what to call the new location attribute
        """
        setattr(self, tag, {i for i in getattr(
            self, component_set) if comp_type in i.ctype})

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
            if ProcessType.HAS_MATMODE in i.ctype:
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
        """Creates a dummy process for discharge of stored resource

        Args:
            process (Process): Dummy process name derived from storage process
        Returns:
            Process: Dummy process for storage
        """
        return Process(name=process.name+'_discharge', conversion=process.conversion_discharge, cap_min=process.cap_min,
                       cap_max=process.cap_max, introduce=process.introduce, retire=process.retire, capex=0, vopex=0, fopex=0,
                       lifetime=process.lifetime, label=process.label + '_storage', material_cons=None)

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
