"""transport variables
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import Binary, ConcreteModel, NonNegativeReals, Var


def generate_transport_vars(instance: ConcreteModel, generate_transport_binaries: bool):
    """declares pyomo variables for network location at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        generate_transport_binaries (bool): whether to generate transport binaries
    """
    # instance.Trans_imp = Var(instance.sinks, instance.sources, instance.resources_trans, instance.transports,
    #                          instance.scales_scheduling, within=NonNegativeReals, doc='Resource imported through transport mode')
    # instance.Trans_exp = Var(instance.sources, instance.sinks, instance.resources_trans, instance.transports,
    #                          instance.scales_scheduling, within=NonNegativeReals, doc='Resource exported through transport mode')
    # instance.Trans_imp_cost = Var(instance.sinks, instance.sources, instance.resources_trans, instance.transports,
    #                               instance.scales_scheduling, within=NonNegativeReals, doc='Resource imported through transport mode')
    # instance.Trans_exp_cost = Var(instance.sources, instance.sinks, instance.resources_trans, instance.transports,
    #                               instance.scales_scheduling, within=NonNegativeReals, doc='Resource exported through transport mode')
    # instance.Trans_cost = Var(instance.transports, instance.scales_scheduling,
    #                           within=NonNegativeReals, doc='cost of transportation for transport mode')
    if generate_transport_binaries is True:
        instance.X_F = Var(instance.sources, instance.sinks, instance.transports,
                           instance.scales_network, within=Binary, doc='binaries for transports being set up')

    instance.Cap_F = Var(instance.sources, instance.sinks, instance.transports,
                         instance.scales_network, within=NonNegativeReals, doc='established capacity of transport mode')
    instance.Exp_R = Var(instance.sources, instance.sinks, instance.resources_trans,
                         instance.scales_scheduling, within=NonNegativeReals, doc='resource transported through between locations')
    instance.Exp_F = Var(instance.sources, instance.sinks, instance.transports,
                         instance.scales_scheduling, within=NonNegativeReals, doc='total resources transported mode through between locations')
    instance.Exp_F_network = Var(instance.sources, instance.sinks, instance.transports,
                                 instance.scales_network, within=NonNegativeReals, doc='total resources transported mode through between locations over network scale')
    instance.Exp = Var(instance.sources, instance.sinks, instance.transports, instance.resources_trans,
                       instance.scales_scheduling, within=NonNegativeReals, doc='resource transported through mode between locations')

    return
