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
import pandas

@dataclass
class location:
    """
    Object with data regarding a location
    """

    def __init__(self, name: str, processes:set, scales:temporal_scale, varying_process_df:pandas.DataFrame = pandas.DataFrame(),\
        varying_cost_df:pandas.DataFrame= pandas.DataFrame(), label: str = '', PV_class: str = '', WF_class: str = '', LiI_class: str = '', PSH_class: str = ''):
        """location object parameters

        Args:
            name (str): ID for locations
            label (str, optional): name of the location. Defaults to ''.
            PV_class (str, optional): Residential solar PV costing class based on average availability (DOE/NRELatb). Defaults to ''.
            WF_class (str, optional): Wind costing class based on average availability (DOE/NRELatb). Defaults to ''.
            LiI_class (str, optional): Charging cycle for lithium ion batteries (NRELatb). Defaults to ''.
            PSH_class (str, optional): PSH category (NRELatb). Defaults to ''.
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
        
    def make_capacity_factor(self):
        if self.varying_process_df.empty == True:
            return None
        else:
            capacity_factor = {process.name: {scale: self.varying_process_df[process.name][self.varying_process_df['scales'] == scale].values[0] \
                if process.name in list(self.varying_process_df.columns) else 1 for scale in self.varying_process_df['scales']}\
                    for process in self.varying_processes}
            return capacity_factor
        
    def make_cost_factor(self):
        if self.varying_cost_df.empty == True:
            return None
        else:
            cost_factor = {resource.name: {scale: self.varying_cost_df[resource.name][self.varying_cost_df['scales'] == scale].values[0]\
                if resource.name in list(self.varying_cost_df.columns) else 1 for scale in self.varying_cost_df['scales']} for resource in self.varying_resources}
            return cost_factor
    
    def get_resources(self):
        if len(self.processes) == 0:
            return None
        else:
            return set().union(*[set(i.conversion.keys()) for i in self.processes])
    
    def get_materials(self):
        if len(self.processes) == 0:
            return None
        else:
            return set().union(*[set(i.material_cons.keys()) for i in self.processes if i.material_cons is not None])
    
    def get_varying_processes(self):
        return {i for i in self.processes if i.varying == True}
    
    def get_varying_resources(self):
        return {i for i in self.resources if i.varying == True}
    
    def get_resource_price(self):
        # return {i.name: i.price for i in self.resources if i.varying == False if i.consumption_max > 0}
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