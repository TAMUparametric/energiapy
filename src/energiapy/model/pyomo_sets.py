#%%
"""pyomo sets
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from ..components.location import Location
from ..components.scenario import Scenario 
from ..components.temporal_scale import Temporal_scale
from pyomo.environ import ConcreteModel, Set
# from typing import 

def generate_sets(instance: ConcreteModel, location_set:set = {}, transport_set:set= {}, scales: Temporal_scale = {},\
    process_set:set = {}, resource_set:set = {}, material_set:set = {}, source_set:set = {}, sink_set:set = {} ):
    """Generates pyomo sets based on declared lists

    Args:
        instance (ConcreteModel): pyomo instance
        process_list (list, optional): list of processes. Defaults to [].
        location_list (list, optional): list of locations. Defaults to [].
        transport_list (list, optional): list of transports. Defaults to [].
        scales (dict, optional): scales of the problem, generated through temporal_scale. Defaults to {}.
        
    """
    instance.processes = Set(initialize  = [i.name for i in process_set], doc = 'Set of processes')
    instance.resources = Set(initialize = [i.name for i in resource_set], doc = 'Set of resources')
    instance.resources_store = Set(initialize = [i.name for i in resource_set if i.store_max > 0], doc = 'Set of storeable resources')
    instance.resource_nosell = Set(initialize = [i.name for i in resource_set if i.sell ==  False], doc = 'Set of dischargeable resources')
    instance.resources_purch = Set(initialize = [i.name for i in resource_set if i.cons_max > 0], doc = 'Set of purchased resources')   
    instance.resources_varying = Set(initialize = [i.name for i in resource_set if i.varying == True], doc = 'Set of resources with varying purchase price')    
    instance.resources_demand = Set(initialize = [i.name for i in resource_set if i.demand == True], doc = 'Set of resources with exact demand')    
    instance.processes_varying = Set(initialize  = [i.name for i in process_set if i.varying == True], doc = 'Set of processes with varying capacity')
    instance.locations = Set(initialize = [i.name for i in location_set], doc = 'Set of locations')
    instance.scales = Set(scales.name, initialize = scales.scale)
    
    if source_set is not None:
        instance.sources = Set(initialize = [i.name for i in source_set], doc = 'Set of sources')
    
    if sink_set is not None:
        instance.sinks = Set(initialize = [i.name for i in sink_set], doc = 'Set of sinks')
    
    if material_set is not None:
        instance.materials = Set(initialize = [i.name for i in material_set], doc = 'Set of materials')
    
    if transport_set is not None:
        instance.transports = Set(initialize = [i.name for i in transport_set], doc = 'Set of transports')

    return



# %%
