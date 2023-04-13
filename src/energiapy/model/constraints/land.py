"""pyomo land constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Constraint

from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list


def constraint_land_process(instance: ConcreteModel, land_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Land required for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        land_dict (dict): land required at location
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: land_process
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)

    def land_process_rule(instance, location, process, *scale_list):
        return instance.Land_process[location, process, scale_list] == land_dict[process] * instance.Cap_P[
            location, process, scale_list]

    instance.constraint_land_process = Constraint(
        instance.locations, instance.processes, *scales, rule=land_process_rule, doc='land required for process')
    constraint_latex_render(land_process_rule)
    return instance.constraint_land_process


def constraint_land_location(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Land required at each location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: land_location
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)

    def land_location_rule(instance, location, *scale_list):
        return instance.Land_location[location, scale_list] == sum(
            instance.Land_process[location, process_, scale_list] for process_ in instance.processes)

    instance.constraint_land_location = Constraint(
        instance.locations, *scales, rule=land_location_rule, doc='land required for process')
    constraint_latex_render(land_location_rule)
    return instance.constraint_land_location


def constraint_land_network(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Land required by network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: land_network
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)

    def land_network_rule(instance, *scale_list):
        return instance.Land_network[scale_list] == sum(
            instance.Land_location[location_, scale_list] for location_ in instance.locations)

    instance.constraint_land_network = Constraint(
        *scales, rule=land_network_rule, doc='land required for process')
    constraint_latex_render(land_network_rule)
    return instance.constraint_land_network


def constraint_land_location_restriction(instance: ConcreteModel, network_scale_level: int = 0,
                                         land_restriction: float = 0) -> Constraint:
    """Land required at each location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: land_location
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)

    def land_location_restriction_rule(instance, location, *scale_list):
        return instance.Land_location[location, scale_list] <= land_restriction

    instance.constraint_land_location_restriction = Constraint(
        instance.locations, *scales, rule=land_location_restriction_rule, doc='land required for process')
    constraint_latex_render(land_location_restriction_rule)
    return instance.constraint_land_location_restriction
