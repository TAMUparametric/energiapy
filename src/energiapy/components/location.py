"""Location data class
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
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
from ..components.process import Process, ProcessMode
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
        availability_factor (Union[float, Dict[Resource, DataFrame]), optional): Factor for varying resource availability, scale changer normalizes. Defaults to None
        demand_scale_level (int, optional): scale level for demand (resource). Defaults to 0
        price_scale_level (int, optional): scale level for purchase cost (resource). Defaults to 0
        capacity_scale_level (int, optional): scale level for capacity (process). Defaults to 0
        expenditure_scale_level (int, optional): scale level for technology (process). Defaults to 0
        availability_scale_level (int, optional): scale level for availability (resource). Defaults to 0
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
    availability_factor: Union[float, Dict[Resource, float]] = None
    demand_scale_level: int = 0
    price_scale_level: int = 0
    capacity_scale_level: int = 0
    expenditure_scale_level: int = 0
    availability_scale_level: int = 0
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
            varying_cost (Set): resources with varying costs
            varying_demand (Set): resources with varying demands
            resource_price (Dict): dictionary with the purchase cost of resources.
            failure_processes (Set): set of processes with failure rates
            fail_factor (Dict[Process, float]): creates a dictionary with failure points on a temporal scale
        """
        self.resources = self.get_resources()
        self.resources_full = self.resources.union(
            {i.resource_storage for i in self.processes if i.resource_storage is not None})
        self.materials = self.get_materials()
        self.scale_levels = self.scales.scale_levels
        self.processes_full = self.processes.union({create_storage_process(
            i) for i in self.processes if i.processmode == ProcessMode.STORAGE})
        self.prod_max = self.get_prod_max()
        self.prod_min = self.get_prod_min()

        if self.capacity_factor is not None:
            self.varying_capacity = set(self.capacity_factor.keys())
            if isinstance(list(self.capacity_factor.values())[0], DataFrame):
                self.capacity_factor = scale_changer(
                    self.capacity_factor, scales=self.scales, scale_level=self.capacity_scale_level)
            else:
                warn(
                    'Input should be a dict of a DataFrame, Dict[Process, float]')

        if self.price_factor is not None:
            self.varying_cost = set(self.price_factor.keys())
            if isinstance(list(self.price_factor.values())[0], DataFrame):
                self.price_factor = scale_changer(
                    self.price_factor, scales=self.scales, scale_level=self.price_scale_level)
            else:
                warn(
                    'Input should be a dict of a DataFrame, Dict[Resource, float]')

        if self.demand_factor is not None:
            self.varying_demand = set(self.demand_factor.keys())
            if isinstance(list(self.demand_factor.values())[0], DataFrame):
                self.demand_factor = scale_changer(
                    self.demand_factor, scales=self.scales, scale_level=self.demand_scale_level)
            else:
                warn(
                    'Input should be a dict of a DataFrame, Dict[Resource, float]')

        if self.availability_factor is not None:
            self.varying_availability = set(self.availability_factor.keys())
            if isinstance(list(self.availability_factor.values())[0], DataFrame):
                self.availability_factor = scale_changer(
                    self.availability_factor, scales=self.scales, scale_level=self.availability_scale_level)
            else:
                warn(
                    'Input should be a dict of a DataFrame, Dict[Resource, float]')

        self.resource_price = self.get_resource_price()
        self.failure_processes = self.get_failure_processes()
        self.fail_factor = self.make_fail_factor()

        if self.capex_factor is not None:
            self.varying_capex = set(self.capex_factor.keys())
            if isinstance(list(self.capex_factor.values())[0], DataFrame):
                self.capex_factor = scale_changer(
                    self.capex_factor, scales=self.scales, scale_level=self.expenditure_scale_level)
            else:
                warn(
                    'Input should be a dict of a DataFrame, Dict[Resource, float]')

        if self.vopex_factor is not None:
            self.varying_vopex = set(self.vopex_factor.keys())
            if isinstance(list(self.vopex_factor.values())[0], DataFrame):
                self.vopex_factor = scale_changer(
                    self.vopex_factor, scales=self.scales, scale_level=self.expenditure_scale_level)
            else:
                warn(
                    'Input should be a dict of a DataFrame, Dict[Resource, float]')

        if self.fopex_factor is not None:
            self.varying_fopex = set(self.fopex_factor.keys())
            if isinstance(list(self.fopex_factor.values())[0], DataFrame):
                self.fopex_factor = scale_changer(
                    self.fopex_factor, scales=self.scales, scale_level=self.expenditure_scale_level)
            else:
                warn(
                    'Input should be a dict of a DataFrame, Dict[Resource, float]')

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
        return resources_single.union(resources_multi)

    def get_materials(self) -> Set[Material]:
        """fetches required materials for processes introduced at locations

        Returns:
            Set[Material]: set of materials
        """
        if len(self.processes) == 0:
            return None
        else:
            return set().union(*[set(i.material_cons.keys()) for i in self.processes if i.material_cons is not None])

    def get_resource_price(self):
        """gets resource prices for resources with non-varying costs

        Returns:
            Set[Resource]: set of resources with non-varying cost factors
        """
        return {i.name: i.price for i in self.resources}

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

    def get_prod_max(self) -> dict:
        """
        make a dictionary with maximum production
        """
        prod_max_dict = {}
        for i in self.processes_full:
            if i.processmode == ProcessMode.MULTI:
                prod_max_dict[i.name] = i.prod_max
            else:
                prod_max_dict[i.name] = {j: None for j in self.scales.scale[0]}
                for j in self.scales.scale[0]:
                    prod_max_dict[i.name][j] = i.prod_max
        return prod_max_dict

    def get_prod_min(self) -> dict:
        """
        make a dictionary with minimum production
        """
        prod_min_dict = {}
        for i in self.processes_full:
            if i.processmode == ProcessMode.MULTI:
                prod_min_dict[i.name] = i.prod_min
            else:
                prod_min_dict[i.name] = {0: None}
                prod_min_dict[i.name][0] = i.prod_min
        return prod_min_dict

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
