from pyomo.environ import ConcreteModel, NonNegativeReals, Var


def generate_emission_vars(instance: ConcreteModel):
    """declares pyomo variables for emission at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for network variables. Defaults to 0.
    """
    instance.carbon_emission_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='Carbon emissions across network at network_scale')
    instance.carbon_emission_location = Var(instance.locations, instance.scales_network,
                                            within=NonNegativeReals, doc='Carbon emissions at location at network_scale')

    instance.global_warming_potential_location = Var(
        instance.locations, instance.scales_network, within=NonNegativeReals, doc='global warming potential caused at each location')
    instance.global_warming_potential_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='global warming potential caused at network scale')
    instance.global_warming_potential_process = Var(
        instance.locations, instance.processes, instance.scales_network, within=NonNegativeReals, doc='global warming potential caused by each process')
    instance.global_warming_potential_resource_consumption = Var(
        instance.locations, instance.resources_purch, instance.scales_network, within=NonNegativeReals, doc='global warming potential caused by each resource at consumption')
    # instance.global_warming_potential_resource_consumption_negative = Var(
    #     instance.locations, instance.resources_purch, instance.scales_network, within=NonNegativeReals, doc='global warming potential caused by each resource at consumption')
    instance.global_warming_potential_resource_discharge = Var(
        instance.locations, instance.resources_sell, instance.scales_network, within=NonNegativeReals, doc='global warming potential caused by each resource at consumption')
    instance.global_warming_potential_resource = Var(
        instance.locations, instance.resources, instance.scales_network, within=NonNegativeReals, doc='global warming potential caused by each resource')
    instance.global_warming_potential_material = Var(instance.locations, instance.processes_materials,
                                                     instance.scales_network, within=NonNegativeReals, doc='global warming potential caused by each material')
    instance.global_warming_potential_material_mode = Var(instance.locations, instance.processes_materials, instance.material_modes,
                                                          instance.scales_network, within=NonNegativeReals, doc='global warming potential caused by each material')

    instance.ozone_depletion_potential_location = Var(
        instance.locations, instance.scales_network, within=NonNegativeReals, doc='ozone depletion potential caused at each location')
    instance.ozone_depletion_potential_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='ozone depletion potential caused at network scale')
    instance.ozone_depletion_potential_process = Var(
        instance.locations, instance.processes, instance.scales_network, within=NonNegativeReals, doc='ozone depletion potential caused by each process')
    instance.ozone_depletion_potential_resource_consumption = Var(
        instance.locations, instance.resources_purch, instance.scales_network, within=NonNegativeReals, doc='ozone depletion potential caused by each resource at consumption')
    instance.ozone_depletion_potential_resource_discharge = Var(
        instance.locations, instance.resources_sell, instance.scales_network, within=NonNegativeReals, doc='ozone depletion potential caused by each resource at consumption')
    instance.ozone_depletion_potential_resource = Var(
        instance.locations, instance.resources, instance.scales_network, within=NonNegativeReals, doc='ozone depletion potential caused by each resource')
    instance.ozone_depletion_potential_material = Var(instance.locations, instance.processes_materials,
                                                      instance.scales_network, within=NonNegativeReals, doc='ozone depletion potential caused by each material')
    instance.ozone_depletion_potential_material_mode = Var(instance.locations, instance.processes_materials, instance.material_modes,
                                                           instance.scales_network, within=NonNegativeReals, doc='ozone depletion potential caused by each material')

    instance.acidification_potential_location = Var(
        instance.locations, instance.scales_network, within=NonNegativeReals, doc='acidification potential caused at each location')
    instance.acidification_potential_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='acidification potential caused at network scale')
    instance.acidification_potential_process = Var(
        instance.locations, instance.processes, instance.scales_network, within=NonNegativeReals, doc='acidification potential caused by each process')
    instance.acidification_potential_resource_consumption = Var(
        instance.locations, instance.resources_purch, instance.scales_network, within=NonNegativeReals, doc='acidification potential caused by each resource at consumption')
    instance.acidification_potential_resource_discharge = Var(
        instance.locations, instance.resources_sell, instance.scales_network, within=NonNegativeReals, doc='acidification potential caused by each resource at consumption')
    instance.acidification_potential_resource = Var(
        instance.locations, instance.resources, instance.scales_network, within=NonNegativeReals, doc='acidification potential caused by each resource')
    instance.acidification_potential_material = Var(instance.locations, instance.processes_materials,
                                                    instance.scales_network, within=NonNegativeReals, doc='acidification potential caused by each material')
    instance.acidification_potential_material_mode = Var(instance.locations, instance.processes_materials, instance.material_modes,
                                                         instance.scales_network, within=NonNegativeReals, doc='acidification potential caused by each material')

    instance.terrestrial_eutrophication_potential_location = Var(
        instance.locations, instance.scales_network, within=NonNegativeReals, doc='terrestrial eutrophication potential caused at each location')
    instance.terrestrial_eutrophication_potential_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='terrestrial eutrophication potential caused at network scale')
    instance.terrestrial_eutrophication_potential_process = Var(
        instance.locations, instance.processes, instance.scales_network, within=NonNegativeReals, doc='terrestrial eutrophication potential caused by each process')
    instance.terrestrial_eutrophication_potential_resource_consumption = Var(
        instance.locations, instance.resources_purch, instance.scales_network, within=NonNegativeReals, doc='terrestrial eutrophication potential caused by each resource at consumption')
    instance.terrestrial_eutrophication_potential_resource_discharge = Var(
        instance.locations, instance.resources_sell, instance.scales_network, within=NonNegativeReals, doc='terrestrial eutrophication potential caused by each resource at consumption')
    instance.terrestrial_eutrophication_potential_resource = Var(
        instance.locations, instance.resources, instance.scales_network, within=NonNegativeReals, doc='terrestrial eutrophication potential caused by each resource')
    instance.terrestrial_eutrophication_potential_material = Var(instance.locations, instance.processes_materials,
                                                                 instance.scales_network, within=NonNegativeReals, doc='terrestrial eutrophication potential caused by each material')
    instance.terrestrial_eutrophication_potential_material_mode = Var(instance.locations, instance.processes_materials, instance.material_modes,
                                                                      instance.scales_network, within=NonNegativeReals, doc='terrestrial eutrophication potential caused by each material')

    instance.freshwater_eutrophication_potential_location = Var(
        instance.locations, instance.scales_network, within=NonNegativeReals, doc='freshwater eutrophication potential caused at each location')
    instance.freshwater_eutrophication_potential_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='freshwater eutrophication potential caused at network scale')
    instance.freshwater_eutrophication_potential_process = Var(
        instance.locations, instance.processes, instance.scales_network, within=NonNegativeReals, doc='freshwater eutrophication potential caused by each process')
    instance.freshwater_eutrophication_potential_resource_consumption = Var(
        instance.locations, instance.resources_purch, instance.scales_network, within=NonNegativeReals, doc='freshwater eutrophication potential caused by each resource at consumption')
    instance.freshwater_eutrophication_potential_resource_discharge = Var(
        instance.locations, instance.resources_sell, instance.scales_network, within=NonNegativeReals, doc='freshwater eutrophication potential caused by each resource at consumption')
    instance.freshwater_eutrophication_potential_resource = Var(
        instance.locations, instance.resources, instance.scales_network, within=NonNegativeReals, doc='freshwater eutrophication potential caused by each resource')
    instance.freshwater_eutrophication_potential_material = Var(instance.locations, instance.processes_materials,
                                                                instance.scales_network, within=NonNegativeReals, doc='freshwater eutrophication potential caused by each material')
    instance.freshwater_eutrophication_potential_material_mode = Var(instance.locations, instance.processes_materials, instance.material_modes,
                                                                     instance.scales_network, within=NonNegativeReals, doc='freshwater eutrophication potential caused by each material')

    instance.marine_eutrophication_potential_location = Var(
        instance.locations, instance.scales_network, within=NonNegativeReals, doc='marine eutrophication potential caused at each location')
    instance.marine_eutrophication_potential_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='marine eutrophication potential caused at network scale')
    instance.marine_eutrophication_potential_process = Var(
        instance.locations, instance.processes, instance.scales_network, within=NonNegativeReals, doc='marine eutrophication potential caused by each process')
    instance.marine_eutrophication_potential_resource_consumption = Var(
        instance.locations, instance.resources_purch, instance.scales_network, within=NonNegativeReals, doc='marine eutrophication potential caused by each resource at consumption')
    instance.marine_eutrophication_potential_resource_discharge = Var(
        instance.locations, instance.resources_sell, instance.scales_network, within=NonNegativeReals, doc='marine eutrophication potential caused by each resource at consumption')
    instance.marine_eutrophication_potential_resource = Var(
        instance.locations, instance.resources, instance.scales_network, within=NonNegativeReals, doc='marine eutrophication potential caused by each resource')
    instance.marine_eutrophication_potential_material = Var(instance.locations, instance.processes_materials,
                                                            instance.scales_network, within=NonNegativeReals, doc='marine eutrophication potential caused by each material')
    instance.marine_eutrophication_potential_material_mode = Var(instance.locations, instance.processes_materials, instance.material_modes,
                                                                 instance.scales_network, within=NonNegativeReals, doc='marine eutrophication potential caused by each material')
