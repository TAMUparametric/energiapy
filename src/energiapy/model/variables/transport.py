"""pyomo transport variables
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import Var, ConcreteModel, NonNegativeReals, Binary


def generate_transport_vars(instance: ConcreteModel):
    """declares pyomo variables for network location at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
    """
    instance.Trans_imp = Var(instance.sinks, instance.sources, instance.resources_trans, instance.transports,
                             instance.scales_scheduling, within=NonNegativeReals, doc='Resource imported through transport mode')
    instance.Trans_exp = Var(instance.sources, instance.sinks, instance.resources_trans, instance.transports,
                             instance.scales_scheduling, within=NonNegativeReals, doc='Resource exported through transport mode')
    instance.Trans_imp_cost = Var(instance.sinks, instance.sources, instance.resources_trans, instance.transports,
                                  instance.scales_scheduling, within=NonNegativeReals, doc='Resource imported through transport mode')
    instance.Trans_exp_cost = Var(instance.sources, instance.sinks, instance.resources_trans, instance.transports,
                                  instance.scales_scheduling, within=NonNegativeReals, doc='Resource exported through transport mode')
    instance.Trans_cost = Var(instance.transports, instance.scales_scheduling,
                              within=NonNegativeReals, doc='cost of transportation for transport mode')
    instance.X_T = Var(instance.sources, instance.sinks, instance.transports,
                       instance.scales_network, within=Binary, doc='binaries for transports being set up')
    return
