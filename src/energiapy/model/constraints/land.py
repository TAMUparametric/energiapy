"""pyomo land constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Constraint
from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list
from ...utils.scale_utils import scale_pyomo_set
from ...utils.scale_utils import scale_tuple
from ...components.location import Location
from itertools import product
from typing import Union
from enum import Enum, auto

def constraint_process_land(instance: ConcreteModel, land_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Land required for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        land_dict (dict): land required at location
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: process_land
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def process_land_rule(instance, location, process, *scale_list):
        return instance.Land_process[location, process, scale_list] == land_dict[process]*instance.Cap_P[location, process, scale_list]
    instance.constraint_process_land = Constraint(
        instance.locations, instance.processes, *scales, rule=process_land_rule, doc='land required for process')
    constraint_latex_render(process_land_rule)
    return instance.constraint_process_land



def constraint_location_land(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Land required at each location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_land
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def location_land_rule(instance, location, *scale_list):
        return instance.Land_location[location, scale_list] == sum(instance.Land_process[location, process_, scale_list] for process_ in instance.processes)
    instance.constraint_location_land = Constraint(
        instance.locations, *scales, rule=location_land_rule, doc='land required for process')
    constraint_latex_render(location_land_rule)
    return instance.constraint_location_land



def constraint_network_land(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Land required by network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_land
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_land_rule(instance, *scale_list):
        return instance.Land_network[scale_list] == sum(instance.Land_location[location_, scale_list] for location_ in instance.locations)
    instance.constraint_network_land = Constraint(
        *scales, rule=network_land_rule, doc='land required for process')
    constraint_latex_render(network_land_rule)
    return instance.constraint_network_land

def constraint_location_land_restriction(instance: ConcreteModel, network_scale_level: int = 0, land_restriction: float = 0) -> Constraint:
    """Land required at each location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
 
    Returns:
        Constraint: location_land
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def location_land_restriction_rule(instance, location, *scale_list):
        return instance.Land_location[location, scale_list] <= land_restriction
    instance.constraint_location_land_restriction = Constraint(
        instance.locations, *scales, rule=location_land_restriction_rule, doc='land required for process')
    constraint_latex_render(location_land_restriction_rule)
    return instance.constraint_location_land_restriction