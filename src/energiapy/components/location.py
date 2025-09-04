"""Location data class
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.1.0"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from dataclasses import dataclass
from itertools import product
from random import sample
from typing import Dict, Set, Union
from warnings import warn

from pandas import DataFrame

from ..components.material import Material
from ..components.process import Process, ProcessMode, MaterialMode
from ..components.resource import Resource
from ..components.temporal_scale import TemporalScale
from ..utils.process_utils import create_storage_process
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
        price_factor (Union[float, Dict[Resource, DataFrame]), optional): Factor for varying cost, scale changer normalizes. Defaults to None
        capacity_factor (Union[float, Dict[Process, DataFrame]), optional):  Factor for varying capacity, scale changer normalizes.Defaults to None
        capex_factor (Union[float, Dict[Process, DataFrame]), optional):  Factor for varying capital expenditure, scale changer normalizes. Defaults to None
        vopex_factor (Union[float, Dict[Process, DataFrame]), optional):  Factor for varying variable operational expenditure, scale changer normalizes. Defaults to None
        fopex_factor (Union[float, Dict[Process, DataFrame]), optional):  Factor for varying fixed operational expenditure, scale changer normalizes. Defaults to None
        incidental_factor (Union[float, Dict[Process, DataFrame]), optional):  Factor for varying incidental expenditure, scale changer normalizes. Defaults to None
        availability_factor (Union[float, Dict[Resource, DataFrame]), optional): Factor for varying resource availability, scale changer normalizes. Defaults to None
        revenue_factor (Union[float, Dict[Resource, DataFrame]), optional): Factor for varying resource revenue, scale changer normalizes. Defaults to None
        demand_factor_scale_level (int, optional): scale level for demand variance (resource). Defaults to 0
        price_factor_scale_level (int, optional): scale level for purchase cost variance(resource). Defaults to 0
        capacity_factor_scale_level (int, optional): scale level for capacity variance(process). Defaults to 0
        expenditure_factor_scale_level (int, optional): scale level for technology cost variance (process). Defaults to 0
        availability_factor_scale_level (int, optional): scale level for availability varriance (resource). Defaults to 0
        revenue_factor_scale_level (int, optional): scale level for revenue varriance (resource). Defaults to 0
        land_cost (float, optional): cost of land. Defaults to 0
        credit (Dict[Process, float], optional): credit earned by process per unit basis. Defaults to None.
        label(str, optional):Longer descriptive label if required. Defaults to ''

    Examples:
        Locations need a set of processes and the scale levels for demand, capacity, and cost, and if applicable demand factors, price_factors, capacity factors

        >>> Goa= Location(name='Goa', processes= {Process1, Process2}, demand_scale_level=2, capacity_scale_level= 2, price_scale_level= 1, demand_factor= {Resource1: DataFrame,}, price_factor = {Resource2: DataFrame}, capacity_factor = {Process1: DataFrame}, scales= TemporalScale object, label='Home')
    """

    name: str
    processes: Set[Process]
    scales: TemporalScale
    demand: Dict[Resource, float] = None
    demand_factor: Union[float, Dict[Resource, float]] = None
    price_factor: Union[float, Dict[Resource, float]] = None
    capacity_factor: Union[float, Dict[Process, float]] = None
    capex_factor: Union[float, Dict[Process, float]] = None
    vopex_factor: Union[float, Dict[Process, float]] = None
    fopex_factor: Union[float, Dict[Process, float]] = None
    incidental_factor: Union[float, Dict[Process, float]] = None
    availability_factor: Union[float, Dict[Resource, float]] = None
    revenue_factor: Union[float, Dict[Resource, float]] = None
    demand_factor_scale_level: int = None
    price_factor_scale_level: int = None
    capacity_factor_scale_level: int = None
    expenditure_factor_scale_level: int = None
    availability_factor_scale_level: int = None
    revenue_factor_scale_level: int = None
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
            resource_price (Dict): dictionary with the purchase cost of resources.
            failure_processes (Set): set of processes with failure rates
            fail_factor (Dict[Process, float]): creates a dictionary with failure points on a temporal scale
        """
        self.resources = self.get_resources()  # fetch all resources required
        self.resources_full = self.resources.union(
            {i.resource_storage for i in self.processes if i.resource_storage is not None})  # includes storage resources
        self.materials = self.get_materials()  # fetch all materials required
        self.scale_levels = self.scales.scale_levels
        self.processes_full = self.processes.union({create_storage_process(
            i) for i in self.processes if i.processmode == ProcessMode.STORAGE})
        # dicitionary of capacity bounds
        self.cap_max, self.cap_min = self.get_cap_bounds()
        # gets the modes for all processes
        self.modes_dict = {p: p.modes for p in self.processes_full if p.modes}
        # gets the ramp_rates for all processes
        self.ramp_rates_dict = {p: p.ramp_rates for p in self.processes_full}
        # gets the cap_pwl for all processes
        self.cap_pwl_dict = {p: p.cap_pwl for p in self.processes_full}
        # gets the ramp sequences for all processes
        self.ramp_sequence_dict = {
            p: p.ramp_sequence for p in self.processes_full}
        self.modes_all_dict = {p: {'modes': self.modes_dict[p], 'ramp_rates': self.ramp_rates_dict[p],
                                   'cap_pwl': self.cap_pwl_dict[p], 'ramp_sequence': self.ramp_sequence_dict[p]} if p.processmode == ProcessMode.MULTI else {'modes': None, 'ramp_rates': None,
                                                                                                                                                             'cap_pwl': None, 'ramp_sequence': None} for p in self.processes_full}

        self.resource_price, self.resource_revenue = self.get_resource_prices()
        # fetch all processes with failure rates set
        self.failure_processes = self.get_failure_processes()
        self.fail_factor = self.make_fail_factor()
        # self.emission_dict = {i: i.emission_dict for i in self.processes_full}
        self.storage_cost_dict = {
            i.resource_storage.name: i.storage_cost for i in self.processes_full if i.resource_storage is not None}

        self.factor_handler(
            factor_name='capacity_factor', factor_scale_name='capacity_factor_scale_level', varying_set_name='varying_capacity')

        self.factor_handler(
            factor_name='price_factor', factor_scale_name='price_factor_scale_level', varying_set_name='varying_price')

        self.factor_handler(
            factor_name='demand_factor', factor_scale_name='demand_factor_scale_level', varying_set_name='varying_demand')

        self.factor_handler(
            factor_name='availability_factor', factor_scale_name='availability_factor_scale_level', varying_set_name='varying_availability')

        self.factor_handler(
            factor_name='revenue_factor', factor_scale_name='revenue_factor_scale_level', varying_set_name='varying_revenue')

        self.factor_handler(
            factor_name='capex_factor', factor_scale_name='expenditure_factor_scale_level', varying_set_name='varying_capex')

        self.factor_handler(
            factor_name='fopex_factor', factor_scale_name='expenditure_factor_scale_level', varying_set_name='varying_fopex')

        self.factor_handler(
            factor_name='vopex_factor', factor_scale_name='expenditure_factor_scale_level', varying_set_name='varying_vopex')

        self.factor_handler(
            factor_name='incidental_factor', factor_scale_name='expenditure_factor_scale_level', varying_set_name='varying_incidental')

    def get_resources(self) -> Set[Resource]:
        """fetches required resources for processes introduced at locations

        Returns:
            Set[Resource]: set of resources
        """
        if len(self.processes) == 0:
            return None

        resources_single = set().union(
            *[set(i.conversion.keys()) for i in self.processes if i.processmode == ProcessMode.SINGLE])
        resources_multi = set()
        for i in [i for i in self.processes if i.processmode == ProcessMode.MULTI]:
            resources_multi = resources_multi.union(
                *[set(j.keys()) for j in list(i.conversion.values())])
        resources_storage = set(
            [i.storage for i in self.processes if i.processmode == ProcessMode.STORAGE])
        return resources_single.union(resources_multi).union(resources_storage)

    def get_materials(self) -> Set[Material]:
        """fetches required materials for processes introduced at locations

        Returns:
            Set[Material]: set of materials
        """
        if len(self.processes) == 0:
            return None
        else:
            materials = set()
            for i in self.processes:
                if i.material_cons is not None:
                    if isinstance(i.material_cons, dict):
                        for j in i.material_cons.keys():
                            materials = materials.union(
                                set(i.material_cons[j].keys()))
                    else:
                        materials = materials.union(
                            set(i.material_cons.keys()))
                        # return set().union(*[set(i.material_cons.keys()) for i in self.processes if i.material_cons is not None])
            return materials

    def factor_handler(self, factor_name: str, factor_scale_name: str, varying_set_name: str):
        """1. creates self.varying_x as a set of varying components
           2. changes the scale of the varying factor dictionary to tuple

        Args:
            factor_name (str): name of factor 
            factor_scale (str): name of the scale of the factor
            varying_set_name (str): set with varying components

        Returns:
            Union[set, set]: (varying factor with scales updated, contains components that vary)
        """
        factor = getattr(self, factor_name)
        factor_scale = getattr(self, factor_scale_name)
        if factor is not None:
            if factor_scale is None:
                warn(
                    f'[{self.name}]: Mention {factor_scale_name} for the {factor_name}')
            varying_set = set(factor.keys())
            if isinstance(list(factor.values())[0], DataFrame):
                factor = scale_changer(
                    factor, scales=self.scales, scale_level=factor_scale)  # changes the scales to tuple
            else:
                warn(
                    f'[{self.name}]: {factor_name} should be a dict of a DataFrame, Dict[Process, float]')
            setattr(self, factor_name, factor)
            setattr(self, varying_set_name, varying_set)
        else:
            if factor_scale is not None:
                warn(
                    f'[{self.name}]: Do not give {factor_scale_name} without a {factor_name}')

    def get_resource_prices(self) -> Union[dict, dict]:
        """gets resource purchase and selling prices

        Returns:
            Union[dict,dict]: (dict with purchase prices, dict with selling prices)
        """
        return {i.name: i.price for i in self.resources}, {i.name: i.revenue for i in self.resources}

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
        for i in self.processes_full:
            if i.materialmode == MaterialMode.MULTI:
                cap_max_dict[i.name] = {j: None for j in self.scales.scale[0]}
                cap_min_dict[i.name] = {j: None for j in self.scales.scale[0]}
                for j in self.scales.scale[0]:
                    cap_max_dict[i.name][j] = i.cap_max
                    cap_min_dict[i.name][j] = i.cap_min
            else:
                if i.processmode == ProcessMode.MULTI:
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

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
