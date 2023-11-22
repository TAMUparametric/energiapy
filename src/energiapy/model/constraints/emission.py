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


def constraint_global_warming_potential_resource(instance: ConcreteModel, resource_gwp_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates the global warming potential from each resource

    Args:
        instance (ConcreteModel): pyomo model instance
        resource_gwp_dict (dict): GWP associated with each resource
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: global_warming_potential_resource
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def global_warming_potential_resource_rule(instance, location, resource,  *scale_list):
        return instance.global_warming_potential_resource[location, resource, scale_list] == resource_gwp_dict[location][resource]*instance.C_location[location, resource, scale_list]
    instance.constraint_global_warming_potential_resource = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=global_warming_potential_resource_rule, doc='global warming potential for the each resource')
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
            instance.global_warming_potential_resource[location, resource_, scale_list] for resource_ in instance.resources_purch)
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
