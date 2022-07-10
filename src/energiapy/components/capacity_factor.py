#%%
"""Capacity factor data class  
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from ..components.temporal_scale import temporal_scale
from dataclasses import dataclass
from itertools import product

@dataclass
class capacity_factor:
    """Object with varying capacity factor data
    """
    def __init__(self, locations: list, processes: list, scales: temporal_scale, varying_process_dict: dict, scheduling_scale_level: int, name:str = 'capacity_factor'):
        self.locations = locations
        self.processes = processes 
        self.varying_process_dict = varying_process_dict
        self.scales = scales.scale
        self.name = name
        self.capacity_factor = self.make_capacity_factor()
        
    def __repr__(self):
        return self.name       
    
    def make_capacity_factor(self):
        capacity_factor_dict = {location.name:{process.name: \
            {scale: self.varying_process_dict[location.name][process.name][scale] \
                if process.name in self.varying_process_dict[location.name].keys() else 1 \
                for scale in product(*self.scales.values())} \
                for process in self.processes} for location in self.locations}
        
        return capacity_factor_dict


