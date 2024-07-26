from pyomo.environ import Binary, ConcreteModel, NonNegativeReals, Var


def generate_transport_resource_vars(instance: ConcreteModel):
    """declares pyomo variables for resource balance for transportation

    Args:
        instance (ConcreteModel): pyomo instance
    """

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

def generate_transport_network_binaries(instance: ConcreteModel):
    instance.X_F = Var(instance.sources, instance.sinks, instance.transports,
                    instance.scales_network, within=Binary, doc='binaries for transports being set up')