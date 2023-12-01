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

from ..utils.latex_utils import constraint_latex_render
from ..utils.scale_utils import scale_tuple
from ..components.resource import Resource
from ..components.location import Location
from ..model.constraints.constraints import Constraints


def objective_cost(instance: ConcreteModel, constraints: Set[Constraints], network_scale_level: int = 0, annualization_factor: float = 1) -> Objective:
    """Objective to minimize total cost

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): fraction of capital expenditure incurred on an annual basis

    Returns:
        Objective: cost objective
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)

    def objective_cost_rule(instance):
        capex = sum(instance.Capex_network[scale_] for scale_ in scale_iter)
        vopex = sum(instance.Vopex_network[scale_] for scale_ in scale_iter)
        fopex = sum(instance.Fopex_network[scale_] for scale_ in scale_iter)
        incidental = sum(
            instance.Incidental_network[scale_] for scale_ in scale_iter)
        storage_cost = sum(
            instance.Inv_cost_network[scale_] for scale_ in scale_iter)
        cost_purch = sum(instance.B_network[resource_, scale_] for resource_, scale_ in
                         product(instance.resources_purch, scale_iter))

        if Constraints.LAND in constraints:
            land_cost = sum(
                instance.Land_cost_network[scale_] for scale_ in scale_iter)
        else:
            land_cost = 0

        if Constraints.CREDIT in constraints:
            credit = sum(
                instance.Credit_network[scale_] for scale_ in scale_iter)
        else:
            credit = 0

        if len(instance.locations) > 1:
            cost_trans = sum(
                instance.Capex_transport_network[scale_] for scale_ in scale_iter) + sum(
                instance.Vopex_transport_network[scale_] for scale_ in scale_iter) + sum(
                instance.Fopex_transport_network[scale_] for scale_ in scale_iter)
        else:
            cost_trans = 0
        return annualization_factor*capex + vopex + fopex + cost_purch + cost_trans + incidental + land_cost - credit + storage_cost

    instance.objective_cost = Objective(
        rule=objective_cost_rule, doc='total cost')
    constraint_latex_render(objective_cost_rule)
    return instance.objective_cost


def objective_cost_w_demand_penalty(instance: ConcreteModel, demand_penalty: Dict[Location, Dict[Resource, float]], constraints: Set[Constraints],
                                    network_scale_level: int = 0, demand_scale_level: int = 0, annualization_factor: float = 1) -> Objective:
    """Objective to minimize total cost with demand penalty

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        demand_penalty (Dict[Location, Resource]): penalty for unmet demand for resource at each location
        annualization_factor (float, optional): fraction of capital expenditure incurred on an annual basis


    Returns:
        Objective: cost objective
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)
    scale_iter_penalty = scale_tuple(
        instance=instance, scale_levels=demand_scale_level + 1)

    def objective_cost_w_demand_penalty_rule(instance):
        capex = sum(instance.Capex_network[scale_] for scale_ in scale_iter)
        vopex = sum(instance.Vopex_network[scale_] for scale_ in scale_iter)
        fopex = sum(instance.Fopex_network[scale_] for scale_ in scale_iter)
        incidental = sum(
            instance.Incidental_network[scale_] for scale_ in scale_iter)

        cost_purch = sum(instance.B_network[resource_, scale_] for resource_, scale_ in
                         product(instance.resources_purch, scale_iter))

        if Constraints.LAND in constraints:
            land_cost = sum(
                instance.Land_cost_network[scale_] for scale_ in scale_iter)
        else:
            land_cost = 0

        if Constraints.CREDIT in constraints:
            credit = sum(
                instance.Credit_network[scale_] for scale_ in scale_iter)
        else:
            credit = 0

        if len(instance.locations) > 1:
            cost_trans = sum(
                instance.Capex_transport_network[scale_] for scale_ in scale_iter) + sum(
                instance.Vopex_transport_network[scale_] for scale_ in scale_iter) + sum(
                instance.Fopex_transport_network[scale_] for scale_ in scale_iter)
        else:
            cost_trans = 0

        penalty = sum(demand_penalty[location_][resource_]*instance.Demand_penalty[location_, resource_, scale_] for location_, resource_, scale_ in product(
            instance.locations, instance.resources_demand, scale_iter_penalty))
        return annualization_factor*capex + vopex + fopex + cost_purch + cost_trans + incidental + land_cost - credit + penalty
    instance.objective_cost_w_demand_penalty = Objective(
        rule=objective_cost_w_demand_penalty_rule, doc='total cost with penalty for demand')
    constraint_latex_render(objective_cost_w_demand_penalty_rule)
    return instance.objective_cost_w_demand_penalty


def objective_uncertainty_cost(instance: ConcreteModel, penalty: float, network_scale_level: int = 0,
                               uncertainty_scale_level: int = 0, annualization_factor: float = 1) -> Objective:
    """Objective to minimize total cost

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): fraction of capital expenditure incurred on an annual basis


    Returns:
        Objective: cost objective
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)
    scale_iter_uncertainty = scale_tuple(
        instance=instance, scale_levels=uncertainty_scale_level + 1)

    def uncertainty_cost_objective_rule(instance):
        capex = sum(instance.Capex_network[scale_] for scale_ in scale_iter)
        vopex = sum(instance.Vopex_network[scale_] for scale_ in scale_iter)
        fopex = sum(instance.Fopex_network[scale_] for scale_ in scale_iter)
        cost_purch = sum(instance.B_network[resource_, scale_] for resource_, scale_ in
                         product(instance.resources_purch, scale_iter))
        cap_penalty = penalty * sum(instance.Demand_slack[location_, scale_] for location_, scale_ in
                                    product(instance.locations, scale_iter_uncertainty))
        if len(instance.locations) > 1:
            cost_trans = sum(
                instance.Capex_transport_network[scale_] for scale_ in scale_iter) + sum(
                instance.Vopex_transport_network[scale_] for scale_ in scale_iter) + sum(
                instance.Fopex_transport_network[scale_] for scale_ in scale_iter)
        else:
            cost_trans = 0
        return annualization_factor*capex + vopex + fopex + cost_purch + cost_trans + cap_penalty

    instance.uncertainty_cost_objective = Objective(rule=uncertainty_cost_objective_rule,
                                                    doc='total purchase from network')
    constraint_latex_render(uncertainty_cost_objective_rule)
    return instance.uncertainty_cost_objective


# def objective_discharge_max(instance: ConcreteModel, network_scale_level: int = 0) -> Objective:
#     """Objective to maximize total discharge

#     Args:
#         instance (ConcreteModel): pyomo instance
#         network_scale_level (int, optional): scale of network decisions. Defaults to 0.

#     Returns:
#         Objective: cost objective
#     """
#     scale_iter = scale_tuple(instance=instance, scale_levels=network_scale_level + 1)

#     def demand_objective_rule(instance):
#         return sum(instance.S_network[resource_, scale_] for resource_, scale_ in
#                    product(instance.resources_demand, scale_iter))

#     instance.demand_objective = Objective(rule=demand_objective_rule, doc='total purchase from network', sense=maximize)
#     # constraint_latex_render(cost_objective_rule)
#     return instance.demand_objective


def objective_discharge_min(instance: ConcreteModel, resource: Resource, network_scale_level: int = 0 ) -> Objective:
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

    instance.objective_discharge_min = Objective(
        rule=objective_discharge_min_rule, doc='minimize total discharge from specific_network')
    constraint_latex_render(objective_discharge_min_rule)
    return instance.objective_discharge_min


def objective_discharge_max(instance: ConcreteModel, resource: Resource, network_scale_level: int = 0 ) -> Objective:
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

    instance.objective_discharge_max = Objective(
        rule=objective_discharge_max_rule, sense=maximize, doc='maximize total discharge from specific_network')
    constraint_latex_render(objective_discharge_max_rule)
    return instance.objective_discharge_max

# def objective_max_service_level(instance: ConcreteModel, resource: Resource, scheduling_scale_level: int = 0) -> Objective:
#     """
#     Maximize the minimum guaranteed discharge of a particular resource over the scheduling scale
#
#     Args:
#         instance (ConcreteModel): pyomo instance
#         resource: Resource for which service level has to be maximized
#         scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0
#     """
#     scale_iter = scale_tuple(instance=instance, scale_levels=scheduling_scale_level+1)
#
#     def objective_max_service_level_rule(instance, *scale_list):
#         return min(instance.S[resource.name, scale_] for scale_ in scale_iter)
#
#     instance.objective_max_service_level = Objective(rule=objective_max_service_level_rule, sense=maximize,
#                                                          doc='maximize minimum guaranteed discharge over the scheduling scale')
#     constraint_latex_render(objective_max_service_level_rule)
#     return instance.objective_max_service_level


def objective_profit(instance: ConcreteModel, constraints: Set[Constraints], network_scale_level: int = 0, annualization_factor: float = 1) -> Objective:
    """Objective to maximize total profit

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): fraction of capital expenditure incurred on an annual basis


    Returns:
        Objective: profit objective
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)

    def objective_profit_rule(instance):
        capex = sum(instance.Capex_network[scale_] for scale_ in scale_iter)
        vopex = sum(instance.Vopex_network[scale_] for scale_ in scale_iter)
        fopex = sum(instance.Fopex_network[scale_] for scale_ in scale_iter)
        incidental = sum(
            instance.Incidental_network[scale_] for scale_ in scale_iter)

        cost_purch = sum(instance.B_network[resource_, scale_] for resource_, scale_ in
                         product(instance.resources_purch, scale_iter))

        revenue = sum(instance.R_network[resource_, scale_] for resource_, scale_ in
                      product(instance.resources_sell, scale_iter))

        if Constraints.LAND in constraints:
            land_cost = sum(
                instance.Land_cost_network[scale_] for scale_ in scale_iter)
        else:
            land_cost = 0

        if Constraints.CREDIT in constraints:
            credit = sum(
                instance.Credit_network[scale_] for scale_ in scale_iter)
        else:
            credit = 0

        if len(instance.locations) > 1:
            cost_trans = sum(
                instance.Capex_transport_network[scale_] for scale_ in scale_iter) + sum(
                instance.Vopex_transport_network[scale_] for scale_ in scale_iter) + sum(
                instance.Fopex_transport_network[scale_] for scale_ in scale_iter)
        else:
            cost_trans = 0
        return -(annualization_factor*capex + vopex + fopex + cost_purch + cost_trans + incidental + land_cost) + credit + revenue

    instance.objective_profit = Objective(
        rule=objective_profit_rule, sense=maximize, doc='total profit')
    constraint_latex_render(objective_profit_rule)
    return instance.objective_profit


def objective_profit_w_demand_penalty(instance: ConcreteModel, demand_penalty: Dict[Location, Dict[Resource, float]], constraints: Set[Constraints],
                                      network_scale_level: int = 0, demand_scale_level: int = 0, annualization_factor: float = 1) -> Objective:
    """Objective to maximize total profit with a penalty for unmet demand

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): fraction of capital expenditure incurred on an annual basis

    Returns:
        Objective: profit objective
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)
    scale_iter_penalty = scale_tuple(
        instance=instance, scale_levels=demand_scale_level + 1)

    def objective_profit_w_demand_penalty_rule(instance):
        capex = sum(instance.Capex_network[scale_] for scale_ in scale_iter)
        vopex = sum(instance.Vopex_network[scale_] for scale_ in scale_iter)
        fopex = sum(instance.Fopex_network[scale_] for scale_ in scale_iter)
        incidental = sum(
            instance.Incidental_network[scale_] for scale_ in scale_iter)

        cost_purch = sum(instance.B_network[resource_, scale_] for resource_, scale_ in
                         product(instance.resources_purch, scale_iter))

        revenue = sum(instance.R_network[resource_, scale_] for resource_, scale_ in
                      product(instance.resources_sell, scale_iter))

        if Constraints.LAND in constraints:
            land_cost = sum(
                instance.Land_cost_network[scale_] for scale_ in scale_iter)
        else:
            land_cost = 0

        if Constraints.CREDIT in constraints:
            credit = sum(
                instance.Credit_network[scale_] for scale_ in scale_iter)
        else:
            credit = 0

        if len(instance.locations) > 1:
            cost_trans = sum(
                instance.Capex_transport_network[scale_] for scale_ in scale_iter) + sum(
                instance.Vopex_transport_network[scale_] for scale_ in scale_iter) + sum(
                instance.Fopex_transport_network[scale_] for scale_ in scale_iter)
        else:
            cost_trans = 0

        penalty = sum(demand_penalty[location_][resource_]*instance.Demand_penalty[location_, resource_, scale_] for location_, resource_, scale_ in product(
            instance.locations, instance.resources_demand, scale_iter_penalty))
        return -(annualization_factor*capex + vopex + fopex + cost_purch + cost_trans + incidental + land_cost + penalty) + credit + revenue

    instance.objective_profit_w_demand_penalty = Objective(
        rule=objective_profit_w_demand_penalty_rule, sense=maximize, doc='total profit w demand_penalty')
    constraint_latex_render(objective_profit_w_demand_penalty_rule)
    return instance.objective_profit_w_demand_penalty


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

    instance.objective_gwp_min = Objective(
        rule=objective_gwp_min_rule, doc='minimize total gwp for network')
    constraint_latex_render(objective_gwp_min_rule)
    return instance.objective_gwp_min
