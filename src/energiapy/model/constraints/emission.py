"""emission constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Constraint

from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list


def constraint_carbon_emission_location(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Determines the total CO2_Vent at each location

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: carbon_emission_location
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def carbon_emission_location_rule(instance, location, *scale_list):
        return instance.carbon_emission_location[location, scale_list] == instance.S_location[location, 'CO2_Vent', scale_list]
    instance.constraint_carbon_emission_location = Constraint(
        instance.locations, *scales, rule=carbon_emission_location_rule, doc='carbon_emission_location_process')

    constraint_latex_render(carbon_emission_location_rule)
    return instance.constraint_carbon_emission_location


def constraint_carbon_emission(instance: ConcreteModel, carbon_bound: float,  network_scale_level: int = 0, carbon_reduction_percentage: float = 0.0) -> Constraint:
    """Determines the total network-wide CO2_Vent

    Args:
        instance (ConcreteModel): pyomo model instance
        carbon_bound (float): bound for network carbon emission
        network_scale_level (int, optional):  scale of network decisions. Defaults to 0.
        carbon_reduction_percentage (float, optional): percentage reduction required. Defaults to 0.0.

    Returns:
        Constraint: carbon_emission
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def carbon_emission_rule(instance, location, *scale_list):
        return instance.S_location[location, 'CO2_Vent', scale_list] <= (100.0 - carbon_reduction_percentage)*carbon_bound/100.0
    instance.constraint_carbon_emission = Constraint(
        instance.locations, *scales, rule=carbon_emission_rule, doc='carbon_emission_process')
    constraint_latex_render(carbon_emission_rule)
    return instance.constraint_carbon_emission


def constraint_global_warming_potential_process(instance: ConcreteModel, process_gwp_dict: dict, network_scale_level: int = 0) -> Constraint:
    """calculates global warming potential for each process

    Args:
        instance (ConcreteModel): pyomo model instance
        process_gwp_dict (dict): _description_
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: global_warming_potential_process
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def global_warming_potential_process_rule(instance, location, process,  *scale_list):
        return instance.global_warming_potential_process[location, process, scale_list] == process_gwp_dict[location][process]*instance.Cap_P[location, process, scale_list]
    instance.constraint_global_warming_potential_process = Constraint(
        instance.locations, instance.processes, *scales, rule=global_warming_potential_process_rule, doc='global warming potential for the each process')
    constraint_latex_render(global_warming_potential_process_rule)
    return instance.constraint_global_warming_potential_process


def constraint_global_warming_potential_material_mode(instance: ConcreteModel, material_gwp_dict: dict, process_material_mode_material_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the global warming potential arising from the use of materials for processes in each material mode

    Args:
        instance (ConcreteModel): pyomo model instance
        material_gwp_dict (dict): GWP associated with each material
        process_material_mode_material_dict (dict): Material consumed by each process for each material mode
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: global_warming_potential_material_mode
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def global_warming_potential_material_mode_rule(instance, location, process, material_mode, *scale_list):
        if material_mode in process_material_mode_material_dict[process]:
            return instance.global_warming_potential_material_mode[location, process, material_mode, scale_list] == \
                sum(process_material_mode_material_dict[process][material_mode][material]*material_gwp_dict[location][material]
                    for material in instance.materials if material in process_material_mode_material_dict[process][material_mode]) * instance.Cap_P_M[location, process, material_mode, scale_list]
        else:
            return Constraint.Skip
    instance.constraint_global_warming_potential_material_mode = Constraint(
        instance.locations, instance.processes_materials, instance.material_modes, *scales, rule=global_warming_potential_material_mode_rule, doc='global warming potential for the each material')
    constraint_latex_render(global_warming_potential_material_mode_rule)
    return instance.constraint_global_warming_potential_material_mode


def constraint_global_warming_potential_material(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the global warming potential arising from the use of materials for processes across all material modes

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: global_warming_potential_material
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def global_warming_potential_material_rule(instance, location, process,  *scale_list):
        return instance.global_warming_potential_material[location, process, scale_list] == sum(instance.global_warming_potential_material_mode[location, process, material_mode_, scale_list] for material_mode_ in instance.material_modes)
    instance.constraint_global_warming_potential_material = Constraint(
        instance.locations, instance.processes_materials, *scales, rule=global_warming_potential_material_rule, doc='global warming potential for the each material')
    constraint_latex_render(global_warming_potential_material_rule)
    return instance.constraint_global_warming_potential_material


def constraint_global_warming_potential_resource_consumption(instance: ConcreteModel, resource_gwp_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the global warming potential from each resource consumed

    Args:
        instance (ConcreteModel): pyomo model instance
        resource_gwp_dict (dict): GWP associated with each resource
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: global_warming_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def global_warming_potential_resource_consumption_rule(instance, location, resource,  *scale_list):
        # if resource_gwp_dict[location][resource] > 0:
        return instance.global_warming_potential_resource_consumption[location, resource, scale_list] == resource_gwp_dict[location][resource]*instance.C_location[location, resource, scale_list]
        # else:
        #     return instance.global_warming_potential_resource_consumption[location, resource, scale_list] == 0
    instance.constraint_global_warming_potential_resource_consumption = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=global_warming_potential_resource_consumption_rule, doc='global warming potential for the each resource consumed')
    constraint_latex_render(global_warming_potential_resource_consumption_rule)
    return instance.constraint_global_warming_potential_resource_consumption

# def constraint_global_warming_potential_resource_consumption_negative(instance: ConcreteModel, resource_gwp_dict: dict, network_scale_level: int = 0) -> Constraint:
#     """Calculates the global warming potential from each resource consumed

#     Args:
#         instance (ConcreteModel): pyomo model instance
#         resource_gwp_dict (dict): GWP associated with each resource
#         network_scale_level (int, optional): scale for network decisions. Defaults to 0.

#     Returns:
#         Constraint: global_warming_potential_resource
#     """
#     scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

#     def global_warming_potential_resource_consumption_negative_rule(instance, location, resource,  *scale_list):
#         if resource_gwp_dict[location][resource] > 0:
#             return instance.global_warming_potential_resource_consumption_negative[location, resource, scale_list] == 0
#         else:
#             return instance.global_warming_potential_resource_consumption_negative[location, resource, scale_list] == -1*resource_gwp_dict[location][resource]*instance.C_location[location, resource, scale_list]
#     instance.constraint_global_warming_potential_resource_consumption_negative = Constraint(
#         instance.locations, instance.resources_purch, *scales, rule=global_warming_potential_resource_consumption_negative_rule, doc='global warming potential for the each resource consumed')
#     constraint_latex_render(global_warming_potential_resource_consumption_negative_rule)
#     return instance.constraint_global_warming_potential_resource_consumption_negative


def constraint_global_warming_potential_resource_discharge(instance: ConcreteModel, resource_gwp_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the global warming potential from each resource

    Args:
        instance (ConcreteModel): pyomo model instance
        resource_gwp_dict (dict): GWP associated with each resource
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: global_warming_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def global_warming_potential_resource_discharge_rule(instance, location, resource,  *scale_list):
        return instance.global_warming_potential_resource_discharge[location, resource, scale_list] == resource_gwp_dict[location][resource]*instance.S_location[location, resource, scale_list]
    instance.constraint_global_warming_potential_resource_discharge = Constraint(
        instance.locations, instance.resources_sell, *scales, rule=global_warming_potential_resource_discharge_rule, doc='global warming potential for the each resource discharged')
    constraint_latex_render(global_warming_potential_resource_discharge_rule)
    return instance.constraint_global_warming_potential_resource_discharge


def constraint_global_warming_potential_resource(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the global warming potential from each resource

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: global_warming_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def global_warming_potential_resource_rule(instance, location, resource,  *scale_list):
        # if (resource in instance.resources_sell) or (resource in instance.resources_purch):
        if resource in instance.resources_sell:
            sales = instance.global_warming_potential_resource_discharge[location,
                                                                         resource, scale_list]
        else:
            sales = 0

        if resource in instance.resources_purch:
            purch = instance.global_warming_potential_resource_consumption[
                location, resource, scale_list]

        else:
            purch = 0
        return instance.global_warming_potential_resource[location, resource, scale_list] == sales + purch

        # else:
        #     return Constraint.Skip
    instance.constraint_global_warming_potential_resource = Constraint(
        instance.locations, instance.resources, *scales, rule=global_warming_potential_resource_rule, doc='global warming potential for the each resource')
    constraint_latex_render(global_warming_potential_resource_rule)
    return instance.constraint_global_warming_potential_resource


def constraint_global_warming_potential_location(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the global warming potential at each location

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: global_warming_potential_location
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def global_warming_potential_location_rule(instance, location, *scale_list):
        gwp_process = sum(
            instance.global_warming_potential_process[location, process_, scale_list] for process_ in instance.processes)
        gwp_resource = sum(
            instance.global_warming_potential_resource[location, resource_, scale_list] for resource_ in instance.resources)
        gwp_material = sum(
            instance.global_warming_potential_material[location, material_, scale_list] for material_ in instance.processes_materials)

        return instance.global_warming_potential_location[location, scale_list] == gwp_process + gwp_resource + gwp_material
    instance.constraint_global_warming_potential_location = Constraint(
        instance.locations, *scales, rule=global_warming_potential_location_rule, doc='global warming potential for the each location')
    constraint_latex_render(global_warming_potential_location_rule)
    return instance.constraint_global_warming_potential_location


def constraint_global_warming_potential_network(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Global warming potential for the whole network

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: global_warming_potential_network
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def global_warming_potential_network_rule(instance, *scale_list):
        return instance.global_warming_potential_network[scale_list] == \
            sum(instance.global_warming_potential_location[location_,
                scale_list] for location_ in instance.locations)
    instance.constraint_global_warming_potential_network = Constraint(
        *scales, rule=global_warming_potential_network_rule, doc='global warming potential for the whole network')
    constraint_latex_render(global_warming_potential_network_rule)
    return instance.constraint_global_warming_potential_network


def constraint_global_warming_potential_network_reduction(instance: ConcreteModel, network_scale_level: int = 0, gwp_reduction_pct: float = 0, gwp: float = 0) -> Constraint:
    """Required reduction in global warming potential at network level

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.
        gwp_reduction_pct (float, optional): GWP reduction required. Defaults to 0.
        gwp (float, optional): Base Case (Current) GWP. Defaults to 0.

    Returns:
        Constraint: global_warming_potential_network_reduction
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def global_warming_potential_network_reduction_rule(instance, *scale_list):
        return instance.global_warming_potential_network[scale_list] <= gwp*(1 - gwp_reduction_pct/100)
    instance.constraint_global_warming_potential_network_reduction = Constraint(
        *scales, rule=global_warming_potential_network_reduction_rule, doc='global warming potential for the whole network')
    constraint_latex_render(global_warming_potential_network_reduction_rule)
    return instance.constraint_global_warming_potential_network_reduction


def constraint_global_warming_potential_network_bound(instance: ConcreteModel, gwp_bound: float, network_scale_level: int = 0) -> Constraint:
    """Required bound in global warming potential at network level

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.
        gwp_bound_pct (float, optional): GWP bound required. Defaults to 0.
        gwp (float, optional): Base Case (Current) GWP. Defaults to 0.

    Returns:
        Constraint: global_warming_potential_network_bound
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def global_warming_potential_network_bound_rule(instance, *scale_list):
        return instance.global_warming_potential_network[scale_list] <= gwp_bound
    constraint_latex_render(global_warming_potential_network_bound_rule)
    return Constraint(
        *scales, rule=global_warming_potential_network_bound_rule, doc='global warming potential bound for the whole network')


def constraint_global_warming_potential_20_resource(instance: ConcreteModel, emission_dict: dict, network_scale_level: int = 0) -> Constraint:
    """calculates global warming potential for each process

    Args:
        instance (ConcreteModel): pyomo model instance
        process_gwp_dict (dict): _description_
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: global_warming_potential_process
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def global_warming_potential_process_rule(instance, location, process, resource, *scale_list):
        return instance.global_warming_potential_20_resource[location, resource, scale_list] == emission_dict[location][process][resource]*instance.Cap_P[location, process, scale_list]
    instance.constraint_global_warming_potential_process = Constraint(
        instance.locations, instance.processes, *scales, rule=global_warming_potential_process_rule, doc='global warming potential for the each process')
    constraint_latex_render(global_warming_potential_process_rule)
    return instance.constraint_global_warming_potential_process

# *--------------------Ozone Depletion Potential-------------------------------------------------------


def constraint_ozone_depletion_potential_process(instance: ConcreteModel, process_odp_dict: dict, network_scale_level: int = 0) -> Constraint:
    """calculates ozone depletion potential for each process

    Args:
        instance (ConcreteModel): pyomo model instance
        process_odp_dict (dict): _description_
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: ozone_depletion_potential_process
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def ozone_depletion_potential_process_rule(instance, location, process,  *scale_list):
        return instance.ozone_depletion_potential_process[location, process, scale_list] == process_odp_dict[location][process]*instance.Cap_P[location, process, scale_list]
    instance.constraint_ozone_depletion_potential_process = Constraint(
        instance.locations, instance.processes, *scales, rule=ozone_depletion_potential_process_rule, doc='ozone depletion potential for the each process')
    constraint_latex_render(ozone_depletion_potential_process_rule)
    return instance.constraint_ozone_depletion_potential_process


def constraint_ozone_depletion_potential_material_mode(instance: ConcreteModel, material_odp_dict: dict, process_material_mode_material_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the ozone depletion potential arising from the use of materials for processes in each material mode

    Args:
        instance (ConcreteModel): pyomo model instance
        material_odp_dict (dict): odp associated with each material
        process_material_mode_material_dict (dict): Material consumed by each process for each material mode
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: ozone_depletion_potential_material_mode
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def ozone_depletion_potential_material_mode_rule(instance, location, process, material_mode, *scale_list):
        if material_mode in process_material_mode_material_dict[process]:
            return instance.ozone_depletion_potential_material_mode[location, process, material_mode, scale_list] == \
                sum(process_material_mode_material_dict[process][material_mode][material]*material_odp_dict[location][material]
                    for material in instance.materials if material in process_material_mode_material_dict[process][material_mode]) * instance.Cap_P_M[location, process, material_mode, scale_list]
        else:
            return Constraint.Skip
    instance.constraint_ozone_depletion_potential_material_mode = Constraint(
        instance.locations, instance.processes_materials, instance.material_modes, *scales, rule=ozone_depletion_potential_material_mode_rule, doc='ozone depletion potential for the each material')
    constraint_latex_render(ozone_depletion_potential_material_mode_rule)
    return instance.constraint_ozone_depletion_potential_material_mode


def constraint_ozone_depletion_potential_material(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the ozone depletion potential arising from the use of materials for processes across all material modes

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: ozone_depletion_potential_material
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def ozone_depletion_potential_material_rule(instance, location, process,  *scale_list):
        return instance.ozone_depletion_potential_material[location, process, scale_list] == sum(instance.ozone_depletion_potential_material_mode[location, process, material_mode_, scale_list] for material_mode_ in instance.material_modes)
    instance.constraint_ozone_depletion_potential_material = Constraint(
        instance.locations, instance.processes_materials, *scales, rule=ozone_depletion_potential_material_rule, doc='ozone depletion potential for the each material')
    constraint_latex_render(ozone_depletion_potential_material_rule)
    return instance.constraint_ozone_depletion_potential_material


def constraint_ozone_depletion_potential_resource_consumption(instance: ConcreteModel, resource_odp_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the ozone depletion potential from each resource consumed

    Args:
        instance (ConcreteModel): pyomo model instance
        resource_odp_dict (dict): odp associated with each resource
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: ozone_depletion_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def ozone_depletion_potential_resource_consumption_rule(instance, location, resource,  *scale_list):
        return instance.ozone_depletion_potential_resource_consumption[location, resource, scale_list] == resource_odp_dict[location][resource]*instance.C_location[location, resource, scale_list]
    instance.constraint_ozone_depletion_potential_resource_consumption = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=ozone_depletion_potential_resource_consumption_rule, doc='ozone depletion potential for the each resource consumed')
    constraint_latex_render(
        ozone_depletion_potential_resource_consumption_rule)
    return instance.constraint_ozone_depletion_potential_resource_consumption


def constraint_ozone_depletion_potential_resource_discharge(instance: ConcreteModel, resource_odp_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the ozone depletion potential from each resource

    Args:
        instance (ConcreteModel): pyomo model instance
        resource_odp_dict (dict): odp associated with each resource
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: ozone_depletion_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def ozone_depletion_potential_resource_discharge_rule(instance, location, resource,  *scale_list):
        return instance.ozone_depletion_potential_resource_discharge[location, resource, scale_list] == resource_odp_dict[location][resource]*instance.S_location[location, resource, scale_list]
    instance.constraint_ozone_depletion_potential_resource_discharge = Constraint(
        instance.locations, instance.resources_sell, *scales, rule=ozone_depletion_potential_resource_discharge_rule, doc='ozone depletion potential for the each resource discharged')
    constraint_latex_render(ozone_depletion_potential_resource_discharge_rule)
    return instance.constraint_ozone_depletion_potential_resource_discharge


def constraint_ozone_depletion_potential_resource(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the ozone depletion potential from each resource

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: ozone_depletion_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def ozone_depletion_potential_resource_rule(instance, location, resource,  *scale_list):
        # if (resource in instance.resources_sell) or (resource in instance.resources_purch):
        if resource in instance.resources_sell:
            sales = instance.ozone_depletion_potential_resource_discharge[
                location, resource, scale_list]
        else:
            sales = 0

        if resource in instance.resources_purch:
            purch = instance.ozone_depletion_potential_resource_consumption[
                location, resource, scale_list]

        else:
            purch = 0
        return instance.ozone_depletion_potential_resource[location, resource, scale_list] == sales + purch

        # else:
        #     return Constraint.Skip
    instance.constraint_ozone_depletion_potential_resource = Constraint(
        instance.locations, instance.resources, *scales, rule=ozone_depletion_potential_resource_rule, doc='ozone depletion potential for the each resource')
    constraint_latex_render(ozone_depletion_potential_resource_rule)
    return instance.constraint_ozone_depletion_potential_resource


def constraint_ozone_depletion_potential_location(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the ozone depletion potential at each location

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: ozone_depletion_potential_location
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def ozone_depletion_potential_location_rule(instance, location, *scale_list):
        odp_process = sum(
            instance.ozone_depletion_potential_process[location, process_, scale_list] for process_ in instance.processes)
        odp_resource = sum(
            instance.ozone_depletion_potential_resource[location, resource_, scale_list] for resource_ in instance.resources)
        odp_material = sum(
            instance.ozone_depletion_potential_material[location, material_, scale_list] for material_ in instance.processes_materials)

        return instance.ozone_depletion_potential_location[location, scale_list] == odp_process + odp_resource + odp_material
    instance.constraint_ozone_depletion_potential_location = Constraint(
        instance.locations, *scales, rule=ozone_depletion_potential_location_rule, doc='ozone depletion potential for the each location')
    constraint_latex_render(ozone_depletion_potential_location_rule)
    return instance.constraint_ozone_depletion_potential_location


def constraint_ozone_depletion_potential_network(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """ozone depletion potential for the whole network

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: ozone_depletion_potential_network
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def ozone_depletion_potential_network_rule(instance, *scale_list):
        return instance.ozone_depletion_potential_network[scale_list] == \
            sum(instance.ozone_depletion_potential_location[location_,
                scale_list] for location_ in instance.locations)
    instance.constraint_ozone_depletion_potential_network = Constraint(
        *scales, rule=ozone_depletion_potential_network_rule, doc='ozone depletion potential for the whole network')
    constraint_latex_render(ozone_depletion_potential_network_rule)
    return instance.constraint_ozone_depletion_potential_network

# *-------------------------------------Acidification Potential------------------------------------------------


def constraint_acidification_potential_process(instance: ConcreteModel, process_acid_dict: dict, network_scale_level: int = 0) -> Constraint:
    """calculates acidification potential for each process

    Args:
        instance (ConcreteModel): pyomo model instance
        process_acid_dict (dict): _description_
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: acidification_potential_process
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def acidification_potential_process_rule(instance, location, process,  *scale_list):
        return instance.acidification_potential_process[location, process, scale_list] == process_acid_dict[location][process]*instance.Cap_P[location, process, scale_list]
    instance.constraint_acidification_potential_process = Constraint(
        instance.locations, instance.processes, *scales, rule=acidification_potential_process_rule, doc='acidification potential for the each process')
    constraint_latex_render(acidification_potential_process_rule)
    return instance.constraint_acidification_potential_process


def constraint_acidification_potential_material_mode(instance: ConcreteModel, material_acid_dict: dict, process_material_mode_material_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the acidification potential arising from the use of materials for processes in each material mode

    Args:
        instance (ConcreteModel): pyomo model instance
        material_acid_dict (dict): acid associated with each material
        process_material_mode_material_dict (dict): Material consumed by each process for each material mode
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: acidification_potential_material_mode
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def acidification_potential_material_mode_rule(instance, location, process, material_mode, *scale_list):
        if material_mode in process_material_mode_material_dict[process]:
            return instance.acidification_potential_material_mode[location, process, material_mode, scale_list] == \
                sum(process_material_mode_material_dict[process][material_mode][material]*material_acid_dict[location][material]
                    for material in instance.materials if material in process_material_mode_material_dict[process][material_mode]) * instance.Cap_P_M[location, process, material_mode, scale_list]
        else:
            return Constraint.Skip
    instance.constraint_acidification_potential_material_mode = Constraint(
        instance.locations, instance.processes_materials, instance.material_modes, *scales, rule=acidification_potential_material_mode_rule, doc='acidification potential for the each material')
    constraint_latex_render(acidification_potential_material_mode_rule)
    return instance.constraint_acidification_potential_material_mode


def constraint_acidification_potential_material(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the acidification potential arising from the use of materials for processes across all material modes

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: acidification_potential_material
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def acidification_potential_material_rule(instance, location, process,  *scale_list):
        return instance.acidification_potential_material[location, process, scale_list] == sum(instance.acidification_potential_material_mode[location, process, material_mode_, scale_list] for material_mode_ in instance.material_modes)
    instance.constraint_acidification_potential_material = Constraint(
        instance.locations, instance.processes_materials, *scales, rule=acidification_potential_material_rule, doc='acidification potential for the each material')
    constraint_latex_render(acidification_potential_material_rule)
    return instance.constraint_acidification_potential_material


def constraint_acidification_potential_resource_consumption(instance: ConcreteModel, resource_acid_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the acidification potential from each resource consumed

    Args:
        instance (ConcreteModel): pyomo model instance
        resource_acid_dict (dict): acid associated with each resource
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: acidification_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def acidification_potential_resource_consumption_rule(instance, location, resource,  *scale_list):
        return instance.acidification_potential_resource_consumption[location, resource, scale_list] == resource_acid_dict[location][resource]*instance.C_location[location, resource, scale_list]
    instance.constraint_acidification_potential_resource_consumption = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=acidification_potential_resource_consumption_rule, doc='acidification potential for the each resource consumed')
    constraint_latex_render(acidification_potential_resource_consumption_rule)
    return instance.constraint_acidification_potential_resource_consumption


def constraint_acidification_potential_resource_discharge(instance: ConcreteModel, resource_acid_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the acidification potential from each resource

    Args:
        instance (ConcreteModel): pyomo model instance
        resource_acid_dict (dict): acid associated with each resource
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: acidification_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def acidification_potential_resource_discharge_rule(instance, location, resource,  *scale_list):
        return instance.acidification_potential_resource_discharge[location, resource, scale_list] == resource_acid_dict[location][resource]*instance.S_location[location, resource, scale_list]
    instance.constraint_acidification_potential_resource_discharge = Constraint(
        instance.locations, instance.resources_sell, *scales, rule=acidification_potential_resource_discharge_rule, doc='acidification potential for the each resource discharged')
    constraint_latex_render(acidification_potential_resource_discharge_rule)
    return instance.constraint_acidification_potential_resource_discharge


def constraint_acidification_potential_resource(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the acidification potential from each resource

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: acidification_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def acidification_potential_resource_rule(instance, location, resource,  *scale_list):
        # if (resource in instance.resources_sell) or (resource in instance.resources_purch):
        if resource in instance.resources_sell:
            sales = instance.acidification_potential_resource_discharge[location,
                                                                        resource, scale_list]
        else:
            sales = 0

        if resource in instance.resources_purch:
            purch = instance.acidification_potential_resource_consumption[
                location, resource, scale_list]

        else:
            purch = 0
        return instance.acidification_potential_resource[location, resource, scale_list] == sales + purch

        # else:
        #     return Constraint.Skip
    instance.constraint_acidification_potential_resource = Constraint(
        instance.locations, instance.resources, *scales, rule=acidification_potential_resource_rule, doc='acidification potential for the each resource')
    constraint_latex_render(acidification_potential_resource_rule)
    return instance.constraint_acidification_potential_resource


def constraint_acidification_potential_location(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the acidification potential at each location

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: acidification_potential_location
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def acidification_potential_location_rule(instance, location, *scale_list):
        acid_process = sum(
            instance.acidification_potential_process[location, process_, scale_list] for process_ in instance.processes)
        acid_resource = sum(
            instance.acidification_potential_resource[location, resource_, scale_list] for resource_ in instance.resources)
        acid_material = sum(
            instance.acidification_potential_material[location, material_, scale_list] for material_ in instance.processes_materials)

        return instance.acidification_potential_location[location, scale_list] == acid_process + acid_resource + acid_material
    instance.constraint_acidification_potential_location = Constraint(
        instance.locations, *scales, rule=acidification_potential_location_rule, doc='acidification potential for the each location')
    constraint_latex_render(acidification_potential_location_rule)
    return instance.constraint_acidification_potential_location


def constraint_acidification_potential_network(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """acidification potential for the whole network

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: acidification_potential_network
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def acidification_potential_network_rule(instance, *scale_list):
        return instance.acidification_potential_network[scale_list] == \
            sum(instance.acidification_potential_location[location_,
                scale_list] for location_ in instance.locations)
    instance.constraint_acidification_potential_network = Constraint(
        *scales, rule=acidification_potential_network_rule, doc='acidification potential for the whole network')
    constraint_latex_render(acidification_potential_network_rule)
    return instance.constraint_acidification_potential_network

# *-------------------Terrestrial Eutrophication Potential-------------------------------------------------------------


def constraint_terrestrial_eutrophication_potential_process(instance: ConcreteModel, process_eutt_dict: dict, network_scale_level: int = 0) -> Constraint:
    """calculates terrestrial eutrophication potential for each process

    Args:
        instance (ConcreteModel): pyomo model instance
        process_eutt_dict (dict): _description_
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: terrestrial_eutrophication_potential_process
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def terrestrial_eutrophication_potential_process_rule(instance, location, process,  *scale_list):
        return instance.terrestrial_eutrophication_potential_process[location, process, scale_list] == process_eutt_dict[location][process]*instance.Cap_P[location, process, scale_list]
    instance.constraint_terrestrial_eutrophication_potential_process = Constraint(
        instance.locations, instance.processes, *scales, rule=terrestrial_eutrophication_potential_process_rule, doc='terrestrial eutrophication potential for the each process')
    constraint_latex_render(terrestrial_eutrophication_potential_process_rule)
    return instance.constraint_terrestrial_eutrophication_potential_process


def constraint_terrestrial_eutrophication_potential_material_mode(instance: ConcreteModel, material_eutt_dict: dict, process_material_mode_material_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the terrestrial eutrophication potential arising from the use of materials for processes in each material mode

    Args:
        instance (ConcreteModel): pyomo model instance
        material_eutt_dict (dict): eutt associated with each material
        process_material_mode_material_dict (dict): Material consumed by each process for each material mode
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: terrestrial_eutrophication_potential_material_mode
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def terrestrial_eutrophication_potential_material_mode_rule(instance, location, process, material_mode, *scale_list):
        if material_mode in process_material_mode_material_dict[process]:
            return instance.terrestrial_eutrophication_potential_material_mode[location, process, material_mode, scale_list] == \
                sum(process_material_mode_material_dict[process][material_mode][material]*material_eutt_dict[location][material]
                    for material in instance.materials if material in process_material_mode_material_dict[process][material_mode]) * instance.Cap_P_M[location, process, material_mode, scale_list]
        else:
            return Constraint.Skip
    instance.constraint_terrestrial_eutrophication_potential_material_mode = Constraint(
        instance.locations, instance.processes_materials, instance.material_modes, *scales, rule=terrestrial_eutrophication_potential_material_mode_rule, doc='terrestrial eutrophication potential for the each material')
    constraint_latex_render(
        terrestrial_eutrophication_potential_material_mode_rule)
    return instance.constraint_terrestrial_eutrophication_potential_material_mode


def constraint_terrestrial_eutrophication_potential_material(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the terrestrial eutrophication potential arising from the use of materials for processes across all material modes

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: terrestrial_eutrophication_potential_material
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def terrestrial_eutrophication_potential_material_rule(instance, location, process,  *scale_list):
        return instance.terrestrial_eutrophication_potential_material[location, process, scale_list] == sum(instance.terrestrial_eutrophication_potential_material_mode[location, process, material_mode_, scale_list] for material_mode_ in instance.material_modes)
    instance.constraint_terrestrial_eutrophication_potential_material = Constraint(
        instance.locations, instance.processes_materials, *scales, rule=terrestrial_eutrophication_potential_material_rule, doc='terrestrial eutrophication potential for the each material')
    constraint_latex_render(terrestrial_eutrophication_potential_material_rule)
    return instance.constraint_terrestrial_eutrophication_potential_material


def constraint_terrestrial_eutrophication_potential_resource_consumption(instance: ConcreteModel, resource_eutt_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the terrestrial eutrophication potential from each resource consumed

    Args:
        instance (ConcreteModel): pyomo model instance
        resource_eutt_dict (dict): eutt associated with each resource
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: terrestrial_eutrophication_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def terrestrial_eutrophication_potential_resource_consumption_rule(instance, location, resource,  *scale_list):
        return instance.terrestrial_eutrophication_potential_resource_consumption[location, resource, scale_list] == resource_eutt_dict[location][resource]*instance.C_location[location, resource, scale_list]
    instance.constraint_terrestrial_eutrophication_potential_resource_consumption = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=terrestrial_eutrophication_potential_resource_consumption_rule, doc='terrestrial eutrophication potential for the each resource consumed')
    constraint_latex_render(
        terrestrial_eutrophication_potential_resource_consumption_rule)
    return instance.constraint_terrestrial_eutrophication_potential_resource_consumption


def constraint_terrestrial_eutrophication_potential_resource_discharge(instance: ConcreteModel, resource_eutt_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the terrestrial eutrophication potential from each resource

    Args:
        instance (ConcreteModel): pyomo model instance
        resource_eutt_dict (dict): eutt associated with each resource
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: terrestrial_eutrophication_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def terrestrial_eutrophication_potential_resource_discharge_rule(instance, location, resource,  *scale_list):
        return instance.terrestrial_eutrophication_potential_resource_discharge[location, resource, scale_list] == resource_eutt_dict[location][resource]*instance.S_location[location, resource, scale_list]
    instance.constraint_terrestrial_eutrophication_potential_resource_discharge = Constraint(
        instance.locations, instance.resources_sell, *scales, rule=terrestrial_eutrophication_potential_resource_discharge_rule, doc='terrestrial eutrophication potential for the each resource discharged')
    constraint_latex_render(
        terrestrial_eutrophication_potential_resource_discharge_rule)
    return instance.constraint_terrestrial_eutrophication_potential_resource_discharge


def constraint_terrestrial_eutrophication_potential_resource(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the terrestrial eutrophication potential from each resource

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: terrestrial_eutrophication_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def terrestrial_eutrophication_potential_resource_rule(instance, location, resource,  *scale_list):
        # if (resource in instance.resources_sell) or (resource in instance.resources_purch):
        if resource in instance.resources_sell:
            sales = instance.terrestrial_eutrophication_potential_resource_discharge[
                location, resource, scale_list]
        else:
            sales = 0

        if resource in instance.resources_purch:
            purch = instance.terrestrial_eutrophication_potential_resource_consumption[
                location, resource, scale_list]

        else:
            purch = 0
        return instance.terrestrial_eutrophication_potential_resource[location, resource, scale_list] == sales + purch

        # else:
        #     return Constraint.Skip
    instance.constraint_terrestrial_eutrophication_potential_resource = Constraint(
        instance.locations, instance.resources, *scales, rule=terrestrial_eutrophication_potential_resource_rule, doc='terrestrial eutrophication potential for the each resource')
    constraint_latex_render(terrestrial_eutrophication_potential_resource_rule)
    return instance.constraint_terrestrial_eutrophication_potential_resource


def constraint_terrestrial_eutrophication_potential_location(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the terrestrial eutrophication potential at each location

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: terrestrial_eutrophication_potential_location
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def terrestrial_eutrophication_potential_location_rule(instance, location, *scale_list):
        eutt_process = sum(
            instance.terrestrial_eutrophication_potential_process[location, process_, scale_list] for process_ in instance.processes)
        eutt_resource = sum(
            instance.terrestrial_eutrophication_potential_resource[location, resource_, scale_list] for resource_ in instance.resources)
        eutt_material = sum(
            instance.terrestrial_eutrophication_potential_material[location, material_, scale_list] for material_ in instance.processes_materials)

        return instance.terrestrial_eutrophication_potential_location[location, scale_list] == eutt_process + eutt_resource + eutt_material
    instance.constraint_terrestrial_eutrophication_potential_location = Constraint(
        instance.locations, *scales, rule=terrestrial_eutrophication_potential_location_rule, doc='terrestrial eutrophication potential for the each location')
    constraint_latex_render(terrestrial_eutrophication_potential_location_rule)
    return instance.constraint_terrestrial_eutrophication_potential_location


def constraint_terrestrial_eutrophication_potential_network(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """terrestrial eutrophication potential for the whole network

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: terrestrial_eutrophication_potential_network
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def terrestrial_eutrophication_potential_network_rule(instance, *scale_list):
        return instance.terrestrial_eutrophication_potential_network[scale_list] == \
            sum(instance.terrestrial_eutrophication_potential_location[location_,
                scale_list] for location_ in instance.locations)
    instance.constraint_terrestrial_eutrophication_potential_network = Constraint(
        *scales, rule=terrestrial_eutrophication_potential_network_rule, doc='terrestrial eutrophication potential for the whole network')
    constraint_latex_render(terrestrial_eutrophication_potential_network_rule)
    return instance.constraint_terrestrial_eutrophication_potential_network

# *-------------------Freshwater Eutrophication Potential-------------------------------------------------------------


def constraint_freshwater_eutrophication_potential_process(instance: ConcreteModel, process_eutf_dict: dict, network_scale_level: int = 0) -> Constraint:
    """calculates freshwater eutrophication potential for each process

    Args:
        instance (ConcreteModel): pyomo model instance
        process_eutf_dict (dict): _description_
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: freshwater_eutrophication_potential_process
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def freshwater_eutrophication_potential_process_rule(instance, location, process,  *scale_list):
        return instance.freshwater_eutrophication_potential_process[location, process, scale_list] == process_eutf_dict[location][process]*instance.Cap_P[location, process, scale_list]
    instance.constraint_freshwater_eutrophication_potential_process = Constraint(
        instance.locations, instance.processes, *scales, rule=freshwater_eutrophication_potential_process_rule, doc='freshwater eutrophication potential for the each process')
    constraint_latex_render(freshwater_eutrophication_potential_process_rule)
    return instance.constraint_freshwater_eutrophication_potential_process


def constraint_freshwater_eutrophication_potential_material_mode(instance: ConcreteModel, material_eutf_dict: dict, process_material_mode_material_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the freshwater eutrophication potential arising from the use of materials for processes in each material mode

    Args:
        instance (ConcreteModel): pyomo model instance
        material_eutf_dict (dict): eutf associated with each material
        process_material_mode_material_dict (dict): Material consumed by each process for each material mode
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: freshwater_eutrophication_potential_material_mode
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def freshwater_eutrophication_potential_material_mode_rule(instance, location, process, material_mode, *scale_list):
        if material_mode in process_material_mode_material_dict[process]:
            return instance.freshwater_eutrophication_potential_material_mode[location, process, material_mode, scale_list] == \
                sum(process_material_mode_material_dict[process][material_mode][material]*material_eutf_dict[location][material]
                    for material in instance.materials if material in process_material_mode_material_dict[process][material_mode]) * instance.Cap_P_M[location, process, material_mode, scale_list]
        else:
            return Constraint.Skip
    instance.constraint_freshwater_eutrophication_potential_material_mode = Constraint(
        instance.locations, instance.processes_materials, instance.material_modes, *scales, rule=freshwater_eutrophication_potential_material_mode_rule, doc='freshwater eutrophication potential for the each material')
    constraint_latex_render(
        freshwater_eutrophication_potential_material_mode_rule)
    return instance.constraint_freshwater_eutrophication_potential_material_mode


def constraint_freshwater_eutrophication_potential_material(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the freshwater eutrophication potential arising from the use of materials for processes across all material modes

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: freshwater_eutrophication_potential_material
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def freshwater_eutrophication_potential_material_rule(instance, location, process,  *scale_list):
        return instance.freshwater_eutrophication_potential_material[location, process, scale_list] == sum(instance.freshwater_eutrophication_potential_material_mode[location, process, material_mode_, scale_list] for material_mode_ in instance.material_modes)
    instance.constraint_freshwater_eutrophication_potential_material = Constraint(
        instance.locations, instance.processes_materials, *scales, rule=freshwater_eutrophication_potential_material_rule, doc='freshwater eutrophication potential for the each material')
    constraint_latex_render(freshwater_eutrophication_potential_material_rule)
    return instance.constraint_freshwater_eutrophication_potential_material


def constraint_freshwater_eutrophication_potential_resource_consumption(instance: ConcreteModel, resource_eutf_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the freshwater eutrophication potential from each resource consumed

    Args:
        instance (ConcreteModel): pyomo model instance
        resource_eutf_dict (dict): eutf associated with each resource
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: freshwater_eutrophication_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def freshwater_eutrophication_potential_resource_consumption_rule(instance, location, resource,  *scale_list):
        return instance.freshwater_eutrophication_potential_resource_consumption[location, resource, scale_list] == resource_eutf_dict[location][resource]*instance.C_location[location, resource, scale_list]
    instance.constraint_freshwater_eutrophication_potential_resource_consumption = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=freshwater_eutrophication_potential_resource_consumption_rule, doc='freshwater eutrophication potential for the each resource consumed')
    constraint_latex_render(
        freshwater_eutrophication_potential_resource_consumption_rule)
    return instance.constraint_freshwater_eutrophication_potential_resource_consumption


def constraint_freshwater_eutrophication_potential_resource_discharge(instance: ConcreteModel, resource_eutf_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the freshwater eutrophication potential from each resource

    Args:
        instance (ConcreteModel): pyomo model instance
        resource_eutf_dict (dict): eutf associated with each resource
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: freshwater_eutrophication_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def freshwater_eutrophication_potential_resource_discharge_rule(instance, location, resource,  *scale_list):
        return instance.freshwater_eutrophication_potential_resource_discharge[location, resource, scale_list] == resource_eutf_dict[location][resource]*instance.S_location[location, resource, scale_list]
    instance.constraint_freshwater_eutrophication_potential_resource_discharge = Constraint(
        instance.locations, instance.resources_sell, *scales, rule=freshwater_eutrophication_potential_resource_discharge_rule, doc='freshwater eutrophication potential for the each resource discharged')
    constraint_latex_render(
        freshwater_eutrophication_potential_resource_discharge_rule)
    return instance.constraint_freshwater_eutrophication_potential_resource_discharge


def constraint_freshwater_eutrophication_potential_resource(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the freshwater eutrophication potential from each resource

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: freshwater_eutrophication_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def freshwater_eutrophication_potential_resource_rule(instance, location, resource,  *scale_list):
        # if (resource in instance.resources_sell) or (resource in instance.resources_purch):
        if resource in instance.resources_sell:
            sales = instance.freshwater_eutrophication_potential_resource_discharge[
                location, resource, scale_list]
        else:
            sales = 0

        if resource in instance.resources_purch:
            purch = instance.freshwater_eutrophication_potential_resource_consumption[
                location, resource, scale_list]

        else:
            purch = 0
        return instance.freshwater_eutrophication_potential_resource[location, resource, scale_list] == sales + purch

        # else:
        #     return Constraint.Skip
    instance.constraint_freshwater_eutrophication_potential_resource = Constraint(
        instance.locations, instance.resources, *scales, rule=freshwater_eutrophication_potential_resource_rule, doc='freshwater eutrophication potential for the each resource')
    constraint_latex_render(freshwater_eutrophication_potential_resource_rule)
    return instance.constraint_freshwater_eutrophication_potential_resource


def constraint_freshwater_eutrophication_potential_location(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the freshwater eutrophication potential at each location

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: freshwater_eutrophication_potential_location
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def freshwater_eutrophication_potential_location_rule(instance, location, *scale_list):
        eutf_process = sum(
            instance.freshwater_eutrophication_potential_process[location, process_, scale_list] for process_ in instance.processes)
        eutf_resource = sum(
            instance.freshwater_eutrophication_potential_resource[location, resource_, scale_list] for resource_ in instance.resources)
        eutf_material = sum(
            instance.freshwater_eutrophication_potential_material[location, material_, scale_list] for material_ in instance.processes_materials)

        return instance.freshwater_eutrophication_potential_location[location, scale_list] == eutf_process + eutf_resource + eutf_material
    instance.constraint_freshwater_eutrophication_potential_location = Constraint(
        instance.locations, *scales, rule=freshwater_eutrophication_potential_location_rule, doc='freshwater eutrophication potential for the each location')
    constraint_latex_render(freshwater_eutrophication_potential_location_rule)
    return instance.constraint_freshwater_eutrophication_potential_location


def constraint_freshwater_eutrophication_potential_network(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """freshwater eutrophication potential for the whole network

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: freshwater_eutrophication_potential_network
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def freshwater_eutrophication_potential_network_rule(instance, *scale_list):
        return instance.freshwater_eutrophication_potential_network[scale_list] == \
            sum(instance.freshwater_eutrophication_potential_location[location_,
                scale_list] for location_ in instance.locations)
    instance.constraint_freshwater_eutrophication_potential_network = Constraint(
        *scales, rule=freshwater_eutrophication_potential_network_rule, doc='freshwater eutrophication potential for the whole network')
    constraint_latex_render(freshwater_eutrophication_potential_network_rule)
    return instance.constraint_freshwater_eutrophication_potential_network

# *-------------------Marine Eutrophication Potential-------------------------------------------------------------


def constraint_marine_eutrophication_potential_process(instance: ConcreteModel, process_eutm_dict: dict, network_scale_level: int = 0) -> Constraint:
    """calculates marine eutrophication potential for each process

    Args:
        instance (ConcreteModel): pyomo model instance
        process_eutm_dict (dict): _description_
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: marine_eutrophication_potential_process
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def marine_eutrophication_potential_process_rule(instance, location, process,  *scale_list):
        return instance.marine_eutrophication_potential_process[location, process, scale_list] == process_eutm_dict[location][process]*instance.Cap_P[location, process, scale_list]
    instance.constraint_marine_eutrophication_potential_process = Constraint(
        instance.locations, instance.processes, *scales, rule=marine_eutrophication_potential_process_rule, doc='marine eutrophication potential for the each process')
    constraint_latex_render(marine_eutrophication_potential_process_rule)
    return instance.constraint_marine_eutrophication_potential_process


def constraint_marine_eutrophication_potential_material_mode(instance: ConcreteModel, material_eutm_dict: dict, process_material_mode_material_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the marine eutrophication potential arising from the use of materials for processes in each material mode

    Args:
        instance (ConcreteModel): pyomo model instance
        material_eutm_dict (dict): eutm associated with each material
        process_material_mode_material_dict (dict): Material consumed by each process for each material mode
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: marine_eutrophication_potential_material_mode
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def marine_eutrophication_potential_material_mode_rule(instance, location, process, material_mode, *scale_list):
        if material_mode in process_material_mode_material_dict[process]:
            return instance.marine_eutrophication_potential_material_mode[location, process, material_mode, scale_list] == \
                sum(process_material_mode_material_dict[process][material_mode][material]*material_eutm_dict[location][material]
                    for material in instance.materials if material in process_material_mode_material_dict[process][material_mode]) * instance.Cap_P_M[location, process, material_mode, scale_list]
        else:
            return Constraint.Skip
    instance.constraint_marine_eutrophication_potential_material_mode = Constraint(
        instance.locations, instance.processes_materials, instance.material_modes, *scales, rule=marine_eutrophication_potential_material_mode_rule, doc='marine eutrophication potential for the each material')
    constraint_latex_render(marine_eutrophication_potential_material_mode_rule)
    return instance.constraint_marine_eutrophication_potential_material_mode


def constraint_marine_eutrophication_potential_material(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the marine eutrophication potential arising from the use of materials for processes across all material modes

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: marine_eutrophication_potential_material
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def marine_eutrophication_potential_material_rule(instance, location, process,  *scale_list):
        return instance.marine_eutrophication_potential_material[location, process, scale_list] == sum(instance.marine_eutrophication_potential_material_mode[location, process, material_mode_, scale_list] for material_mode_ in instance.material_modes)
    instance.constraint_marine_eutrophication_potential_material = Constraint(
        instance.locations, instance.processes_materials, *scales, rule=marine_eutrophication_potential_material_rule, doc='marine eutrophication potential for the each material')
    constraint_latex_render(marine_eutrophication_potential_material_rule)
    return instance.constraint_marine_eutrophication_potential_material


def constraint_marine_eutrophication_potential_resource_consumption(instance: ConcreteModel, resource_eutm_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the marine eutrophication potential from each resource consumed

    Args:
        instance (ConcreteModel): pyomo model instance
        resource_eutm_dict (dict): eutm associated with each resource
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: marine_eutrophication_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def marine_eutrophication_potential_resource_consumption_rule(instance, location, resource,  *scale_list):
        return instance.marine_eutrophication_potential_resource_consumption[location, resource, scale_list] == resource_eutm_dict[location][resource]*instance.C_location[location, resource, scale_list]
    instance.constraint_marine_eutrophication_potential_resource_consumption = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=marine_eutrophication_potential_resource_consumption_rule, doc='marine eutrophication potential for the each resource consumed')
    constraint_latex_render(
        marine_eutrophication_potential_resource_consumption_rule)
    return instance.constraint_marine_eutrophication_potential_resource_consumption


def constraint_marine_eutrophication_potential_resource_discharge(instance: ConcreteModel, resource_eutm_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the marine eutrophication potential from each resource

    Args:
        instance (ConcreteModel): pyomo model instance
        resource_eutm_dict (dict): eutm associated with each resource
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: marine_eutrophication_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def marine_eutrophication_potential_resource_discharge_rule(instance, location, resource,  *scale_list):
        return instance.marine_eutrophication_potential_resource_discharge[location, resource, scale_list] == resource_eutm_dict[location][resource]*instance.S_location[location, resource, scale_list]
    instance.constraint_marine_eutrophication_potential_resource_discharge = Constraint(
        instance.locations, instance.resources_sell, *scales, rule=marine_eutrophication_potential_resource_discharge_rule, doc='marine eutrophication potential for the each resource discharged')
    constraint_latex_render(
        marine_eutrophication_potential_resource_discharge_rule)
    return instance.constraint_marine_eutrophication_potential_resource_discharge


def constraint_marine_eutrophication_potential_resource(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the marine eutrophication potential from each resource

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: marine_eutrophication_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def marine_eutrophication_potential_resource_rule(instance, location, resource,  *scale_list):
        # if (resource in instance.resources_sell) or (resource in instance.resources_purch):
        if resource in instance.resources_sell:
            sales = instance.marine_eutrophication_potential_resource_discharge[
                location, resource, scale_list]
        else:
            sales = 0

        if resource in instance.resources_purch:
            purch = instance.marine_eutrophication_potential_resource_consumption[
                location, resource, scale_list]

        else:
            purch = 0
        return instance.marine_eutrophication_potential_resource[location, resource, scale_list] == sales + purch

        # else:
        #     return Constraint.Skip
    instance.constraint_marine_eutrophication_potential_resource = Constraint(
        instance.locations, instance.resources, *scales, rule=marine_eutrophication_potential_resource_rule, doc='marine eutrophication potential for the each resource')
    constraint_latex_render(marine_eutrophication_potential_resource_rule)
    return instance.constraint_marine_eutrophication_potential_resource


def constraint_marine_eutrophication_potential_location(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the marine eutrophication potential at each location

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: marine_eutrophication_potential_location
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def marine_eutrophication_potential_location_rule(instance, location, *scale_list):
        eutm_process = sum(
            instance.marine_eutrophication_potential_process[location, process_, scale_list] for process_ in instance.processes)
        eutm_resource = sum(
            instance.marine_eutrophication_potential_resource[location, resource_, scale_list] for resource_ in instance.resources)
        eutm_material = sum(
            instance.marine_eutrophication_potential_material[location, material_, scale_list] for material_ in instance.processes_materials)

        return instance.marine_eutrophication_potential_location[location, scale_list] == eutm_process + eutm_resource + eutm_material
    instance.constraint_marine_eutrophication_potential_location = Constraint(
        instance.locations, *scales, rule=marine_eutrophication_potential_location_rule, doc='marine eutrophication potential for the each location')
    constraint_latex_render(marine_eutrophication_potential_location_rule)
    return instance.constraint_marine_eutrophication_potential_location


def constraint_marine_eutrophication_potential_network(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """marine eutrophication potential for the whole network

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: marine_eutrophication_potential_network
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def marine_eutrophication_potential_network_rule(instance, *scale_list):
        return instance.marine_eutrophication_potential_network[scale_list] == \
            sum(instance.marine_eutrophication_potential_location[location_,
                scale_list] for location_ in instance.locations)
    instance.constraint_marine_eutrophication_potential_network = Constraint(
        *scales, rule=marine_eutrophication_potential_network_rule, doc='marine eutrophication potential for the whole network')
    constraint_latex_render(marine_eutrophication_potential_network_rule)
    return instance.constraint_marine_eutrophication_potential_network
