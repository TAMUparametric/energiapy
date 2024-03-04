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


def objective_cost(instance: ConcreteModel, constraints: Set[Constraints], network_scale_level: int = 0) -> Objective:
    """Objective to minimize total cost

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

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
            cost_trans_capex = sum(
                instance.Capex_transport_network[scale_] for scale_ in scale_iter)
            cost_trans_vopex = sum(
                instance.Vopex_transport_network[scale_] for scale_ in scale_iter)
            cost_trans_fopex = sum(
                instance.Fopex_transport_network[scale_] for scale_ in scale_iter)
        else:
            cost_trans_capex = 0
            cost_trans_vopex = 0
            cost_trans_fopex = 0

        return capex + cost_trans_capex + vopex + fopex + cost_purch + cost_trans_vopex + cost_trans_fopex + incidental + land_cost - credit + storage_cost

    instance.objective_cost = Objective(
        rule=objective_cost_rule, doc='total cost')
    constraint_latex_render(objective_cost_rule)
    return instance.objective_cost


def objective_cost_w_demand_penalty(instance: ConcreteModel, demand_penalty: Dict[Location, Dict[Resource, float]], constraints: Set[Constraints],
                                    network_scale_level: int = 0, demand_scale_level: int = 0) -> Objective:
    """Objective to minimize total cost with demand penalty

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        demand_penalty (Dict[Location, Resource]): penalty for unmet demand for resource at each location

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
            cost_trans_capex = sum(
                instance.Capex_transport_network[scale_] for scale_ in scale_iter)
            cost_trans_vopex = sum(
                instance.Vopex_transport_network[scale_] for scale_ in scale_iter)
            cost_trans_fopex = sum(
                instance.Fopex_transport_network[scale_] for scale_ in scale_iter)
        else:
            cost_trans_capex = 0
            cost_trans_vopex = 0
            cost_trans_fopex = 0

        penalty = sum(demand_penalty[location_][resource_]*instance.Demand_penalty[location_, resource_, scale_] for location_, resource_, scale_ in product(
            instance.locations, instance.resources_demand, scale_iter_penalty))
        return capex + cost_trans_capex + vopex + fopex + cost_purch + cost_trans_vopex + cost_trans_fopex + incidental + land_cost - credit + penalty
    instance.objective_cost_w_demand_penalty = Objective(
        rule=objective_cost_w_demand_penalty_rule, doc='total cost with penalty for demand')
    constraint_latex_render(objective_cost_w_demand_penalty_rule)
    return instance.objective_cost_w_demand_penalty


def objective_uncertainty_cost(instance: ConcreteModel, penalty: float, network_scale_level: int = 0,
                               uncertainty_scale_level: int = 0) -> Objective:
    """Objective to minimize total cost

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

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
            cost_trans_capex = sum(
                instance.Capex_transport_network[scale_] for scale_ in scale_iter)
            cost_trans_vopex = sum(
                instance.Vopex_transport_network[scale_] for scale_ in scale_iter)
            cost_trans_fopex = sum(
                instance.Fopex_transport_network[scale_] for scale_ in scale_iter)
        else:
            cost_trans_capex = 0
            cost_trans_vopex = 0
            cost_trans_fopex = 0
        return capex + cost_trans_capex + vopex + fopex + cost_purch + cost_trans_vopex + cost_trans_fopex + cap_penalty

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

    instance.objective_discharge_min = Objective(
        rule=objective_discharge_min_rule, doc='minimize total discharge from specific_network')
    constraint_latex_render(objective_discharge_min_rule)
    return instance.objective_discharge_min


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

    instance.objective_discharge_max = Objective(
        rule=objective_discharge_max_rule, sense=maximize, doc='maximize total discharge from specific_network')
    constraint_latex_render(objective_discharge_max_rule)
    return instance.objective_discharge_max


def objective_profit(instance: ConcreteModel, constraints: Set[Constraints], network_scale_level: int = 0) -> Objective:
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
            cost_trans_capex = sum(
                instance.Capex_transport_network[scale_] for scale_ in scale_iter)
            cost_trans_vopex = sum(
                instance.Vopex_transport_network[scale_] for scale_ in scale_iter)
            cost_trans_fopex = sum(
                instance.Fopex_transport_network[scale_] for scale_ in scale_iter)
        else:
            cost_trans_capex = 0
            cost_trans_vopex = 0
            cost_trans_fopex = 0
        return -(capex + cost_trans_capex + vopex + fopex + cost_purch + cost_trans_vopex + cost_trans_fopex + incidental + land_cost) + credit + revenue

    instance.objective_profit = Objective(
        rule=objective_profit_rule, sense=maximize, doc='total profit')
    constraint_latex_render(objective_profit_rule)
    return instance.objective_profit


def objective_profit_w_demand_penalty(instance: ConcreteModel, demand_penalty: Dict[Location, Dict[Resource, float]], constraints: Set[Constraints],
                                      network_scale_level: int = 0, demand_scale_level: int = 0) -> Objective:
    """Objective to maximize total profit with a penalty for unmet demand

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

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
            cost_trans_capex = sum(
                instance.Capex_transport_network[scale_] for scale_ in scale_iter)
            cost_trans_vopex = sum(
                instance.Vopex_transport_network[scale_] for scale_ in scale_iter)
            cost_trans_fopex = sum(
                instance.Fopex_transport_network[scale_] for scale_ in scale_iter)
        else:
            cost_trans_capex = 0
            cost_trans_vopex = 0
            cost_trans_fopex = 0

        penalty = sum(demand_penalty[location_][resource_]*instance.Demand_penalty[location_, resource_, scale_] for location_, resource_, scale_ in product(
            instance.locations, instance.resources_demand, scale_iter_penalty))
        return -(capex + cost_trans_capex + vopex + fopex + cost_purch + cost_trans_vopex + cost_trans_fopex + incidental + land_cost + penalty) + credit + revenue

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

    instance.objective_emission_min = Objective(
        rule=objective_emission_min_rule, doc='minimize total emission for network')
    constraint_latex_render(objective_emission_min_rule)
    return instance.objective_emission_min
