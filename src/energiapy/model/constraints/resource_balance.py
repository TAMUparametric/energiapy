"""pyomo resource balance constraints
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

class ProcessMode(Enum):
    single = auto() #only allows one mode
    multi = auto() # allows multiple modes


def resource_consumption_constraint(instance: ConcreteModel, loc_res_dict: dict = {}, cons_max: dict = {}, scheduling_scale_level: int = 0) -> Constraint:
    """Determines consumption of resource at location in network 

    Args:
        instance (ConcreteModel): pyomo instance
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        cons_max (dict, optional): maximum allowed consumption of resource at location. Defaults to {}.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: resource_consumption_constraint
    """
    scales = scale_list(instance=instance,
                        scale_levels=instance.scales.__len__())

    def resource_consumption_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.C[location, resource, scale_list[:scheduling_scale_level+1]] <= cons_max[location][resource]
        else:
            return instance.C[location, resource, scale_list[:scheduling_scale_level+1]] <= 0
    instance.resource_consumption_constraint = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=resource_consumption_rule, doc='resource consumption')
    constraint_latex_render(resource_consumption_rule)
    return instance.resource_consumption_constraint


def resource_purchase_constraint(instance: ConcreteModel, cost_factor: dict = {}, price: dict = {},
                                 loc_res_dict: dict = {}, scheduling_scale_level: int = 0, expenditure_scale_level: int = 0) -> Constraint:
    """Determines expenditure on resource at location in network at the scheduling/expenditure scale

    Args:
        instance (ConcreteModel): pyomo instance
        cost_factor (dict, optional): uncertain cost training data. Defaults to {}.
        price (dict, optional): base price of resource. Defaults to {}.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        expenditure_scale_level (int, optional): scale of resource purchase decisions. Defaults to 0.

    Returns:
        Constraint: resource_purchase_constraint
    """
    scales = scale_list(instance=instance,
                        scale_levels=instance.scales.__len__())

    def resource_purchase_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_varying.intersection(loc_res_dict[location]):
            return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == price[location][resource] *\
                cost_factor[location][resource][scale_list[:expenditure_scale_level+1]] * \
                instance.C[location, resource,
                           scale_list[:scheduling_scale_level+1]]
        else:
            if resource in instance.resources_purch.intersection(loc_res_dict[location]):
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == price[location][resource]*instance.C[location, resource, scale_list[:scheduling_scale_level+1]]
            else:
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == 0
    instance.resource_purchase_constraint = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=resource_purchase_rule, doc='expenditure on purchase of resource')
    constraint_latex_render(resource_purchase_rule)
    return instance.resource_purchase_constraint


def inventory_balance_constraint(instance: ConcreteModel, scheduling_scale_level: int = 0, \
    conversion: dict = {}, cluster_wt: dict = None) -> Constraint:
    """balances resource across the scheduling horizon
    Mass balance in any temporal discretization has the following within their respective sets:
    - consumption for resources that can be purchased
    - produced for resources produced in the system. [conversion * nameplate capacity]
    - discharge for resources that can be sold(if selling cost)/discharged bound by the demand constraint
    - transport for resources that can be translocated
    - storage for resources that can be held in inventory
    
    The general mass balance is given as:
    
    consumption + produced - discharge + transport == storage
    
    Args:
        instance (ConcreteModel): pyomo instance
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        conversion (dict, optional): unit conversion of resource by production facility. Defaults to {}.

    Returns:
        Constraint: inventory_balance_constraint
    """
    scales = scale_list(instance=instance,
                        scale_levels=instance.scales.__len__())
    scale_iter = scale_tuple(
        instance=instance, scale_levels=instance.scales.__len__())

    def inventory_balance_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_purch:
            consumption = instance.C[location, resource,
                                     scale_list[:scheduling_scale_level+1]]
        else:
            consumption = 0

        if resource in instance.resources_store:
            if scale_list[:scheduling_scale_level+1] != scale_iter[0]:
                storage = instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] \
                    - instance.Inv[location, resource, scale_iter[scale_iter.index(
                        scale_list[:scheduling_scale_level+1]) - 1]]
            else:
                storage = instance.Inv[location, resource,
                                       scale_list[:scheduling_scale_level+1]]
        else:
            storage = 0

        if resource in instance.resources_sell:
            discharge = instance.S[location, resource,
                                   scale_list[:scheduling_scale_level+1]]
        else:
            discharge = 0

        if len(instance.locations) > 1:
            if resource in instance.resources_trans:
                transport = sum(instance.Imp[location, source_, resource, scale_list[:scheduling_scale_level+1]] for source_ in instance.sources if source_ != location if location in instance.sinks)\
                    - sum(instance.Exp[location, sink_, resource, scale_list[:scheduling_scale_level+1]] for sink_ in instance.sinks if sink_ != location if location in instance.sources)\

            else:
                transport = 0
        else:
            transport = 0

        # produced = sum(conversion[process][resource]*instance.P[location, process, scale_list[:scheduling_scale_level+1]] for process in instance.processes_singlem) \
        #     + sum(instance.P[location, process, scale_list[:scheduling_scale_level+1]] for process in instance.processes_multim)
        
        produced = sum(conversion[process][resource]*instance.P[location, process,
                       scale_list[:scheduling_scale_level+1]] for process in instance.processes_full) #includes processes + discharge

        if cluster_wt is not None:
            return cluster_wt[scale_list[:scheduling_scale_level+1]]*(consumption + produced - discharge + transport) == storage
        else:
            return consumption + produced - discharge + transport == storage
    instance.inventory_balance_constraint = Constraint(
        instance.locations, instance.resources, *scales, rule=inventory_balance_rule, doc='mass balance across scheduling scale')
    constraint_latex_render(inventory_balance_constraint)
    return instance.inventory_balance_constraint


def demand_constraint(instance: ConcreteModel, demand: Union[dict, float], demand_factor: Union[dict, float], \
    demand_scale_level: int = 0, scheduling_scale_level: int = 0, cluster_wt: dict = None) -> Constraint:
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

    def demand_rule(instance, location, resource, *scale_list): 
         
        if demand_factor[location] is not None:
            if type(demand_factor[location][list(demand_factor[location])[0]]) == float:
                discharge = sum(instance.S[location, resource_, scale_list[:scheduling_scale_level+1]] for
                        resource_ in instance.resources_demand) 
            else:
                discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[:scheduling_scale_level+1] == scale_list)
           
            if type(demand) is dict:
                demandtarget = demand[location][resource]*demand_factor[location][resource][scale_list[:demand_scale_level+1]]
            else:
                demandtarget = demand*demand_factor[location][resource][scale_list[:demand_scale_level+1]]
                
        else: 
            # if scale_list[:scheduling_scale_level+1] != scale_iter[0]: #TODO - doesn't meet demand in first timeperiod
            discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[:scheduling_scale_level+1] == scale_list)
            
            if type(demand) is dict:        
                demandtarget = demand[location][resource]
            
            else:
                demandtarget = demand
            
            # else:
            #     discharge = instance.S[location, resource, scale_list[:scheduling_scale_level+1]]
            #     demandtarget = 0
            
        # if cluster_wt is not None: 
        #     return discharge == cluster_wt[scale_list[:scheduling_scale_level+1]]*demandtarget
        # else:
        # return discharge >= demandtarget
        return discharge >= demandtarget

    if len(instance.locations) > 1:
        instance.demand_constraint = Constraint(
            instance.sinks, instance.resources_demand, *scales, rule=demand_rule, doc='specific demand for resources')
    else:
        instance.demand_constraint = Constraint(
            instance.locations, instance.resources_demand, *scales, rule=demand_rule, doc='specific demand for resources')
    constraint_latex_render(demand_rule)
    return instance.demand_constraint



def location_production_constraint(instance: ConcreteModel, cluster_wt: dict, network_scale_level: int = 0) -> Constraint:
    """Determines total production capacity utilization at location

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_production_constraint
    """

    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=instance.scales.__len__())

    def location_production_rule(instance, location, process, *scale_list):
        if cluster_wt is not None:
            return instance.P_location[location, process, scale_list] == sum(cluster_wt[scale_]*instance.P[location, process, scale_] for scale_ in scale_iter)
        else:
            return instance.P_location[location, process, scale_list] == sum(instance.P[location, process, scale_] for scale_ in scale_iter)
    instance.location_production_constraint = Constraint(
        instance.locations, instance.processes, *scales, rule=location_production_rule, doc='total production at location')
    constraint_latex_render(location_production_rule)
    return instance.location_production_constraint


def location_discharge_constraint(instance: ConcreteModel, cluster_wt: dict, network_scale_level: int = 0) -> Constraint:
    """Determines total resource discharged/sold at locations in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_discharge_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=instance.scales.__len__())

    def location_discharge_rule(instance, location, resource, *scale_list):
        if cluster_wt is not None:
            return instance.S_location[location, resource, scale_list] == sum(cluster_wt[scale_]*instance.S[location, resource, scale_] for scale_ in scale_iter)
        else:
            return instance.S_location[location, resource, scale_list] == sum(instance.S[location, resource, scale_] for scale_ in scale_iter)
    instance.location_discharge_constraint = Constraint(
        instance.locations, instance.resources_sell, *scales, rule=location_discharge_rule, doc='total discharge at location')
    constraint_latex_render(location_discharge_rule)
    return instance.location_discharge_constraint


def location_consumption_constraint(instance: ConcreteModel, cluster_wt: dict, network_scale_level: int = 0) -> Constraint:
    """Determines total resource consumed at locations in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_consumption_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=instance.scales.__len__())

    def location_consumption_rule(instance, location, resource, *scale_list):
        if cluster_wt is not None:
            return instance.C_location[location, resource, scale_list] == sum(cluster_wt[scale_]*instance.C[location, resource, scale_] for scale_ in scale_iter)
        else:
            return instance.C_location[location, resource, scale_list] == sum(instance.C[location, resource, scale_] for scale_ in scale_iter)
    instance.location_consumption_constraint = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=location_consumption_rule, doc='total consumption at location')
    constraint_latex_render(location_consumption_rule)
    return instance.location_consumption_constraint


def location_purchase_constraint(instance: ConcreteModel, cluster_wt: dict, network_scale_level: int = 0) -> Constraint:
    """Determines total resource purchase expenditure at locations in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_purchase_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=instance.scales.__len__())

    def location_purchase_rule(instance, location, resource, *scale_list):
        if cluster_wt is not None:
            return instance.B_location[location, resource, scale_list] == sum(cluster_wt[scale_]*instance.B[location, resource, scale_] for scale_ in scale_iter)
        else:
            return instance.B_location[location, resource, scale_list] == sum(instance.B[location, resource, scale_] for scale_ in scale_iter)
    instance.location_purchase_constraint = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=location_purchase_rule, doc='total purchase at location')
    constraint_latex_render(location_purchase_rule)
    return instance.location_purchase_constraint


# *-------------------------Network scale mass balance calculation constraints--------------------------

def network_production_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Determines total production utilization across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_production_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_production_rule(instance, process, *scale_list):
        return instance.P_network[process, scale_list] == sum(instance.P_location[location_, process, scale_list] for location_ in instance.locations)
    instance.network_production_constraint = Constraint(
        instance.processes, *scales, rule=network_production_rule, doc='total production from network')
    constraint_latex_render(network_production_rule)
    return instance.network_production_constraint


def network_discharge_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Determines total resource discharged across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_discharge_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_discharge_rule(instance, resource, *scale_list):
        return instance.S_network[resource, scale_list] == sum(instance.S_location[location_, resource, scale_list] for location_ in instance.locations)
    instance.network_discharge_constraint = Constraint(
        instance.resources_sell, *scales, rule=network_discharge_rule, doc='total discharge from network')
    constraint_latex_render(network_discharge_rule)
    return instance.network_discharge_constraint


def network_consumption_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Determines total resource consumed across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_consumption_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_consumption_rule(instance, resource, *scale_list):
        return instance.C_network[resource, scale_list] == sum(instance.C_location[location_, resource, scale_list] for location_ in instance.locations)
    instance.network_consumption_constraint = Constraint(
        instance.resources_purch, *scales, rule=network_consumption_rule, doc='total consumption from network')
    constraint_latex_render(network_consumption_rule)
    return instance.network_consumption_constraint


def network_purchase_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Determines total purchase expenditure on resource across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_purchase_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_purchase_rule(instance, resource, *scale_list):
        return instance.B_network[resource, scale_list] == sum(instance.B_location[location_, resource, scale_list] for location_ in instance.locations)
    instance.network_purchase_constraint = Constraint(
        instance.resources_purch, *scales, rule=network_purchase_rule, doc='total purchase from network')
    constraint_latex_render(network_purchase_rule)
    return instance.network_purchase_constraint
