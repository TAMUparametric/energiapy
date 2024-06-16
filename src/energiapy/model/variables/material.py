from pyomo.environ import ConcreteModel, NonNegativeReals, Var, Binary


def generate_material_vars(instance: ConcreteModel):
    """declares pyomo variables for material at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for network variables. Defaults to 0.
    """

    if hasattr(instance, 'materials') is True:
        instance.material_mode_process = Var(instance.locations, instance.processes, instance.material_modes, instance.materials,
                                             instance.scales_network, within=NonNegativeReals, doc='materials utilized in material mode for each process')
        instance.material_process = Var(instance.locations, instance.processes, instance.materials,
                                        instance.scales_network, within=NonNegativeReals, doc='materials utilized by each process')
        instance.material_location = Var(instance.locations, instance.materials, instance.scales_network,
                                         within=NonNegativeReals, doc='materials utilized at each location')
        instance.material_network = Var(instance.materials, instance.scales_network,
                                        within=NonNegativeReals, doc='materials utilized at network scale')
        instance.X_M = Var(instance.locations, instance.process_material_modes,
                           instance.scales_network, within=Binary, doc='binaries process material combinations')
        instance.Cap_P_M = Var(instance.locations, instance.processes, instance.material_modes, instance.scales_network,
                               within=NonNegativeReals, doc='capacity for process material combinations')
