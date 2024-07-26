"""binary variables
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import Binary, ConcreteModel, Var


def generate_network_binary_vars(instance: ConcreteModel):
    """declares the following binary variables:

    scales_network_binary: Set of scales to define the network level

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for network variables. Defaults to 0.
    """
    instance.X_P = Var(instance.locations, instance.processes,
                       instance.scales_network, within=Binary, doc='Process Binary')
    instance.X_S = Var(instance.locations, instance.resources_store,
                       instance.scales_network, within=Binary, doc='Storage Binary')
