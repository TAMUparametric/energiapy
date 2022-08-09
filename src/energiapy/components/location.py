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

from dataclasses import dataclass, field

from ..components.temporal_scale import Temporal_scale
from ..components.process import Process
from ..components.resource import Resource
from ..components.material import Material
import pandas
from typing import Set, Dict, Union

@dataclass
class Location:
    """
    Object with data regarding a location
    Args:
        name (str): ID
        processes (Set[Process]): set of processes to include at location
        scales (temporal_scale): temporal scale of the problem
        demand (Set[Resource], optional): demand for resources at location
        varying_process_df (pandas.DataFrame, optional): contains varying production data at appropriate resolution. Defaults to pandas.DataFrame().
        varying_cost_df (pandas.DataFrame, optional): contains varying resource cost data at appropriate resolution. Defaults to pandas.DataFrame().
        label (str, optional): label. Defaults to ''.
        PV_class (str, optional): PV cost category as defined by NREL annual technology baseline (ATB). Defaults to ''.
        WF_class (str, optional): WF cost category as defined by NREL ATB. Defaults to ''.
        LiI_class (str, optional): Li-ion cost category as defined by NREL ATB. Defaults to ''.
        PSH_class (str, optional): PSH cost category as defined by NREL ATB. Defaults to ''.
    """
    name: str 
    processes: Set[Process] 
    scales: Temporal_scale 
    demand: Union[float, Dict[Resource, float]] = 0.0
    label: str = ''
    PV_class: str = ''
    WF_class: str = ''
    LiI_class: str = ''
    PSH_class: str = ''
    
    def __post_init__(self):
        self.resources = self.get_resources()
        self.materials = self.get_materials()
        self.scale_levels = self.scales.scale_levels
        self.varying_processes = self.get_varying_processes()
        self.varying_resources = self.get_varying_resources()
        self.capacity_factor = self.get_capacityfactor()
        self.cost_factor = self.get_costfactor()
        self.resource_price = self.get_resource_price()    
    
      
    def get_resources(self) -> Set[Resource]:
        """fetches required resources for processes introduced at locations 

        Returns:
            Set[resource]: set of resources
        """
        if len(self.processes) == 0:
            return None
        else:
            return set().union(*[set(i.conversion.keys()) for i in self.processes])

    
    def get_materials(self) -> Set[Material]:
        """fetches required materials for processes introduced at locations

        Returns:
            Set[material]: set of materials
        """
        if len(self.processes) == 0:
            return None
        else:
            return set().union(*[set(i.material_cons.keys()) for i in self.processes if i.material_cons is not None])
    

    def get_resource_price(self):
        """gets resource prices for resources with non-varying costs
        
        Returns:
            Set[resource]: set of resources with non-varying cost factors
        """
        return {i.name: i.price for i in self.resources}
    
    
    def get_varying_processes(self):
        return {i for i in self.processes if i.varying == True}
    
    def get_varying_resources(self):
        return {i for i in self.resources if i.varying == True}            
    
    def get_capacityfactor(self):
        return {i.name: i.capacity_factor for i in self.varying_processes}
    
    def get_costfactor(self):
        return {i.name: i.cost_factor for i in self.varying_resources}
    
    
    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name


