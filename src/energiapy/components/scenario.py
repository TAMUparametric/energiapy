"""Cost scenario data class  
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
from ..components.network import Network
from ..components.temporal_scale import Temporal_scale
from ..model.pyomo_cons import *

@dataclass
class Scenario:
    """creates a scenario dataclass object
    Args:
        name (str): ID
        network (network): network object with the locations, transport linakges, and processes (with resources and materials)
        scales (temporal_scale): scales of the problem 
        expenditure_scale_level (int, optional): scale for resource purchase. Defaults to 0.
        scheduling_scale_level (int, optional): scale of production and inventory scheduling. Defaults to 0.
        network_scale_level (int, optional): scale for network decisions such as facility location. Defaults to 0.
        demand_scale_level (int, optional): scale for meeting specific demand for resource. Defaults to 0.
        label (str, optional): descriptive label. Defaults to ''.
    """
    name: str 
    network: Network
    scales: Temporal_scale 
    expenditure_scale_level: int = 0
    scheduling_scale_level: int = 0
    network_scale_level: int = 0
    demand_scale_level: int = 0 
    label: str = ''

    def __post_init__(self):    
        self.transport_set = set().union(*self.network.transport_dict.values())
        self.source_locations = self.network.source_locations
        self.sink_locations = self.network.sink_locations
        self.transport_dict = self.network.transport_dict
        self.transport_avail_dict = self.network.transport_avail_dict
        self.location_set = set(self.source_locations + self.sink_locations)         
        self.trans_max = {j.name: j.trans_max for j in self.transport_set}
        self.trans_loss = {j.name: j.trans_loss for j in self.transport_set} 
        self.trans_cost = {j.name: j.trans_cost for j in self.transport_set}
        self.trans_emit =  {j.name: j.trans_emit for j in self.transport_set} 
        self.process_set = set().union(*[i.processes for i in self.location_set if i.processes is not None])
        self.resource_set = set().union(*[i.resources for i in self.location_set if i.resources is not None])
        self.material_set = set().union(*[i.materials for i in self.location_set if i.materials is not None])
        self.conversion = {i.name: {j.name: i.conversion[j] if j in i.conversion.keys()\
            else 0 for j in self.resource_set} for i in self.process_set}
        self.prod_max = {i.name: {j.name: j.prod_max for j in i.processes} for i in self.location_set}
        self.prod_min = {i.name: {j.name: j.prod_min for j in i.processes} for i in self.location_set}
        self.cons_max = {i.name: {j.name: j.cons_max for j in i.resources} for i in self.location_set}
        self.store_max = {i.name: {j.name: j.store_max for j in i.resources} for i in self.location_set}
        self.store_min = {i.name: {j.name: j.store_min for j in i.resources} for i in self.location_set}
        self.capacity_factor = {i.name: i.capacity_factor for i in self.location_set}  
        self.loc_res_dict =  {i.name: {j.name for j in i.resources} for i in self.location_set}
        self.loc_pro_dict =  {i.name: {j.name for j in i.processes} for i in self.location_set}
        self.cost_factor =  {i.name: i.cost_factor for i in self.location_set}
        self.price = {i.name: i.resource_price for i in self.location_set}
        self.capex_dict = {i.name: i.capex for i in self.process_set}
        self.fopex_dict = {i.name: i.fopex for i in self.process_set}
        self.vopex_dict = {i.name: i.vopex for i in self.process_set}
        self.demand_dict = {i.name: {j.name: i.demand[j] for j in i.demand} for i in self.location_set}
        self.distance_dict = self.network.distance_dict
    def __repr__(self):
        return self.name



    

    
    