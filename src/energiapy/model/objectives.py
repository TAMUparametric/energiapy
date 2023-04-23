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
from typing import Set

from pyomo.environ import ConcreteModel, Objective, maximize

from ..utils.latex_utils import constraint_latex_render
from ..utils.scale_utils import scale_tuple
from ..components.resource import Resource
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
            cost_trans = sum(instance.Trans_cost_network[transport_, scale_] for transport_, scale_ in
                             product(instance.transports, scale_iter))
        else:
            cost_trans = 0
        return capex + vopex + fopex + cost_purch + cost_trans + incidental + land_cost + credit

    instance.objective_cost = Objective(
        rule=objective_cost_rule, doc='total cost')
    constraint_latex_render(objective_cost_rule)
    return instance.objective_cost


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
            cost_trans = sum(instance.Trans_cost_network[transport_, scale_] for transport_, scale_ in
                             product(instance.transports, scale_iter))
        else:
            cost_trans = 0
        return capex + vopex + fopex + cost_purch + cost_trans + cap_penalty

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



def objective_revenue(instance: ConcreteModel, constraints: Set[Constraints], network_scale_level: int = 0) -> Objective:
    """Objective to minimize total revenue

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Objective: revenue objective
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)

    def objective_revenue_rule(instance):
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
            cost_trans = sum(instance.Trans_cost_network[transport_, scale_] for transport_, scale_ in
                             product(instance.transports, scale_iter))
        else:
            cost_trans = 0
        return capex + vopex + fopex + cost_purch + cost_trans + incidental + land_cost + credit

    instance.objective_revenue = Objective(
        rule=objective_revenue_rule, doc='total revenue')
    constraint_latex_render(objective_revenue_rule)
    return instance.objective_revenue
