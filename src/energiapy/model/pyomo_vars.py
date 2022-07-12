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
from ..utils.model_utils import scale_set



def generate_expenditure_vars(instance: ConcreteModel, scale_level:int = 0):
    """declares pyomo variables for expenditure at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for scheduling variables. Defaults to 0.
    """
    # exp_scales_list = [instance.scales[i].data() for i in range(scale_level+ 1)]
    instance.scales_expenditure = scale_set(instance= instance, scale_level= scale_level)
    instance.Opex_fix = Var(instance.locations, instance.processes, instance.scales_expenditure, within = NonNegativeReals, doc = 'Fixed Opex' )
    instance.Opex_var = Var(instance.locations, instance.processes, instance.scales_expenditure, within = NonNegativeReals, doc = 'Variable Opex' )
    instance.Capex = Var(instance.locations, instance.processes, instance.scales_expenditure, within = NonNegativeReals, doc = 'Capex' )

    return

def generate_scheduling_vars(instance: ConcreteModel, scale_level:int = 0):    
    """declares pyomo variables for scheduling at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for scheduling variables. Defaults to 0.
    """
    instance.scales_scheduling = scale_set(instance= instance, scale_level= scale_level)
    instance.P = Var(instance.locations, instance.processes, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource Production')
    instance.B = Var(instance.locations, instance.resources, instance.scales_scheduling, within = NonNegativeReals, doc = 'Purchase Expenditure')
    instance.C = Var(instance.locations, instance.resources, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource Consumption')
    instance.S = Var(instance.locations, instance.resources, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource Dispensed/Sold')
    instance.Inv = Var(instance.locations, instance.resources, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource Inventory')

    
    return 



def generate_network_vars(instance: ConcreteModel, scale_level:int = 0):    
    """declares pyomo variables for network location at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for network variables. Defaults to 0.
    """
    instance.scales_network = scale_set(instance= instance, scale_level= scale_level)
    instance.X_P = Var(instance.locations, instance.processes, instance.scales_network, within=Binary, doc='Process Binary')
    instance.X_S = Var(instance.locations, instance.resources_store, instance.scales_network, within=Binary, doc='Storage Binary')
    instance.Cap_P = Var(instance.locations, instance.processes, instance.scales_network, within=NonNegativeReals, doc='Process Capacity')
    instance.Cap_S = Var(instance.locations, instance.resources_store, instance.scales_network, within=NonNegativeReals, doc='Storage Capacity')
    return 

def generate_uncertainty_vars(instance:ConcreteModel, scale_level:int= 0):

    instance.scale_uncertainty = scale_set(instance, scale_level= scale_level)
    
    return

def generate_vars(instance:ConcreteModel, expenditure_scale_level:int=0, scheduling_scale_level:int = 0, network_scale_level:int = 0):
    """declares pyomo variables at chosen scales

    Args:
        instance (ConcreteModel): pyomo instance
        expenditure_scale_level (int, optional): scale for expenditure variables. Defaults to 0.
        scheduling_scale_level (int, optional): scale for scheduling variables. Defaults to 0.
    """
    generate_expenditure_vars(instance = instance, scale_level= expenditure_scale_level)
    generate_scheduling_vars(instance = instance, scale_level= scheduling_scale_level)
    generate_network_vars(instance = instance, scale_level= network_scale_level)
    return 

#%%

