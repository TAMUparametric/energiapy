"""pyomo transport variables
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
from ...utils.model_utils import scale_pyomo_set

def generate_transport_vars(instance: ConcreteModel, scale_level:int = 0):    
    """declares pyomo variables for network location at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for network variables. Defaults to 0.
    """
    instance.scales_transport = scale_pyomo_set(instance= instance, scale_level= scale_level)
    instance.Trans_imp = Var(instance.sinks, instance.sources, instance.resources_trans, instance.transports, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource imported through transport mode')
    instance.Trans_exp = Var(instance.sources, instance.sinks, instance.resources_trans, instance.transports, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource exported through transport mode')
    instance.Trans_imp_cost = Var(instance.sinks, instance.sources, instance.resources_trans, instance.transports, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource imported through transport mode')
    instance.Trans_exp_cost = Var(instance.sources, instance.sinks, instance.resources_trans, instance.transports, instance.scales_scheduling, within = NonNegativeReals, doc = 'Resource exported through transport mode')
    instance.Trans_cost = Var(instance.transports, instance.scales_scheduling, within = NonNegativeReals, doc = 'cost of transportation for transport mode')
    return 
