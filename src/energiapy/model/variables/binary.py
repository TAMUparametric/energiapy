"""pyomo binary variables
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

def generate_network_binary_vars(instance: ConcreteModel, scale_level:int= 0):    
    """declares the following binary variables:

    scales_network_binary: Set of scales to define the network level

    .. math::

        X^{P}_{location, process, scale_{network}} \\textnormal{Process binary, 1 if process is set up, 0 otherwise}

        X^{S}_{location, resource, scale_{network}}: \\textnormal{Storage binary variable, 1 if storage for resource is set up, 0 otherwise}

   Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for network variables. Defaults to 0.
    """
    instance.scales_network_binary = scale_pyomo_set(instance= instance, scale_level= scale_level)
    instance.X_P = Var(instance.locations, instance.processes, instance.scales_network_binary, within=Binary, doc='Process Binary')
    instance.X_S = Var(instance.locations, instance.resources_store, instance.scales_network_binary, within=Binary, doc='Storage Binary')
    return 
