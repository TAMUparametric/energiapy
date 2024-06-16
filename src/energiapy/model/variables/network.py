from pyomo.environ import ConcreteModel, NonNegativeReals, Var


def generate_network_vars(instance: ConcreteModel):
    """declares pyomo variables for network location at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for network variables. Defaults to 0.
    """

    instance.Cap_P = Var(instance.locations, instance.processes,
                         instance.scales_network, within=NonNegativeReals, doc='Process Capacity')
    instance.Cap_S = Var(instance.locations, instance.resources_store,
                         instance.scales_network, within=NonNegativeReals, doc='Storage Capacity')

    instance.P_location = Var(instance.locations, instance.processes, instance.scales_network,
                              within=NonNegativeReals, doc='Total production at location')

    instance.P_location_material_m = Var(instance.locations, instance.processes, instance.material_modes, instance.scales_network,
                                         within=NonNegativeReals, doc='Total production at location in material mode')

    instance.S_location = Var(instance.locations, instance.resources_sell, instance.scales_network,
                              within=NonNegativeReals, doc='Total resource discharge at location')

    instance.C_location = Var(instance.locations, instance.resources_purch, instance.scales_network,
                              within=NonNegativeReals, doc='Total resource consumption at location')
    instance.P_network = Var(instance.processes, instance.scales_network,
                             within=NonNegativeReals, doc='Total production from network')
    instance.S_network = Var(instance.resources_sell, instance.scales_network,
                             within=NonNegativeReals, doc='Total resource discharge from network')
    instance.C_network = Var(instance.resources_purch, instance.scales_network,
                             within=NonNegativeReals, doc='Total resource consumption from network')

    instance.Inv_network = Var(instance.locations, instance.resources_store,
                               instance.scales_network, doc='Total inventory stored at location for resource')


def generate_network_theta_vars(instance: ConcreteModel):
    """declares multiparametric variable for network location at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for network variables. Defaults to 0.
    """
    instance.Cap_P_theta = Var(instance.locations, instance.processes,
                               instance.scales_network, within=NonNegativeReals, doc='Process Capacity')
