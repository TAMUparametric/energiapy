"""pyomo uncertain constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from typing import Union

from pyomo.environ import ConcreteModel, Constraint

from ...utils.scale_utils import scale_tuple


def constraint_uncertain_resource_demand(instance: ConcreteModel, demand: Union[dict, float], scheduling_scale_level: int = 0) -> Constraint:
    """Discharge meets an uncertain demand

    Args:
        instance (ConcreteModel): model instance
        demand (float): demand to be met
        scheduling_scale_level (int, optional): scheduling scales of the problem. Defaults to 0.

    Returns:
        Constraint: instance.uncertain_resource_demand
    """

    scales = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level+1)

    def uncertain_resource_demand_rule(instance, location, resource, *scale_list):
        if isinstance(demand, dict):
            return instance.S[location, resource, scale_list[:scheduling_scale_level+1]] >= demand[location][resource]*instance.resource_demand_uncertainty[location, resource, scale_list[:scheduling_scale_level+1]]
        else:
            return instance.S[location, resource, scale_list[:scheduling_scale_level+1]] >= demand*instance.resource_demand_uncertainty[location, resource, scale_list[:scheduling_scale_level+1]]

    instance.constraint_uncertain_resource_demand = Constraint(instance.locations, instance.resources_uncertain_demand, *scales, rule=uncertain_resource_demand_rule,
                                                               doc='meet uncertain demand')
    return instance.constraint_uncertain_resource_demand


def constraint_uncertain_process_capacity(instance: ConcreteModel, capacity: dict, network_scale_level: int = 0) -> Constraint:
    """provides uncertainty to process capacity

    Args:
        instance (ConcreteModel): model instance 
        capacity (dict, optional): base capacity of the process. Defaults to float.
        network_scale_level (int, optional): network scales of the problem. Defaults to 0.

    Returns:
        Constraint: uncertain_process_capacity
    """
    scales = scale_tuple(instance=instance, scale_levels=network_scale_level+1)

    def uncertain_process_capacity_rule(instance, location, process, *scale_list):
        return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] == capacity[location][process]*instance.process_capacity_uncertainty[location, process, scale_list[:network_scale_level+1]]

    instance.constraint_uncertain_process_capacity = Constraint(instance.locations, instance.processes_uncertain_capacity, *scales, rule=uncertain_process_capacity_rule,
                                                                doc='uncertain capacity for process')
    return instance.constraint_uncertain_process_capacity
