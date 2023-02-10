"""pyomo uncertain constraints
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
from ...utils.model_utils import scale_list
from ...utils.model_utils import scale_pyomo_set
from ...utils.model_utils import scale_tuple
from ...components.location import Location
from itertools import product
from typing import Union
from enum import Enum, auto

def demand_constraint_flex(instance: ConcreteModel, demand: int, demand_factor: Union[dict, float], \
    demand_scale_level: int = 0, scheduling_scale_level: int = 0) -> Constraint:
    """Ensures that demand for resource is met at chosen temporal scale

    Args:
        instance (ConcreteModel): pyomo instance
        demand_scale_level (int, optional): scale of demand decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        demand_dict (dict, optional): demand at location. Defaults to {}.

    Returns:
        Constraint: demand_constraint
    """
    # scales = scale_list(instance= instance, scale_levels = demand_scale_level+1)
    scales = scale_list(instance=instance,
                        scale_levels=instance.scales.__len__())
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level+1)
 
    def demand_flex_rule(instance, location, resource, *scale_list):
        if type(demand_factor[location][list(demand_factor[location])[0]]) == float:
            return sum(instance.S[location, resource_, scale_list[:scheduling_scale_level+1]] for
                       resource_ in instance.resources_demand) == demand*demand_factor[location][scale_list[:demand_scale_level+1]] - instance.Demand_slack[location, scale_list[:demand_scale_level+1]]
        else:
            return sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[:scheduling_scale_level+1] == scale_list)\
                == demand*demand_factor[location][resource][scale_list[:demand_scale_level+1]] - instance.Demand_slack[location, scale_list[:demand_scale_level+1]]

    if len(instance.locations) > 1:
        instance.demand_constraint_flex = Constraint(
            instance.sinks, instance.resources_demand, *scales, rule=demand_flex_rule, doc='specific demand for resources')
    else:
        instance.demand_constraint_flex = Constraint(
            instance.locations, instance.resources_demand, *scales, rule=demand_flex_rule, doc='specific demand for resources')
    constraint_latex_render(demand_flex_rule)
    return instance.demand_constraint_flex



def delta_cap_location_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=instance.scales.__len__())

    def delta_cap_location_rule(instance, location, process, *scale_list):
        return instance.Delta_Cap_P_location[location, process, scale_list] == sum(instance.Delta_Cap_P[location, process, scale_] for scale_ in scale_iter)
    instance.delta_cap_location_constraint = Constraint(
        instance.locations, instance.processes_varying, *scales, rule=delta_cap_location_rule, doc='total transport cost across scale')
    constraint_latex_render(delta_cap_location_rule)
    return instance.delta_cap_location_constraint


def delta_cap_network_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def delta_cap_network_rule(instance, process, *scale_list):
        return instance.Delta_Cap_P_network[process, scale_list] == sum(instance.Delta_Cap_P_location[location_, process, scale_list] for location_ in instance.locations)
    instance.delta_cap_network_constraint = Constraint(
        instance.processes_varying, *scales, rule=delta_cap_network_rule, doc='total transport cost across scale')
    constraint_latex_render(delta_cap_network_rule)
    return instance.delta_cap_network_constraint



def uncertain_nameplate_production_constraint(instance: ConcreteModel, network_scale_level: int = 0, scheduling_scale_level: int = 0) -> Constraint:
    """Determines production capacity utilization of facilities at location in network and capacity of facilities 
    with uncertain capacility available for utilization

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: uncertain_nameplate_production_constraint
    """
    scales = scale_list(instance=instance,
                        scale_levels=instance.scales.__len__())

    def uncertain_nameplate_production_rule(instance, location, process, *scale_list):
        if process in instance.processes_varying:
            return instance.P[location, process, scale_list[:scheduling_scale_level+1]] <= instance.Cap_P[location, process, scale_list[:network_scale_level+1]]\
                + instance.Delta_Cap_P[location, process,
                                       scale_list[:scheduling_scale_level+1]]
        else:
            return instance.P[location, process, scale_list[:scheduling_scale_level+1]] <= instance.Cap_P[location, process, scale_list[:network_scale_level+1]]
    instance.uncertain_nameplate_production_constraint = Constraint(
        instance.locations, instance.processes, *scales, rule=uncertain_nameplate_production_rule, doc='nameplate production capacity constraint')
    constraint_latex_render(uncertain_nameplate_production_rule)
    return instance.uncertain_nameplate_production_constraint


def uncertain_resource_purchase_constraint(instance: ConcreteModel, price: dict = {},  loc_res_dict: dict = {}, scheduling_scale_level: int = 0, expenditure_scale_level: int = 0) -> Constraint:
    """Determines expenditure on resource at location in network at the scheduling/expenditure scale
    with uncertainty in resource proce

    Args:
        instance (ConcreteModel): pyomo instance
        price (dict, optional): base price of resource. Defaults to {}.
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        expenditure_scale_level (int, optional): scale of expenditure decisions. Defaults to 0.

    Returns:
        Constraint: uncertain_resource_purchase_constraint
    """
    scales = scale_list(instance=instance,
                        scale_levels=instance.scales.__len__())

    def uncertain_resource_purchase_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_varying.intersection(loc_res_dict[location]):
            return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == price[location][resource] *\
                instance.C[location, resource, scale_list[:scheduling_scale_level+1]] * \
                instance.Delta_Cost_R[location, resource,
                                      scale_list[:scheduling_scale_level+1]]
        else:
            if resource in instance.resources_purch.intersection(loc_res_dict[location]):
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == price[location][resource]*instance.C[location, resource, scale_list[:scheduling_scale_level+1]]
            else:
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == 0
    instance.uncertain_resource_purchase_constraint = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=uncertain_resource_purchase_rule, doc='expenditure on purchase of resource')
    constraint_latex_render(uncertain_resource_purchase_rule)
    return instance.uncertain_resource_purchase_constraint
