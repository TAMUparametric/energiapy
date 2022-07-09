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

from ..components.temporal_scale import temporal_scale
from pyomo.environ import ConcreteModel, Set

def generate_sets(instance: ConcreteModel, process_list:list = [], resource_list:list= [], material_list:list= [], \
    location_list:list = [], transport_list:list= [], scales: temporal_scale = {}):
    """Generates pyomo sets based on declared lists

    Args:
        instance (ConcreteModel): pyomo instance
        process_list (list, optional): list of processes. Defaults to [].
        resource_list (list, optional): list of resources. Defaults to [].
        material_list (list, optional): list of materials. Defaults to [].
        location_list (list, optional): list of locations. Defaults to [].
        transport_list (list, optional): list of transports. Defaults to [].
        scales (dict, optional): scales of the problem, generated through temporal_scale. Defaults to {}.
        
    """
    
    instance.processes = Set(initialize  = [i.name for i in process_list], doc = 'Set of processes')
    instance.resources = Set(initialize = [i.name for i in resource_list], doc = 'Set of resources')
    instance.resources_store = Set(initialize = [i.name for i in resource_list if i.store_max > 0], doc = 'Set of storeable resources')
    instance.resource_nosell = Set(initialize = [i.name for i in resource_list if i.sell ==  False], doc = 'Set of dischargeable resources')
    instance.materials = Set(initialize = [i.name for i in material_list], doc = 'Set of materials')
    instance.locations = Set(initialize = [i.name for i in location_list], doc = 'Set of locations')
    instance.transports = Set(initialize = [i.name for i in transport_list], doc = 'Set of transports')
    instance.scales = Set(scales.name, initialize = scales.scale)
    return



# %%
