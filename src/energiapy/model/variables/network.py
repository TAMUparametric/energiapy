"""pyomo network variables
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Var, NonNegativeReals, Set, Binary
from itertools import product
from ...utils.scale_utils import scale_pyomo_set

def generate_network_vars(instance: ConcreteModel, scale_level:int = 0):    
    """declares pyomo variables for network location at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for network variables. Defaults to 0.
    """
    instance.scales_network = scale_pyomo_set(instance= instance, scale_level= scale_level)
    instance.Cap_P = Var(instance.locations, instance.processes, instance.scales_network, within=NonNegativeReals, doc='Process Capacity')
    instance.Cap_S = Var(instance.locations, instance.resources_store, instance.scales_network, within=NonNegativeReals, doc='Storage Capacity')
    
    instance.Land_process = Var(instance.locations, instance.processes, instance.scales_network, within=NonNegativeReals, doc='Land used by Process')
    instance.Land_location = Var(instance.locations, instance.scales_network, within=NonNegativeReals, doc='Land used at location')
    instance.Land_network = Var(instance.scales_network, within=NonNegativeReals, doc='Land used at network')
    
    instance.P_location = Var(instance.locations, instance.processes, instance.scales_network, within=NonNegativeReals, doc='Total production at location')
    instance.S_location = Var(instance.locations, instance.resources_sell, instance.scales_network, within=NonNegativeReals, doc='Total resource discharge at location')
    instance.C_location = Var(instance.locations, instance.resources_purch, instance.scales_network, within=NonNegativeReals, doc='Total resource consumption at location')
    instance.B_location = Var(instance.locations, instance.resources_purch, instance.scales_network, within=NonNegativeReals, doc='Total resource purchase at location')
    instance.P_network = Var(instance.processes, instance.scales_network, within=NonNegativeReals, doc='Total production from network')
    instance.S_network = Var(instance.resources_sell, instance.scales_network, within=NonNegativeReals, doc='Total resource discharge from network')
    instance.C_network = Var(instance.resources_purch, instance.scales_network, within=NonNegativeReals, doc='Total resource consumption from network')
    instance.B_network = Var(instance.resources_purch, instance.scales_network, within=NonNegativeReals, doc='Total resource purchase from network')
    if len(instance.locations) > 1:
        instance.Trans_cost_network = Var(instance.transports, instance.scales_network, within = NonNegativeReals, doc = 'cost of transportation for transport mode')
    instance.Fopex_process = Var(instance.locations, instance.processes, instance.scales_network, within = NonNegativeReals, doc = 'Fixed Opex for process' )
    instance.Vopex_process = Var(instance.locations, instance.processes, instance.scales_network, within = NonNegativeReals, doc = 'Variable Opex for process' )
    instance.Capex_process = Var(instance.locations, instance.processes, instance.scales_network, within = NonNegativeReals, doc = 'Capex for process' )
    instance.Incidental_process = Var(instance.locations, instance.processes, instance.scales_network, within = NonNegativeReals, doc = 'Incidentals for process' )
    
    instance.Fopex_location = Var(instance.locations, instance.scales_network, within = NonNegativeReals, doc = 'Fixed Opex at location scale' )
    instance.Vopex_location = Var(instance.locations, instance.scales_network, within = NonNegativeReals, doc = 'Variable Opex at location scale' )
    instance.Capex_location = Var(instance.locations, instance.scales_network, within = NonNegativeReals, doc = 'Capex at location scale' )
    instance.Incidental_location = Var(instance.locations, instance.scales_network, within = NonNegativeReals, doc = 'Incidental at location scale' )
    
    instance.Fopex_network = Var(instance.scales_network, within = NonNegativeReals, doc = 'Fixed Opex at network scale' )
    instance.Vopex_network = Var(instance.scales_network, within = NonNegativeReals, doc = 'Variable Opex at network scale' )
    instance.Capex_network = Var(instance.scales_network, within = NonNegativeReals, doc = 'Capex at network scale' )
    instance.Incidental_network = Var(instance.scales_network, within = NonNegativeReals, doc = 'Incidental at network scale' )
    
    instance.carbon_emission_network = Var(instance.scales_network, within = NonNegativeReals, doc = 'Carbon emissions across network at network_scale')
    instance.carbon_emission_location = Var(instance.locations, instance.scales_network, within = NonNegativeReals, doc = 'Carbon emissions at location at network_scale')
    
    instance.global_warming_potential_location = Var(instance.locations, instance.scales_network, within= NonNegativeReals, doc = 'global warming potential caused at each location')
    instance.global_warming_potential_network = Var(instance.scales_network, within= NonNegativeReals, doc = 'global warming potential caused at network scale')
    instance.global_warming_potential_process= Var(instance.locations, instance.processes, instance.scales_network, within= NonNegativeReals, doc = 'global warming potential caused by each process') 
    instance.global_warming_potential_resource = Var(instance.locations, instance.resources_purch, instance.scales_network, within= NonNegativeReals, doc = 'global warming potential caused by each resource') 
    instance.global_warming_potential_material = Var(instance.locations, instance.processes_materials, instance.scales_network, within= NonNegativeReals, doc = 'global warming potential caused by each material')
    
    return 
