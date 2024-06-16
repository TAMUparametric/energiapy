"""pyomo objective
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from itertools import product
from typing import Set, Dict

from pyomo.environ import ConcreteModel, Objective, maximize
from ..utils.scale_utils import scale_tuple
from ..components.resource import Resource
from ..components.location import Location
from ..model.constraints.constraints import Constraints


# *------------------------------------------Economic Objectives----------------------------------------------------

def objective_cost(instance: ConcreteModel) -> Objective:
    """Objective to minimize total cost

    Args:
        instance (ConcreteModel): pyomo instance

    Returns:
        Objective: cost objective
    """
    def objective_cost_rule(instance):

        return instance.Cost_total

    return Objective(rule=objective_cost_rule, doc='total cost')


def objective_cost_w_demand_penalty(instance: ConcreteModel, demand_penalty: Dict[Location, Dict[Resource, float]], demand_scale_level: int = 0) -> Objective:
    """Objective to minimize total cost with demand penalty

    Args:
        instance (ConcreteModel): pyomo instance
        demand_scale_level (int, optional): scale of meeting demand. Defaults to 0.
        demand_penalty (Dict[Location, Resource]): penalty for unmet demand for resource at each location

    Returns:
        Objective: cost w demand penalty objective
    """
    scale_iter_penalty = scale_tuple(
        instance=instance, scale_levels=demand_scale_level + 1)

    def objective_cost_w_demand_penalty_rule(instance):
        penalty = sum(demand_penalty[location_][resource_]*instance.Demand_penalty[location_, resource_, scale_] for location_, resource_, scale_ in product(
            instance.locations, instance.resources_demand, scale_iter_penalty))
        return instance.Cost_total + penalty
    return Objective(rule=objective_cost_w_demand_penalty_rule, doc='total cost with penalty for demand')


def objective_profit(instance: ConcreteModel, network_scale_level: int = 0) -> Objective:
    """Objective to maximize total profit

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Objective: profit objective
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)

    def objective_profit_rule(instance):
        return -instance.Cost_total + instance.R_total

    return Objective(rule=objective_profit_rule, sense=maximize, doc='total profit')


def objective_profit_w_demand_penalty(instance: ConcreteModel, demand_penalty: Dict[Location, Dict[Resource, float]],
                                      network_scale_level: int = 0, demand_scale_level: int = 0) -> Objective:
    """Objective to maximize total profit with a penalty for unmet demand

    Args:
        instance (ConcreteModel): pyomo instance
        demand_penalty (Dict[Location, Resource]): penalty for unmet demand for resource at each location
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        demand_scale_level (int, optional): scale of meeting demand. Defaults to 0.
    Returns:
        Objective: profit w demand penalty objective
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)
    scale_iter_penalty = scale_tuple(
        instance=instance, scale_levels=demand_scale_level + 1)

    def objective_profit_w_demand_penalty_rule(instance):
        penalty = sum(demand_penalty[location_][resource_]*instance.Demand_penalty[location_, resource_, scale_] for location_, resource_, scale_ in product(
            instance.locations, instance.resources_demand, scale_iter_penalty))
        return -instance.Cost_total - penalty + instance.R_total
    return Objective(rule=objective_profit_w_demand_penalty_rule, sense=maximize, doc='total profit w demand_penalty')

# *------------------------------------------Discharge Objectives----------------------------------------------------


def objective_discharge_min(instance: ConcreteModel, resource: Resource, network_scale_level: int = 0, ) -> Objective:
    """Minimize discharge of a particular resource

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Objective: objective_discharge_min
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)

    def objective_discharge_min_rule(instance, *scale_list):
        return sum(instance.S_network[resource.name, scale_] for scale_ in scale_iter)

    return Objective(rule=objective_discharge_min_rule, doc='minimize total discharge from specific_network')


def objective_discharge_max(instance: ConcreteModel, resource: Resource, network_scale_level: int = 0, ) -> Objective:
    """Maximize discharge of a particular resource

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Objective: objective_discharge_max
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)

    def objective_discharge_max_rule(instance, *scale_list):
        return sum(instance.S_network[resource.name, scale_] for scale_ in scale_iter)

    return Objective(rule=objective_discharge_max_rule, sense=maximize, doc='maximize total discharge from specific_network')


# *------------------------------------------Emission Objectives----------------------------------------------------

def objective_gwp_min(instance: ConcreteModel, network_scale_level: int = 0, ) -> Objective:
    """Minimize gwp at network level

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Objective: objective_gwp_min
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)

    def objective_gwp_min_rule(instance, *scale_list):
        return sum(instance.global_warming_potential_network[scale_] for scale_ in scale_iter)

    return Objective(rule=objective_gwp_min_rule, doc='minimize total gwp for network')


def objective_emission_min(instance: ConcreteModel, network_scale_level: int = 0, gwp_w: float = 0, odp_w: float = 0, acid_w: float = 0,
                           eutt_w: float = 0, eutf_w: float = 0, eutm_w: float = 0) -> Objective:
    """Minimize emission at network level using weighted sum method

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Objective: objective_emission_min
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)

    def objective_emission_min_rule(instance, *scale_list):
        return gwp_w*sum(instance.global_warming_potential_network[scale_] for scale_ in scale_iter) + odp_w*sum(instance.ozone_depletion_potential_network[scale_] for scale_ in scale_iter) + \
            acid_w*sum(instance.acidification_potential_network[scale_] for scale_ in scale_iter) + eutt_w*sum(instance.terrestrial_eutrophication_potential_network[scale_] for scale_ in scale_iter) + \
            eutf_w*sum(instance.freshwater_eutrophication_potential_network[scale_] for scale_ in scale_iter) + eutm_w*sum(
                instance.marine_eutrophication_potential_network[scale_] for scale_ in scale_iter)
    return Objective(rule=objective_emission_min_rule, doc='minimize total emission for network')
