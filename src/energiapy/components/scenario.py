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

from pandas import DataFrame
from ..components.network import Network
from ..components.location import Location
from ..components.temporal_scale import Temporal_scale
from ..components.process import Process, ProcessMode
from ..model.constraints import *
from ..utils.math_utils import scaler, find_euclidean_distance, generate_connectivity_matrix
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestCentroid
from dataclasses import dataclass
from typing import Union



@dataclass
class Scenario:
    """
    Scenario contains the network between location and all the data within.

    Args:
        name (str): name of scenario, short ones are better to deal with.
        scales (temporal_scale): scales of the problem 
        network (Union[Network, Location]): network object with the locations, transport linakges, and processes (with resources and materials)
        expenditure_scale_level (int, optional): scale for resource purchase. Defaults to 0.
        scheduling_scale_level (int, optional): scale of production and inventory scheduling. Defaults to 0.
        network_scale_level (int, optional): scale for network decisions such as facility location. Defaults to 0.
        demand_scale_level (int, optional): scale for meeting specific demand for resource. Defaults to 0.
        cluster_wt (dict): cluster weights as a dictionary. {scale: int}. Defaults to None. 
        label (str, optional): Longer descriptive label if required. Defaults to ''
    """
    name: str 
    scales: Temporal_scale 
    network: Union[Network, Location] = None
    expenditure_scale_level: int = 0
    scheduling_scale_level: int = 0
    network_scale_level: int = 0
    demand_scale_level: int = 0
    cluster_wt: dict = None 
    label: str = ''

    def __post_init__(self):    

        if type(self.network) == Location:
            self.transport_set = None
            self.source_locations = None
            self.sink_locations = None
            self.transport_dict = None
            self.transport_avail_dict = None
            self.trans_max = None
            self.trans_loss = None 
            self.trans_cost = None
            self.trans_emit =  None
            self.distance_dict = None
            self.location_set = {self.network}   
            
        else:
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
            self.distance_dict = self.network.distance_dict
            
        self.process_set = set().union(*[i.processes for i in self.location_set if i.processes is not None])
        self.resource_set = set().union(*[i.resources for i in self.location_set if i.resources is not None])
        self.material_set = set().union(*[i.materials for i in self.location_set if i.materials is not None])
        # self.dummy_resource_set = set().union(*[i.dummy for i in self.process_set if i.dummy is not None])
        
        conversion = {i.name: {j.name: i.conversion[j] if j in i.conversion.keys()\
            else 0 for j in self.resource_set} for i in self.process_set if i.processmode == ProcessMode.single}
        conversion_discharge = {i.name + '_discharge': {j.name: i.conversion_discharge[j] if j in i.conversion_discharge.keys()\
            else 0 for j in self.resource_set} for i in self.process_set if i.conversion_discharge is not None}
        
        self.conversion = {**conversion, **conversion_discharge}
        
        self.prod_max = {i.name: {j.name: j.prod_max for j in i.processes} for i in self.location_set}
        self.prod_min = {i.name: {j.name: j.prod_min for j in i.processes} for i in self.location_set}
        self.cons_max = {i.name: {j.name: j.cons_max for j in i.resources} for i in self.location_set}
        self.store_max = {i.name: {j.name: j.store_max for j in i.resources} for i in self.location_set}
        self.store_min = {i.name: {j.name: j.store_min for j in i.resources} for i in self.location_set}
        self.capacity_factor = {i.name: i.capacity_factor for i in self.location_set}  
        self.cost_factor = {i.name: i.cost_factor for i in self.location_set}  
        self.loc_res_dict =  {i.name: {j.name for j in i.resources} for i in self.location_set}
        self.loc_pro_dict =  {i.name: {j.name for j in i.processes} for i in self.location_set}
        self.loc_mat_dict =  {i.name: {j.name for j in i.materials} for i in self.location_set}
        self.price = {i.name: i.resource_price for i in self.location_set} # TODO change to be location wise
        self.capex_dict = {i.name: i.capex for i in self.process_set}
        self.fopex_dict = {i.name: i.fopex for i in self.process_set}
        self.vopex_dict = {i.name: i.vopex for i in self.process_set}
        self.capex_capacity_dict = {i.name: i.capex_capacity for i in self.process_set}
        self.capex_power_dict = {i.name: i.capex_power for i in self.process_set}
        self.incidental_dict =  {i.name: i.incidental for i in self.process_set}
        self.land_dict = {i.name: i.land for i in self.process_set}
        self.material_gwp_dict = {i.name:{j.name: j.gwp for j in self.material_set} for i in self.location_set}
        self.resource_gwp_dict = {i.name:{j.name: j.gwp for j in self.resource_set} for i in self.location_set}
        self.process_gwp_dict = {i.name: {j.name: j.gwp for j in self.process_set} for i in self.location_set}
        self.demand_factor = {i.name: i.demand_factor for i in self.location_set}
        self.fail_factor = {i.name: i.fail_factor for i in self.location_set}
        self.process_resource_dict = {i.name: {j.name for j in i.conversion.keys() } for i in self.process_set if i.conversion is not None}
        self.process_material_dict = {i.name: {j.name: i.material_cons[j] for j in i.material_cons.keys() } for i in self.process_set if i.material_cons is not None}
        self.mode_dict = {i.name: [j for j in list(i.multiconversion.keys())] for i in self.process_set if i.processmode == ProcessMode.multi }
        # if type(list(self.location_set)[0].demand) == float:
        #     self.demand = {i.name: i.demand for i in self.location_set}
        # else:

        #     self.demand = {i.name: {j.name if type(j: i.demand[j] for j in i.demand} for i in self.location_set}
        # if self.costdynamics == Costdynamics.constant:
        #     self.cost_factor =  {i.name: i.cost_factor for i in self.location_set}
        # elif 
        
     
    def make_conversion_df(self):
        return DataFrame.from_dict(self.conversion)

    def __repr__(self):
        return self.name




    


