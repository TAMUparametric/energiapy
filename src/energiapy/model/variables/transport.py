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


def generate_transport_vars(instance: ConcreteModel):
    """declares pyomo variables for network location at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
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
    instance.Capex_transport = Var(instance.sources, instance.sinks, instance.transports,
                                   instance.scales_network, within=NonNegativeReals, doc='capex to set up transport mode between sink and source')
    instance.Vopex_transport = Var(instance.sources, instance.sinks, instance.transports,
                                   instance.scales_network, within=NonNegativeReals, doc='vopex of transport mode between sink and source')
    instance.Fopex_transport = Var(instance.sources, instance.sinks, instance.transports,
                                   instance.scales_network, within=NonNegativeReals, doc='fopex of transport mode between sink and source')
    instance.Capex_transport_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='overall capex for transport at the network level')
    instance.Vopex_transport_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='overall vopex for transport at the network level')
    instance.Fopex_transport_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='overall fopex for transport at the network level')

    return
