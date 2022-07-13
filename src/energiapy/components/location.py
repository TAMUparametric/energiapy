"""Location data class  
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from dataclasses import dataclass

from ..components.temporal_scale import temporal_scale
from ..components.process import process
from ..components.resource import resource
from ..components.material import material
import pandas
from typing import Set 

@dataclass
class location:
    """
    Object with data regarding a location
    """

    def __init__(self, name: str, processes:Set[process], scales:temporal_scale, varying_process_df:pandas.DataFrame = pandas.DataFrame(),\
        varying_cost_df:pandas.DataFrame= pandas.DataFrame(), label: str = '', PV_class: str = '', WF_class: str = '', LiI_class: str = '', PSH_class: str = ''):
        """creates a dataclass with information pertaining to a location
        can include - varying capacity factors for processes, varying costs of resources
        PV, WF, Li-ion, PSH classes 

        Args:
            name (str): ID
            processes (Set[process]): set of processes to include at location
            scales (temporal_scale): temporal scale of the problem
            varying_process_df (pandas.DataFrame, optional): contains varying production data at appropriate resolution. Defaults to pandas.DataFrame().
            varying_cost_df (pandas.DataFrame, optional): contains varying resource cost data at appropriate resolution. Defaults to pandas.DataFrame().
            label (str, optional): label. Defaults to ''.
            PV_class (str, optional): PV cost category as defined by NREL annual technology baseline (ATB). Defaults to ''.
            WF_class (str, optional): WF cost category as defined by NREL ATB. Defaults to ''.
            LiI_class (str, optional): Li-ion cost category as defined by NREL ATB. Defaults to ''.
            PSH_class (str, optional): PSH cost category as defined by NREL ATB. Defaults to ''.
        """
        self.name = name
        self.processes = processes
        self.resources = self.get_resources()
        self.materials = self.get_materials()
        self.scales = scales
        self.label = label
        self.varying_process_df = varying_process_df
        self.varying_cost_df = varying_cost_df
        self.PV_class = PV_class
        self.WF_class = WF_class
        self.LiI_class = LiI_class
        self.PSH_class = PSH_class
        self.varying_processes = self.get_varying_processes()
        self.varying_resources = self.get_varying_resources()
        self.capacity_factor = self.make_capacity_factor()
        self.cost_factor = self.make_cost_factor()
        self.resource_price = self.get_resource_price()
        
    def make_capacity_factor(self)-> dict:
        """makes capacity factor dict from varying process/production output DataFrame()

        Returns:
            dict: dictionary with varying capacity factor, structure - {process: scale: value}
        """
        if self.varying_process_df.empty == True:
            return None
        else:
            capacity_factor = {process.name: {scale: self.varying_process_df[process.name][self.varying_process_df['scales'] == scale].values[0] \
                if process.name in list(self.varying_process_df.columns) else 1 for scale in self.varying_process_df['scales']}\
                    for process in self.varying_processes}
            return capacity_factor
        
    def make_cost_factor(self) -> dict:
        """makes cost factor dict from varying process/production output DataFrame()

        Returns:
            dict: dictionary with varying cost factor, structure - {resource: scale: value}
        """
        if self.varying_cost_df.empty == True:
            return None
        else:
            cost_factor = {resource.name: {scale: self.varying_cost_df[resource.name][self.varying_cost_df['scales'] == scale].values[0]\
                if resource.name in list(self.varying_cost_df.columns) else 1 for scale in self.varying_cost_df['scales']} for resource in self.varying_resources}
            return cost_factor
    
    def get_resources(self) -> Set[resource]:
        """fetches required resources for processes introduced at locations 

        Returns:
            Set[resource]: set of resources
        """
        if len(self.processes) == 0:
            return None
        else:
            return set().union(*[set(i.conversion.keys()) for i in self.processes])
    
    def get_materials(self) -> Set[material]:
        """fetches required materials for processes introduced at locations

        Returns:
            Set[material]: set of materials
        """
        if len(self.processes) == 0:
            return None
        else:
            return set().union(*[set(i.material_cons.keys()) for i in self.processes if i.material_cons is not None])
    
    def get_varying_processes(self) -> Set[process]:
        """makes a set of processes with varying capacity factors

        Returns:
            Set[process]: set of processes with varying capacity factors
        """
        return {i for i in self.processes if i.varying == True}
    
    def get_varying_resources(self) -> Set[resource]:
        """makes a set of resources with varying cost factors
        
        Returns:
            Set[resource]: set of resources with varying cost factors
        """
        return {i for i in self.resources if i.varying == True}
    
    def get_resource_price(self):
        """gets resource prices for resources with non-varying costs
        
        Returns:
            Set[resource]: set of resources with non-varying cost factors
        """
        return {i.name: i.price for i in self.resources if i.varying == False}
    
    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name


# class capacity_factor:
#     """Object with varying capacity factor data
#     """
#     def __init__(self, locations: list, processes: list, scales: temporal_scale, varying_process_dict: dict, scheduling_scale_level: int, name:str = 'capacity_factor'):
#         self.locations = locations
#         self.processes = processes 
#         self.varying_process_dict = varying_process_dict
#         self.scales = scales.scale
#         self.name = name
#         self.capacity_factor = self.make_capacity_factor()
        
#     def __repr__(self):
#         return self.name       
    
#     def make_capacity_factor(self):
#         capacity_factor_dict = {location.name:{process.name: \
#             {scale: self.varying_process_dict[location.name][process.name][scale] \
#                 if process.name in self.varying_process_dict[location.name].keys() else 1 \
#                 for scale in product(*self.scales.values())} \
#                 for process in self.processes} for location in self.locations}
        
#         return capacity_factor_dict