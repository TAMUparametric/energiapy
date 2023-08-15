"""resource demand constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.7"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from typing import Union, Dict, Tuple

from pyomo.environ import ConcreteModel, Constraint

from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list, scale_tuple
from ...components.resource import Resource
from ...components.location import Location
from ...components.process import Process


def constraint_demand(instance: ConcreteModel, demand: Union[dict, float], demand_factor: Union[dict, float],
                      demand_scale_level: int = 0, scheduling_scale_level: int = 0,
                      cluster_wt: dict = None, loc_res_dict: dict = None) -> Constraint:
    """Ensures that demand for resource is met at chosen temporal scale

    Args:
        instance (ConcreteModel): pyomo instance
        demand (Union[dict, float]): base demand
        demand_factor (Union[dict, float]): factor to adjust for demand variability
        demand_scale_level (int, optional): scale of demand decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        cluster_wt (dict, optional): weight of each cluster if using clustering. Defaults to None.
        loc_res_dict (dict, optional): location resource map. Defaults to None. 

    Returns:
        Constraint: demand
    """
    scales = scale_list(instance=instance, scale_levels=demand_scale_level+1)
    # scales = scale_list(instance=instance,
    #                     scale_levels=len(instance.scales))
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level + 1)

    if loc_res_dict is None:
        loc_res_dict = dict()

    def demand_rule(instance, location, resource, *scale_list):

        if demand_factor[location] is not None:
            if isinstance(demand_factor[location][list(demand_factor[location])[0]], (float, int)):
                discharge = sum(instance.S[location, resource_, scale_list[:scheduling_scale_level + 1]] for
                                resource_ in instance.resources_demand)
            else:
                discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[
                    :demand_scale_level + 1] == scale_list)

            if isinstance(demand, dict):
                if resource in loc_res_dict[location]:
                    if resource in demand_factor[location].keys():
                        demandtarget = demand[location][resource] * \
                            demand_factor[location][resource][scale_list[:demand_scale_level + 1]]
                    else:
                        demandtarget = demand[location][resource]
                else:
                    demandtarget = 0
            else:
                if resource in loc_res_dict[location]:
                    demandtarget = demand * \
                        demand_factor[location][resource][scale_list[:demand_scale_level + 1]]
                else:
                    demandtarget = 0
        else:
            # TODO - doesn't meet demand in first timeperiod
            discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[
                :demand_scale_level + 1] == scale_list)

            if isinstance(demand, dict):
                demandtarget = demand[location][resource]
            else:
                demandtarget = demand

        return discharge >= demandtarget

    if len(instance.locations) > 1:
        instance.constraint_demand = Constraint(
            instance.sinks, instance.resources_demand, *scales, rule=demand_rule, doc='specific demand for resources')

    else:
        instance.constraint_demand = Constraint(
            instance.locations, instance.resources_demand, *scales, rule=demand_rule,
            doc='specific demand for resources')
    constraint_latex_render(demand_rule)
    return instance.constraint_demand


def constraint_demand_penalty(instance: ConcreteModel, demand: Union[dict, float], demand_factor: Union[dict, float],
                              demand_scale_level: int = 0, scheduling_scale_level: int = 0,
                              cluster_wt: dict = None, loc_res_dict: dict = None) -> Constraint:
    """Ensures that demand for resource is met at chosen temporal scale

    Args:
        instance (ConcreteModel): pyomo instance
        demand (Union[dict, float]): base demand
        demand_factor (Union[dict, float]): factor to adjust for demand variability
        demand_scale_level (int, optional): scale of demand decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        cluster_wt (dict, optional): weight of each cluster if using clustering. Defaults to None.
        loc_res_dict (dict, optional): location resource map. Defaults to None. 

    Returns:
        Constraint: demand
    """
    scales = scale_list(instance=instance, scale_levels=demand_scale_level+1)
    # scales = scale_list(instance=instance,
    #                     scale_levels=len(instance.scales))
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level + 1)

    if loc_res_dict is None:
        loc_res_dict = dict()

    def demand_penalty_rule(instance, location, resource, *scale_list):

        if demand_factor[location] is not None:
            if isinstance(demand_factor[location][list(demand_factor[location])[0]], (float, int)):
                discharge = sum(instance.S[location, resource_, scale_list[:scheduling_scale_level + 1]] for
                                resource_ in instance.resources_demand)
            else:
                discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[
                    :demand_scale_level + 1] == scale_list)

            if isinstance(demand, dict):
                if resource in loc_res_dict[location]:
                    if resource in demand_factor[location].keys():
                        demandtarget = demand[location][resource] * \
                            demand_factor[location][resource][scale_list[:demand_scale_level + 1]]
                    else:
                        demandtarget = demand[location][resource]
                else:
                    demandtarget = 0
            else:
                if resource in loc_res_dict[location]:
                    demandtarget = demand * \
                        demand_factor[location][resource][scale_list[:demand_scale_level + 1]]
                else:
                    demandtarget = 0
        else:
            # TODO - doesn't meet demand in first timeperiod
            discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[
                :demand_scale_level + 1] == scale_list)

            if isinstance(demand, dict):
                demandtarget = demand[location][resource]
            else:
                demandtarget = demand

        return discharge >= demandtarget - instance.Demand_penalty[location, resource, scale_list[:demand_scale_level + 1]]

    if len(instance.locations) > 1:
        instance.constraint_demand_penalty = Constraint(
            instance.sinks, instance.resources_demand, *scales, rule=demand_penalty_rule, doc='specific demand for resources with penalty')

    else:
        instance.constraint_demand_penalty = Constraint(
            instance.locations, instance.resources_demand, *scales, rule=demand_penalty_rule,
            doc='specific demand for resources with penalty')
    constraint_latex_render(demand_penalty_rule)
    return instance.constraint_demand_penalty
