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
from turtle import pu
from ..components.network import network
from ..components.temporal_scale import temporal_scale
from pyomo.environ import ConcreteModel
from ..model.pyomo_sets import generate_sets
from ..model.pyomo_vars import generate_milp_vars, generate_mpmilp_vars 
from ..model.pyomo_cons import *

@dataclass
class scenario:
    def __init__(self, name:str, network:network, scales: temporal_scale,  instance:ConcreteModel, \
        expenditure_scale_level:int= 0, scheduling_scale_level:int= 0, network_scale_level:int= 0, label:str=''):
        self.name = name
        self.network= network
        self.source_locations = self.network.source_locations
        self.sink_locations = self.network.sink_locations
        self.location_set = set(self.source_locations + self.sink_locations)
        self.instance= instance
        self.scales = scales
        self.expenditure_scale_level = expenditure_scale_level
        self.scheduling_scale_level = scheduling_scale_level
        self.network_scale_level = network_scale_level
        self.transport_set = set().union(*self.network.transport_dict.values())
        self.label = label
        
    def formulate_milp(self):
        generate_sets(instance= self.instance, location_set= self.location_set, transport_set= self.transport_set, scales= self.scales)
        generate_milp_vars(instance= self.instance, expenditure_scale_level= self.expenditure_scale_level, scheduling_scale_level = self.scheduling_scale_level \
            , network_scale_level= self.network_scale_level)
        
        nameplate_production_constraint(instance= self.instance, location_set= self.location_set, network_scale_level= \
            self.network_scale_level, scheduling_scale_level= self.scheduling_scale_level)
        nameplate_inventory_constraint(instance= self.instance, location_set= self.location_set, network_scale_level= self.network_scale_level,\
            scheduling_scale_level= self.scheduling_scale_level)
        resource_consumption_constraint(instance= self.instance, location_set= self.location_set, scheduling_scale_level= self.scheduling_scale_level)
        resource_expenditure_constraint(instance= self.instance, location_set= self.location_set, scheduling_scale_level= self.scheduling_scale_level,\
            expenditure_scale_level= self.expenditure_scale_level)
        resource_discharge_constraint(instance= self.instance, scheduling_scale_level= self.scheduling_scale_level)
        
    def formulate_mpmilp(self):
        generate_sets(instance= self.instance, location_set= self.location_set, transport_set= self.transport_set, scales= self.scales)
        generate_mpmilp_vars(instance= self.instance, expenditure_scale_level= self.expenditure_scale_level, scheduling_scale_level = self.scheduling_scale_level \
            , network_scale_level= self.network_scale_level)
        uncertain_nameplate_production_constraint(instance= self.instance, location_set= self.location_set, network_scale_level= self.network_scale_level,\
            scheduling_scale_level= self.scheduling_scale_level)
        
    
    def __repr__(self):
        return self.name
    


    

