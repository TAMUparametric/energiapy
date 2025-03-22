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

from typing import Union, Tuple

from pyomo.environ import ConcreteModel, Constraint

from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list, scale_tuple


# def constraint_demand(instance: ConcreteModel, demand: Union[dict, float], demand_factor: Union[dict, float],
#                       demand_scale_level: int = 0, scheduling_scale_level: int = 0,
#                       cluster_wt: dict = None, location_resource_dict: dict = None, sign: str = 'geq'):

#     scales = scale_list(instance=instance,
#                         scale_levels=scheduling_scale_level + 1)
#     scale_iter = scale_tuple(
#         instance=instance, scale_levels=scheduling_scale_level + 1)
#     if location_resource_dict is None:
#         location_resource_dict = dict()

#     def demand_rule(instance, location, resource, *scale_list):
#         discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[
#             :demand_scale_level + 1] == scale_list)

#         if resource in instance.resources_varying_demand:
#             demandtarget = demand[location][resource] * \
#                 demand_factor[location][resource][scale_list[:scheduling_scale_level + 1]]
#         else:
#             demandtarget = demand[location][resource]

#         if sign == 'geq':
#             return discharge >= demandtarget

#         if sign == 'leq':
#             return discharge <= demandtarget

#         if sign == 'eq':
#             return discharge == demandtarget

#     if len(instance.locations) > 1:
#         instance.constraint_demand = Constraint(
#             instance.sinks, instance.resources_demand, *scales, rule=demand_rule, doc='specific demand for resources')

#     else:
#         instance.constraint_demand = Constraint(
#             instance.locations, instance.resources_demand, *scales, rule=demand_rule,
#             doc='specific demand for resources')

#     constraint_latex_render(demand_rule)
#     return instance.constraint_demand


def constraint_demand(instance: ConcreteModel, demand: Union[dict, float], demand_factor: Union[dict, float],
                      demand_scale_level: int = 0, scheduling_scale_level: int = 0,
                      cluster_wt: dict = None, location_resource_dict: dict = None, sign: str = 'geq') -> Constraint:
    """Ensures that demand for resource is met at chosen temporal scale

    Args:
        instance (ConcreteModel): pyomo instance
        demand (Union[dict, float]): base demand
        demand_factor (Union[dict, float]): factor to adjust for demand variability
        demand_scale_level (int, optional): scale of demand decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        cluster_wt (dict, optional): weight of each cluster if using clustering. Defaults to None.
        location_resource_dict (dict, optional): location resource map. Defaults to None.
        sign (str, optional): Should the supply be greater('geq')/lesser('leq')/equal('eq') to the demand. Defaults to 'geq'

    Returns:
        Constraint: demand
    """
    scales = scale_list(instance=instance, scale_levels=demand_scale_level+1)
    # scales = scale_list(instance=instance,
    #                     scale_levels=len(instance.scales))
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level + 1)

    if location_resource_dict is None:
        location_resource_dict = dict()

    def demand_rule(instance, location, resource, *scale_list):

        if demand_factor[location] is not None:
            if isinstance(demand_factor[location][list(demand_factor[location])[0]], (float, int)):
                discharge = sum(instance.S[location, resource_, scale_list[:scheduling_scale_level + 1]] for
                                resource_ in instance.resources_demand)

            else:
                discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[
                    :demand_scale_level + 1] == scale_list)

            if isinstance(demand, dict):
                if resource in location_resource_dict[location]:
                    if resource in demand_factor[location].keys():
                        demandtarget = demand[location][resource] * \
                            demand_factor[location][resource][scale_list[:demand_scale_level + 1]]
                    else:
                        demandtarget = demand[location][resource]
                else:
                    demandtarget = 0
            else:
                if resource in location_resource_dict[location]:
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

        if sign == 'geq':
            return discharge >= demandtarget

        if sign == 'leq':
            return discharge <= demandtarget

        if sign == 'eq':
            return discharge == demandtarget

    if len(instance.locations) > 1:
        instance.constraint_demand = Constraint(
            instance.sinks, instance.resources_demand, *scales, rule=demand_rule, doc='specific demand for resources')

    else:
        instance.constraint_demand = Constraint(
            instance.locations, instance.resources_demand, *scales, rule=demand_rule,
            doc='specific demand for resources')

    constraint_latex_render(demand_rule)
    return instance.constraint_demand

def constraint_demand_lb(instance: ConcreteModel, demand: Union[dict, float], demand_factor: Union[dict, float],
                      demand_scale_level: int = 0, scheduling_scale_level: int = 0, epsilon: float = 1,
                      cluster_wt: dict = None, location_resource_dict: dict = None, sign: str = 'geq') -> Constraint:
    """Ensures that demand for resource is met at chosen temporal scale

    Args:
        instance (ConcreteModel): pyomo instance
        demand (Union[dict, float]): base demand
        demand_factor (Union[dict, float]): factor to adjust for demand variability
        demand_scale_level (int, optional): scale of demand decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        cluster_wt (dict, optional): weight of each cluster if using clustering. Defaults to None.
        location_resource_dict (dict, optional): location resource map. Defaults to None.
        sign (str, optional): Should the supply be greater('geq')/lesser('leq')/equal('eq') to the demand. Defaults to 'geq'

    Returns:
        Constraint: demand
    """
    scales = scale_list(instance=instance, scale_levels=demand_scale_level+1)
    # scales = scale_list(instance=instance,
    #                     scale_levels=len(instance.scales))
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level + 1)

    if location_resource_dict is None:
        location_resource_dict = dict()

    def demand_rule(instance, location, resource, *scale_list):

        if demand_factor[location] is not None:
            if isinstance(demand_factor[location][list(demand_factor[location])[0]], (float, int)):
                discharge = sum(instance.S[location, resource_, scale_list[:scheduling_scale_level + 1]] for
                                resource_ in instance.resources_demand)

            else:
                discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[
                    :demand_scale_level + 1] == scale_list)

            if isinstance(demand, dict):
                if resource in location_resource_dict[location]:
                    if resource in demand_factor[location].keys():
                        demandtarget = demand[location][resource] * \
                            demand_factor[location][resource][scale_list[:demand_scale_level + 1]]
                    else:
                        demandtarget = demand[location][resource]
                else:
                    demandtarget = 0
            else:
                if resource in location_resource_dict[location]:
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

        if sign == 'geq':
            return discharge >= epsilon*demandtarget

        if sign == 'leq':
            return discharge <= epsilon*demandtarget

        if sign == 'eq':
            return discharge == epsilon*demandtarget

    if len(instance.locations) > 1:
        instance.constraint_demand_lb = Constraint(
            instance.sinks, instance.resources_demand, *scales, rule=demand_rule, doc='specific demand for resources')

    else:
        instance.constraint_demand_lb = Constraint(
            instance.locations, instance.resources_demand, *scales, rule=demand_rule,
            doc='specific demand for resources')

    constraint_latex_render(demand_rule)
    return instance.constraint_demand_lb



def constraint_demand_penalty(instance: ConcreteModel, demand: Union[dict, float], demand_factor: Union[dict, float],
                              demand_scale_level: int = 0, scheduling_scale_level: int = 0,
                              cluster_wt: dict = None, location_resource_dict: dict = None, sign: str = 'geq') -> Constraint:
    """Ensures that demand for resource is met at chosen temporal scale

    Args:
        instance (ConcreteModel): pyomo instance
        demand (Union[dict, float]): base demand
        demand_factor (Union[dict, float]): factor to adjust for demand variability
        demand_scale_level (int, optional): scale of demand decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        cluster_wt (dict, optional): weight of each cluster if using clustering. Defaults to None.
        location_resource_dict (dict, optional): location resource map. Defaults to None. 
        sign (str, optional): Should the supply be greater('geq')/lesser('leq')/equal('eq') to the demand. Defaults to 'geq'

    Returns:
        Constraint: demand
    """
    scales = scale_list(instance=instance, scale_levels=demand_scale_level+1)
    # scales = scale_list(instance=instance,
    #                     scale_levels=len(instance.scales))
    scale_iter = scale_tuple(instance=instance, scale_levels=scheduling_scale_level + 1)
    scale_iter_d = scale_tuple(instance=instance, scale_levels=demand_scale_level + 1)

    if location_resource_dict is None:
        location_resource_dict = dict()

    def demand_penalty_rule(instance, location, resource, *scale_list):
        if scale_list[:scheduling_scale_level+1] in scale_iter and scale_list[:demand_scale_level+1] in scale_iter_d:
            if demand_factor[location] is not None:
                if isinstance(demand_factor[location][list(demand_factor[location])[0]], (float, int)):
                    discharge = sum(instance.S[location, resource_, scale_list[:scheduling_scale_level + 1]] for
                                    resource_ in instance.resources_demand)
                else:
                    discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[
                        :demand_scale_level + 1] == scale_list)

                if isinstance(demand, dict):
                    if resource in location_resource_dict[location]:
                        if resource in demand_factor[location].keys():
                            demandtarget = demand[location][resource] * \
                                demand_factor[location][resource][scale_list[:demand_scale_level + 1]]
                        else:
                            demandtarget = demand[location][resource]
                    else:
                        demandtarget = 0
                else:
                    if resource in location_resource_dict[location]:
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

            if sign == 'geq':
                return discharge >= demandtarget - instance.Demand_penalty[location, resource, scale_list[:demand_scale_level + 1]]

            if sign == 'leq':
                return discharge <= demandtarget - instance.Demand_penalty[location, resource, scale_list[:demand_scale_level + 1]]

            if sign == 'eq':
                return discharge == demandtarget - instance.Demand_penalty[location, resource, scale_list[:demand_scale_level + 1]]
        else:
            return Constraint.Skip

    if len(instance.locations) > 1:
        instance.constraint_demand_penalty = Constraint(
            instance.sinks, instance.resources_demand, *scales, rule=demand_penalty_rule, doc='specific demand for resources with penalty')

    else:
        instance.constraint_demand_penalty = Constraint(
            instance.locations, instance.resources_demand, *scales, rule=demand_penalty_rule,
            doc='specific demand for resources with penalty')
    constraint_latex_render(demand_penalty_rule)
    return instance.constraint_demand_penalty

def constraint_demand_penalty_location(instance: ConcreteModel, cluster_wt: dict,
                                       network_scale_level: int = 0, demand_scale_level: int = 0) -> Constraint:
    """

    Args:
        instance (ConcreteModel): pyomo instance
        cluster_wt:
        network_scale_level:

    Returns:
        Constraint: _description_
    """

    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)
    scale_iter_n = scale_tuple(instance=instance, scale_levels=network_scale_level + 1)
    scale_iter = scale_tuple(instance=instance, scale_levels=demand_scale_level+1)

    def location_demand_penalty_rule(instance, location, resource_demand, *scale_list):
        if scale_list in scale_iter_n:
            def weight(x): return 1 if cluster_wt is None else cluster_wt[x]

            return instance.Demand_penalty_location[location, resource_demand, scale_list] == sum(
                weight(scale_) * instance.Demand_penalty[location, resource_demand, scale_[:demand_scale_level + 1]]
                for scale_ in scale_iter if scale_[:network_scale_level + 1] == scale_list)
        else:
            return Constraint.Skip

    instance.constraint_demand_penalty_location = Constraint(instance.locations, instance.resources_demand, *scales,
                                                             rule=location_demand_penalty_rule,
                                                             doc='total unmet demand at a location')
    constraint_latex_render(location_demand_penalty_rule)
    return instance.constraint_demand_penalty_location

def constraint_demand_penalty_network(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """

    Args:
        instance:
        network_scale_level:

    Returns:

    """

    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)
    scale_iter = scale_tuple(instance=instance, scale_levels=network_scale_level + 1)

    def demand_penalty_network_rule(instance, resource_demand, *scale_list):
        if scale_list in scale_iter:
            return instance.Demand_penalty_network[resource_demand, scale_list] == sum(
                instance.Demand_penalty_location[location_, resource_demand, scale_list] for location_ in instance.locations)
        else:
            return Constraint.Skip

    instance.constraint_demand_penalty_network = Constraint(
        instance.resources_demand, *scales, rule=demand_penalty_network_rule, doc='total unmet demand from network')
    constraint_latex_render(demand_penalty_network_rule)
    return instance.constraint_demand_penalty_network

def constraint_demand_penalty_cost(instance: ConcreteModel, demand_penalty_dict: dict, demand_penalty_factor: dict, demand_scale_level: int):
    '''

    Args:
        instance:
        demand_penalty_dict:
        network_scale_level:

    Returns:

    '''

    scales = scale_list(instance=instance, scale_levels=demand_scale_level + 1)

    scale_iter = scale_tuple(instance=instance, scale_levels=demand_scale_level+1)

    def demand_penalty_cost_rule(instance, location, resource_demand, *scale_list):
        if scale_list[:demand_scale_level + 1] in scale_iter:
            if demand_penalty_dict[location][resource_demand] is not None:
                Demand_penalty = instance.Demand_penalty[location, resource_demand, scale_list]
            else:
                Demand_penalty = 0

            if demand_penalty_factor[location] is not None:
                if resource_demand in list(demand_penalty_factor[location].keys()):
                    demand_penalty_fact = demand_penalty_factor[location][resource_demand][scale_list]
                else:
                    demand_penalty_fact = 1
            else:
                demand_penalty_fact = 1

            return instance.Demand_penalty_cost[location, resource_demand, scale_list] == demand_penalty_fact * demand_penalty_dict[location][resource_demand] * Demand_penalty
        else:
            return Constraint.Skip

    instance.constraint_demand_penalty_cost = Constraint(instance.locations, instance.resources_demand, *scales,
                                                         rule=demand_penalty_cost_rule, doc='Demand penalty cost')
    constraint_latex_render(demand_penalty_cost_rule)
    return instance.constraint_demand_penalty_cost


def constraint_demand_penalty_cost_location(instance: ConcreteModel, demand_scale_level: int = 0,
                                            network_scale_level: int = 0):
    '''

    Args:
        instance:
        demand_scale_level:
        network_scale_level:

    Returns:

    '''
    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)
    scale_iter_n = scale_tuple(instance=instance, scale_levels=network_scale_level + 1)
    scale_iter = scale_tuple(instance=instance, scale_levels=demand_scale_level + 1)

    def location_demand_penalty_cost_rule(instance, location, resource_demand, *scale_list):
        if scale_list in scale_iter_n:
            return instance.Demand_penalty_cost_location[location, resource_demand, scale_list] == sum(
                instance.Demand_penalty_cost[location, resource_demand, scale_[:demand_scale_level + 1]]
                for scale_ in scale_iter if scale_[:network_scale_level + 1] == scale_list)
        else:
            return Constraint.Skip

    instance.constraint_demand_penalty_cost_location = Constraint(instance.locations, instance.resources_demand,
                                                                  *scales, rule=location_demand_penalty_cost_rule,
                                                                  doc='Total demand penalty cost at a location')
    constraint_latex_render(location_demand_penalty_cost_rule)
    return instance.constraint_demand_penalty_cost_location


def constraint_demand_penalty_cost_network(instance: ConcreteModel, network_scale_level: int = 0):
    """

    Args:
        instance:
        network_scale_level:

    Returns:

    """

    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)
    scale_iter = scale_tuple(instance=instance, scale_levels=network_scale_level + 1)

    def network_demand_penalty_cost_rule(instance, resource_demand, *scale_list):
        if scale_list in scale_iter:
            return instance.Demand_penalty_cost_network[resource_demand, scale_list] == sum(
                instance.Demand_penalty_cost_location[location_, resource_demand, scale_list]
                for location_ in instance.locations)
        else:
            return Constraint.Skip

    instance.constraint_demand_penalty_cost_network = Constraint(instance.resources_demand, *scales,
                                                                 rule=network_demand_penalty_cost_rule,
                                                                 doc='Total demand penalty cost for the network')
    constraint_latex_render(network_demand_penalty_cost_rule)
    return instance.constraint_demand_penalty_cost_network

def constraint_demand_theta(instance: ConcreteModel, demand: Union[dict, float], demand_factor: Union[dict, float],
                            demand_scale_level: int = 0, scheduling_scale_level: int = 0,
                            cluster_wt: dict = None, location_resource_dict: dict = None, sign: str = 'geq') -> Constraint:
    """Ensures that demand for resource is met at chosen temporal scale with the demand being multiplied by a
    multiparametric theta variable 

    Args:
        instance (ConcreteModel): pyomo instance
        demand (Union[dict, float]): base demand
        demand_factor (Union[dict, float]): factor to adjust for demand variability
        demand_scale_level (int, optional): scale of demand decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        cluster_wt (dict, optional): weight of each cluster if using clustering. Defaults to None.
        location_resource_dict (dict, optional): location resource map. Defaults to None. 
        sign (str, optional): Should the supply be greater('geq')/lesser('leq')/equal('eq') to the demand. Defaults to 'geq'

    Returns:
        Constraint: demand
    """
    scales = scale_list(instance=instance, scale_levels=demand_scale_level+1)
    # scales = scale_list(instance=instance,
    #                     scale_levels=len(instance.scales))
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level + 1)

    if location_resource_dict is None:
        location_resource_dict = dict()

    def demand_rule(instance, location, resource, *scale_list):

        if demand_factor[location] is not None:
            if isinstance(demand_factor[location][list(demand_factor[location])[0]], (float, int)):
                discharge = sum(instance.S[location, resource_, scale_list[:scheduling_scale_level + 1]] for
                                resource_ in instance.resources_demand)
            else:
                discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[
                    :demand_scale_level + 1] == scale_list)

            if isinstance(demand, dict):
                if resource in location_resource_dict[location]:
                    if resource in demand_factor[location].keys():
                        demandtarget = demand[location][resource] * \
                            demand_factor[location][resource][scale_list[:demand_scale_level + 1]]
                    else:
                        demandtarget = demand[location][resource]
                else:
                    demandtarget = 0
            else:
                if resource in location_resource_dict[location]:
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

        if sign == 'geq':
            return discharge >= demandtarget*instance.demand_theta[location, resource, scale_list[:demand_scale_level]]

        if sign == 'leq':
            return discharge <= demandtarget*instance.demand_theta[location, resource, scale_list[:demand_scale_level]]

        if sign == 'eq':
            return discharge == demandtarget*instance.demand_theta[location, resource, scale_list[:demand_scale_level]]

    if len(instance.locations) > 1:
        instance.constraint_demand = Constraint(
            instance.sinks, instance.resources_demand, *scales, rule=demand_rule, doc='specific demand for resources')

    else:
        instance.constraint_demand = Constraint(
            instance.locations, instance.resources_demand, *scales, rule=demand_rule,
            doc='specific demand for resources')
    constraint_latex_render(demand_rule)
    return instance.constraint_demand
