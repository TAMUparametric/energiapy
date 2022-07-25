#%%.
"""pyomo variables
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
from ..utils.model_utils import scale_pyomo_set



def generate_expenditure_vars(instance: ConcreteModel, scale_level:int = 0):
    """declares pyomo variables for expenditure at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for scheduling variables. Defaults to 0.
    """
    # exp_scales_list = [instance.scales[i].data() for i in range(scale_level+ 1)]
    instance.scales_expenditure = scale_pyomo_set(instance= instance, scale_level= scale_level)
    instance.Fopex_process = Var(instance.locations, instance.processes, instance.scales_expenditure, within = NonNegativeReals, doc = 'Fixed Opex for process' )
    instance.Vopex_process = Var(instance.locations, instance.processes, instance.scales_expenditure, within = NonNegativeReals, doc = 'Variable Opex for process' )
    instance.Capex_process = Var(instance.locations, instance.processes, instance.scales_expenditure, within = NonNegativeReals, doc = 'Capex for process' )
    
    instance.Fopex_location = Var(instance.locations, instance.scales_expenditure, within = NonNegativeReals, doc = 'Fixed Opex at location scale' )
    instance.Vopex_location = Var(instance.locations, instance.scales_expenditure, within = NonNegativeReals, doc = 'Variable Opex at location scale' )
    instance.Capex_location = Var(instance.locations, instance.scales_expenditure, within = NonNegativeReals, doc = 'Capex at location scale' )
    
    
    instance.Fopex_network = Var(instance.scales_expenditure, within = NonNegativeReals, doc = 'Fixed Opex at network scale' )
    instance.Vopex_network = Var(instance.scales_expenditure, within = NonNegativeReals, doc = 'Variable Opex at network scale' )
    instance.Capex_network = Var(instance.scales_expenditure, within = NonNegativeReals, doc = 'Capex at network scale' )
    return

def generate_scheduling_vars(instance: ConcreteModel, scale_level:int = 0):    
    """declares pyomo variables for scheduling at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for scheduling variables. Defaults to 0.
    """
    instance.scales_scheduling = scale_pyomo_set(instance= instance, scale_level= scale_level)
    instance.P = Var(instance.locations, instance.processes, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource Production')
    instance.B = Var(instance.locations, instance.resources, instance.scales_scheduling, within = NonNegativeReals, doc = 'Purchase Expenditure')
    instance.C = Var(instance.locations, instance.resources, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource Consumption')
    instance.S = Var(instance.locations, instance.resources, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource Dispensed/Sold')
    instance.Inv = Var(instance.locations, instance.resources, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource Inventory')
    instance.Imp = Var(instance.sinks, instance.sources, instance.resources, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource import')
    instance.Exp = Var(instance.sources, instance.sinks, instance.resources, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource export')
    return 


def generate_network_vars(instance: ConcreteModel, scale_level:int = 0):    
    """declares pyomo variables for network location at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for network variables. Defaults to 0.
    """
    instance.scales_network = scale_pyomo_set(instance= instance, scale_level= scale_level)
    instance.X_P = Var(instance.locations, instance.processes, instance.scales_network, within=Binary, doc='Process Binary')
    instance.X_S = Var(instance.locations, instance.resources_store, instance.scales_network, within=Binary, doc='Storage Binary')
    instance.Cap_P = Var(instance.locations, instance.processes, instance.scales_network, within=NonNegativeReals, doc='Process Capacity')
    instance.Cap_S = Var(instance.locations, instance.resources_store, instance.scales_network, within=NonNegativeReals, doc='Storage Capacity')
    return 


def generate_transport_vars(instance: ConcreteModel, scale_level:int = 0):    
    """declares pyomo variables for network location at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for network variables. Defaults to 0.
    """
    instance.scales_transport = scale_pyomo_set(instance= instance, scale_level= scale_level)
    instance.Trans_imp = Var(instance.sinks, instance.sources, instance.resources, instance.transports, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource imported through transport mode')
    instance.Trans_exp = Var(instance.sources, instance.sinks, instance.resources, instance.transports, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource exported through transport mode')
    instance.Trans_imp_cost = Var(instance.sinks, instance.sources, instance.resources, instance.transports, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource imported through transport mode')
    instance.Trans_exp_cost = Var(instance.sources, instance.sinks, instance.resources, instance.transports, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource exported through transport mode')
    instance.Trans_cost = Var(instance.transports, instance.scales_scheduling, within = NonNegativeReals, doc = 'cost of transportation for transport mode')
    return 




def generate_summing_vars(instance:ConcreteModel, scale_level:int = 0):
    """declares pyomo variables to sum mass balance at location and network scales

    Args:
        instance (ConcreteModel): pyomo instance
    """
    instance.scales_summing = scale_pyomo_set(instance= instance, scale_level= scale_level)
    instance.P_location = Var(instance.locations, instance.processes, instance.scales_summing, within=NonNegativeReals, doc='Total production at location')
    instance.S_location = Var(instance.locations, instance.resources, instance.scales_summing, within=NonNegativeReals, doc='Total resource discharge at location')
    instance.C_location = Var(instance.locations, instance.resources, instance.scales_summing, within=NonNegativeReals, doc='Total resource consumption at location')
    instance.B_location = Var(instance.locations, instance.resources, instance.scales_summing, within=NonNegativeReals, doc='Total resource purchase at location')
    instance.P_network = Var(instance.processes, instance.scales_summing, within=NonNegativeReals, doc='Total production from network')
    instance.S_network = Var(instance.resources, instance.scales_summing, within=NonNegativeReals, doc='Total resource discharge from network')
    instance.C_network = Var(instance.resources, instance.scales_summing, within=NonNegativeReals, doc='Total resource consumption from network')
    instance.B_network = Var(instance.resources, instance.scales_summing, within=NonNegativeReals, doc='Total resource purchase from network')
    instance.Trans_cost_network = Var(instance.transports, instance.scales_summing, within = NonNegativeReals, doc = 'cost of transportation for transport mode')
    
    return

def generate_uncertainty_vars(instance:ConcreteModel, scale_level:int= 0):
    """declares pyomo variables for uncertainty analysis of processes and resources

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional): scale for uncertainty. Defaults to 0.
    """
    instance.scale_uncertainty = scale_pyomo_set(instance, scale_level= scale_level)
    instance.Delta_Cost_R = Var(instance.locations, instance.resources_varying, instance.scale_uncertainty, within= NonNegativeReals, doc= 'uncertain purchase price')
    instance.Delta_Cap_P = Var(instance.locations, instance.processes_varying, instance.scale_uncertainty, bounds = (0, 200), within= NonNegativeReals, doc= 'uncertain resource availability')
    instance.Delta_Cap_P_location = Var(instance.locations, instance.processes_varying, instance.scales_summing, within= NonNegativeReals, doc= 'uncertain resource availability - network scale at location')
    instance.Delta_Cap_P_network = Var(instance.processes_varying, instance.scales_summing, within= NonNegativeReals, doc= 'uncertain resource availability - network scale')
    return

def generate_milp_vars(instance:ConcreteModel,  expenditure_scale_level:int=0, scheduling_scale_level:int = 0, network_scale_level:int = 0):
    """declares pyomo variables at chosen scales

    Args:
        instance (ConcreteModel): pyomo instance
        expenditure_scale_level (int, optional): scale for expenditure variables. Defaults to 0.
        scheduling_scale_level (int, optional): scale for scheduling variables. Defaults to 0.
    """
    generate_expenditure_vars(instance = instance, scale_level= network_scale_level)
    generate_scheduling_vars(instance = instance, scale_level= scheduling_scale_level)
    generate_network_vars(instance = instance, scale_level= network_scale_level)
    generate_summing_vars(instance = instance, scale_level= network_scale_level)
    generate_transport_vars(instance= instance, scale_level= scheduling_scale_level)
    return 

def generate_mpmilp_vars(instance:ConcreteModel, expenditure_scale_level:int=0, scheduling_scale_level:int = 0, network_scale_level:int = 0):
    """declares pyomo variables at chosen scales

    Args:
        instance (ConcreteModel): pyomo instance
        expenditure_scale_level (int, optional): scale for expenditure variables. Defaults to 0.
        scheduling_scale_level (int, optional): scale for scheduling variables. Defaults to 0.
    """
    generate_expenditure_vars(instance = instance, scale_level= network_scale_level)
    generate_scheduling_vars(instance = instance, scale_level= scheduling_scale_level)
    generate_network_vars(instance = instance, scale_level= network_scale_level)
    generate_summing_vars(instance = instance, scale_level= network_scale_level)
    generate_transport_vars(instance= instance, scale_level= scheduling_scale_level)
    generate_uncertainty_vars(instance= instance, scale_level= scheduling_scale_level)
    
    return 




#%%

