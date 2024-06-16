from pyomo.environ import ConcreteModel, Var, NonNegativeReals


def generate_land_vars(instance: ConcreteModel, scale_level: int = 0):
    """variables for land usage and costs

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional): scale at which credits are assigned. Defaults to 0.
    """

    instance.Land_process = Var(instance.locations, instance.processes,
                                instance.scales_network, within=NonNegativeReals, doc='Land cost by Process')
    instance.Land_location = Var(instance.locations, instance.scales_network,
                                 within=NonNegativeReals, doc='Land used at location')
    instance.Land_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='Land used at network')

    instance.Land_cost_process = Var(instance.locations, instance.processes,
                                     instance.scales_network, within=NonNegativeReals, doc='Land used by Process')
    instance.Land_cost_location = Var(
        instance.locations, instance.scales_network, within=NonNegativeReals, doc='Land cost at location')
    instance.Land_cost_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='Land cost at network')
