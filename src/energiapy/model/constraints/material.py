"""material constraints
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


def constraint_material_mode_process(instance: ConcreteModel, process_material_mode_material_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates material utilization for each process under material mode

    Args:
        instance (ConcreteModel): pyomo model instance
        process_material_mode_material_dict (dict): materials consumed by each process under material_mode
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: material_mode_process
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def material_mode_process_rule(instance, location, process, material_mode, material, *scale_list):
        if material_mode in process_material_mode_material_dict[process].keys():
            if material in process_material_mode_material_dict[process][material_mode].keys():
                return instance.material_mode_process[location, process, material_mode, material, scale_list] == process_material_mode_material_dict[process][material_mode][material]*instance.Cap_P_M[location, process, material_mode, scale_list]
            else:
                return instance.material_mode_process[location, process, material_mode, material, scale_list] == 0
        else:
            return instance.material_mode_process[location, process, material_mode, material, scale_list] == 0
    instance.constraint_material_mode_process = Constraint(
        instance.locations, instance.processes, instance.material_modes, instance.materials, *scales, rule=material_mode_process_rule, doc='material utilization for each process')
    constraint_latex_render(material_mode_process_rule)
    return instance.constraint_material_mode_process


def constraint_material_process(instance: ConcreteModel, process_material_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Calculates material utilization for each process

    Args:
        instance (ConcreteModel): pyomo model instance
        process_material_dict (dict): materials consumed by each process
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: material_process
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def material_process_rule(instance, location, process, material, *scale_list):
        if process_material_dict[process][material] is not None:
            return instance.material_process[location, process, material, scale_list] == sum(instance.material_mode_process[location, process, material_mode_, material, scale_list] for material_mode_ in instance.material_modes)
        else:
            return instance.material_process[location, process, material, scale_list] == 0
    instance.constraint_material_process = Constraint(
        instance.locations, instance.processes, instance.materials, *scales, rule=material_process_rule, doc='material utilization for each process')
    constraint_latex_render(material_process_rule)
    return instance.constraint_material_process


# def constraint_material_process(instance: ConcreteModel, process_material_dict: dict, network_scale_level: int = 0) -> Constraint:
#     """Calculates material utilization for each process

#     Args:
#         instance (ConcreteModel): pyomo model instance
#         process_material_dict (dict): materials consumed by each process
#         network_scale_level (int, optional): scale for network decisions. Defaults to 0.

#     Returns:
#         Constraint: material_process
#     """
#     scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

#     def material_process_rule(instance, location, process, material, *scale_list):
#         if process_material_dict[process][material] is not None:
#             return instance.material_process[location, process, material, scale_list] == process_material_dict[process][material]*instance.Cap_P[location, process, scale_list]
#         else:
#             return Constraint.Skip
#     instance.constraint_material_process = Constraint(
#         instance.locations, instance.processes, instance.materials, *scales, rule=material_process_rule, doc='material utilization for each process')
#     constraint_latex_render(material_process_rule)
#     return instance.constraint_material_process


def constraint_material_location(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Calculates the material utilization at each location

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: material_location
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def material_location_rule(instance, location, material, *scale_list):
        return instance.material_location[location, material, scale_list] == sum(instance.material_process[location, process_, material, scale_list] for process_ in instance.processes)
    instance.constraint_material_location = Constraint(
        instance.locations, instance.materials, *scales, rule=material_location_rule, doc='material utilization for each location')
    constraint_latex_render(material_location_rule)
    return instance.constraint_material_location


def constraint_material_network(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Material utilization for the whole network

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: material_network
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def material_network_rule(instance, material, *scale_list):
        return instance.material_network[material, scale_list] == sum(instance.material_location[location_, material, scale_list] for location_ in instance.locations)
    instance.constraint_material_network = Constraint(
        instance.materials, *scales, rule=material_network_rule, doc='material utilization for the whole network')
    constraint_latex_render(material_network_rule)
    return instance.constraint_material_network


def constraint_production_facility_material_mode(instance: ConcreteModel, network_scale_level: int = 0, location_process_dict: dict = None) -> Constraint:
    """Capacity of process as a sum of the processes under different material modes

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        location_process_dict (dict, optional): dict with processes at location. Defaults to None.

    Returns:
        Constraint: constraint_production_facility_material_mode
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def production_facility_material_mode_rule(instance, location, process, *scale_list):
        if process in location_process_dict[location]:
            return instance.Cap_P[location, process, scale_list] == sum(instance.Cap_P_M[location, i[0], i[1], scale_list] for i in instance.process_material_modes if i[0] == process)
        else:
            return Constraint.Skip
    instance.constraint_production_facility_material_mode = Constraint(
        instance.locations, instance.processes, *scales, rule=production_facility_material_mode_rule, doc='capacity of process under different material modes')

    constraint_latex_render(production_facility_material_mode_rule)
    return instance.constraint_production_facility_material_mode


def constraint_production_facility_material_mode_binary(instance: ConcreteModel, network_scale_level: int = 0, location_process_dict: dict = None) -> Constraint:
    """Capacity of process as a sum of the processes under different material modes

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        location_process_dict (dict, optional): dict with processes at location. Defaults to None.

    Returns:
        Constraint: constraint_production_facility_material_mode_binary
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def production_facility_material_mode_binary_rule(instance, location, process, *scale_list):
        if process in location_process_dict[location]:
            return sum(instance.X_M[location, i[0], i[1], scale_list] for i in instance.process_material_modes if i[0] == process) == instance.X_P[location, process, scale_list]
        else:
            return Constraint.Skip
    instance.constraint_production_facility_material_mode_binary = Constraint(
        instance.locations, instance.processes, *scales, rule=production_facility_material_mode_binary_rule, doc='capacity of process under different material modes')

    constraint_latex_render(production_facility_material_mode_binary_rule)
    return instance.constraint_production_facility_material_mode_binary


def constraint_production_facility_material(instance: ConcreteModel, prod_max: dict, location_process_dict: dict = None,
                                            network_scale_level: int = 0, process_material_modes_dict: dict = None) -> Constraint:
    """Determines where production facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        prod_max (dict): maximum production of process at location
        location_process_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        process_material_modes_dict (dict, optional): material modes available for processes

    Returns:
        Constraint: production_facility_material
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def production_facility_material_rule(instance, location, process, material_mode, *scale_list):
        if location_process_dict is not None:
            if process in location_process_dict[location]:
                if material_mode in process_material_modes_dict[process]:
                    return instance.Cap_P_M[location, process, material_mode, scale_list[:network_scale_level + 1]] <= prod_max[location][process][list(prod_max[location][process].keys())[-1:][0]]*instance.X_M[location, process, material_mode, scale_list[:network_scale_level + 1]]
                else:
                    return Constraint.Skip
            else:
                return instance.Cap_P_M[location, material_mode, process, scale_list[:network_scale_level + 1]] == 0
        else:
            return Constraint.Skip

    instance.constraint_production_facility_material = Constraint(
        instance.locations, instance.processes,  instance.material_modes, *
        scales, rule=production_facility_material_rule,
        doc='production facility sizing and location for material mode')
    constraint_latex_render(production_facility_material_rule)
    return instance.constraint_production_facility_material


def constraint_min_production_facility_material(instance: ConcreteModel, prod_min: dict, location_process_dict: dict = None,
                                                network_scale_level: int = 0, process_material_modes_dict: dict = None) -> Constraint:
    """Determines where production facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        prod_min (dict): minimum production of process at location
        location_process_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        process_material_modes_dict (dict, optional): material modes available for processes

    Returns:
        Constraint: min_production_facility_material
    """

    if location_process_dict is None:
        location_process_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def min_production_facility_material_rule(instance, location, process, material_mode, *scale_list):
        if location_process_dict is not None:
            if process in location_process_dict[location]:
                if material_mode in process_material_modes_dict[process]:
                    return instance.Cap_P_M[location, process, material_mode, scale_list[:network_scale_level + 1]] >= prod_min[location][process][list(prod_min[location][process].keys())[:1][0]] * instance.X_M[location, process, material_mode, scale_list[:network_scale_level + 1]]
                else:
                    return Constraint.Skip
            else:
                return instance.Cap_P_M[location, process, material_mode, scale_list[:network_scale_level + 1]] == 0
        else:
            return Constraint.Skip

    instance.constraint_min_production_facility_material = Constraint(
        instance.locations, instance.processes, instance.material_modes, *
        scales, rule=min_production_facility_material_rule,
        doc='production facility sizing and location for material mode')
    constraint_latex_render(min_production_facility_material_rule)
    return instance.constraint_min_production_facility_material