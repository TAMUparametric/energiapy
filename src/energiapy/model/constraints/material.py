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
            return instance.material_process[location, process, material, scale_list] == process_material_dict[process][material]*instance.Cap_P[location, process, scale_list]
        else:
            return Constraint.Skip
    instance.constraint_material_process = Constraint(
        instance.locations, instance.processes, instance.materials, *scales, rule=material_process_rule, doc='material utilization for each process')
    constraint_latex_render(material_process_rule)
    return instance.constraint_material_process


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
