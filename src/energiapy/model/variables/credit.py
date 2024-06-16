from pyomo.environ import ConcreteModel, Var, NonNegativeReals


def generate_credit_vars(instance: ConcreteModel, scale_level: int = 0):
    """variables for credits earned

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional): scale at which credits are assigned. Defaults to 0.
    """
    instance.Credit_process = Var(instance.locations, instance.processes, instance.scales_network,
                                  within=NonNegativeReals, doc='credit earned by each process')
    instance.Credit_location = Var(instance.locations,
                                   instance.scales_network, within=NonNegativeReals, doc='credit earned at each location')
    instance.Credit_network = Var(instance.scales_network,
                                  within=NonNegativeReals, doc='credit earned at network level')