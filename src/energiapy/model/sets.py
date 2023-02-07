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

def generate_sets(instance: ConcreteModel, scenario:Scenario):
    """Generates pyomo sets based on declared lists

    Args:
        instance (ConcreteModel): pyomo instance
        scenario (Scenario): scenario

    """
    location_set = scenario.location_set
    transport_set= scenario.transport_set
    scales= scenario.scales
    process_set= scenario.process_set
    resource_set= scenario.resource_set 
    material_set= scenario.material_set
    source_set= scenario.source_locations
    sink_set= scenario.sink_locations

    instance.processes = Set(initialize  = [i.name for i in process_set], doc = 'Set of processes')
    instance.resources_nosell = Set(initialize = [i.name for i in resource_set if i.sell ==  False], doc = 'Set of non-dischargeable resources')
    instance.resources_sell = Set(initialize = [i.name for i in resource_set if i.sell ==  True], doc = 'Set of dischargeable resources')
    instance.resources_purch = Set(initialize = [i.name for i in resource_set if i.cons_max > 0], doc = 'Set of purchased resources')   
    instance.resources_varying = Set(initialize = [i.name for i in resource_set if i.varying == True], doc = 'Set of resources with varying purchase price')  
    instance.resources_demand = Set(initialize = [i.name for i in resource_set if i.demand == True], doc = 'Set of resources with exact demand')    
    instance.processes_varying = Set(initialize  = [i.name for i in process_set if i.varying == True], doc = 'Set of processes with varying capacity')
    instance.processes_failure = Set(initialize  = [i.name for i in process_set if i.p_fail is not None], doc = 'Set of processes which can fail')
    instance.processes_materials = Set(initialize  = [i.name for i in process_set if i.material_cons is not None], doc = 'Set of processes which can fail')
    instance.processes_storage = Set(initialize= [i.name for i in process_set if i.conversion_discharge is not None], doc = 'Set of storage process' )
    instance.locations = Set(initialize = [i.name for i in location_set], doc = 'Set of locations')
    instance.scales = Set(scales.list, initialize = scales.scale) #indexed set. scales.scale is a set of list(s) {[],.}
    
    instance.processes_full = Set(initialize = list(scenario.conversion.keys()), doc = 'set of process + discharge dummy processes')
    dummy_resources = {i.dummy for i in process_set if i.dummy is not None}
    # dummy_resources = set() # collect dummy resources for storage
    # for i in [i for i in process_set if i.conversion_discharge is not None]:
    #     dummy_resources = dummy_resources.union(set(i.dummy))
    
    if dummy_resources:
        instance.resources_store = Set(initialize = [i.name for i in list(dummy_resources)], doc = 'Set of storeable resources')
        resource_set = dummy_resources.union(resource_set)

    else:
        instance.resources_store = Set(initialize = [i.name for i in resource_set if i.store_max > 0], doc = 'Set of storeable resources')

    instance.resources = Set(initialize = [i.name for i in resource_set], doc = 'Set of resources')

    
    if source_set is not None:
        instance.sources = Set(initialize = [i.name for i in source_set], doc = 'Set of sources')
    
    if sink_set is not None:
        instance.sinks = Set(initialize = [i.name for i in sink_set], doc = 'Set of sinks')
    
    if material_set is not None:
        instance.materials = Set(initialize = [i.name for i in material_set], doc = 'Set of materials')
    
    if transport_set is not None:
        instance.transports = Set(initialize = [i.name for i in transport_set], doc = 'Set of transports')
        instance.resources_trans = Set(initialize = [i.name for i in set().union(*[i.resources for i in transport_set])], doc= 'Set of transportable resources')
    return



# %%
