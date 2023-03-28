"""pyomo resource balance constraints
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

from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list, scale_tuple


def constraint_resource_consumption(instance: ConcreteModel, loc_res_dict: dict = None, cons_max: dict = None,
                                    scheduling_scale_level: int = 0) -> Constraint:
    """Determines consumption of resource at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        cons_max (dict, optional): maximum allowed consumption of resource at location. Defaults to {}.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: resource_consumption
    """

    if loc_res_dict is None:
        loc_res_dict = dict()

    if cons_max is None:
        cons_max = dict()

    scales = scale_list(instance=instance,
                        scale_levels=instance.scales.__len__())

    def resource_consumption_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.C[location, resource, scale_list[:scheduling_scale_level + 1]] <= cons_max[location][
                resource]
        else:
            return instance.C[location, resource, scale_list[:scheduling_scale_level + 1]] <= 0

    instance.constraint_resource_consumption = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=resource_consumption_rule,
        doc='resource consumption')
    constraint_latex_render(resource_consumption_rule)
    return instance.constraint_resource_consumption


def constraint_resource_purchase(instance: ConcreteModel, cost_factor: dict = None, price: dict = None,
                                 loc_res_dict: dict = None, scheduling_scale_level: int = 0,
                                 expenditure_scale_level: int = 0) -> Constraint:
    """Determines expenditure on resource at location in network at the scheduling/expenditure scale

    Args:
        instance (ConcreteModel): pyomo instance
        cost_factor (dict, optional): uncertain cost training data. Defaults to {}.
        price (dict, optional): base price of resource. Defaults to {}.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        expenditure_scale_level (int, optional): scale of resource purchase decisions. Defaults to 0.

    Returns:
        Constraint: resource_purchase
    """

    if loc_res_dict is None:
        loc_res_dict = dict()

    if cost_factor is None:
        cost_factor = dict()

    if price is None:
        price = dict()

    scales = scale_list(instance=instance,
                        scale_levels=instance.scales.__len__())

    def resource_purchase_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_varying_price.intersection(loc_res_dict[location]):
            return instance.B[location, resource, scale_list[:scheduling_scale_level + 1]] == price[location][
                resource] * \
                cost_factor[location][resource][scale_list[:expenditure_scale_level + 1]] * \
                instance.C[location, resource,
                scale_list[:scheduling_scale_level + 1]]
        else:
            if resource in instance.resources_purch.intersection(loc_res_dict[location]):
                return instance.B[location, resource, scale_list[:scheduling_scale_level + 1]] == price[location][
                    resource] * instance.C[location, resource, scale_list[:scheduling_scale_level + 1]]
            else:
                return instance.B[location, resource, scale_list[:scheduling_scale_level + 1]] == 0

    instance.constraint_resource_purchase = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=resource_purchase_rule,
        doc='expenditure on purchase of resource')
    constraint_latex_render(resource_purchase_rule)
    return instance.constraint_resource_purchase


def constraint_inventory_balance(instance: ConcreteModel, scheduling_scale_level: int = 0,
                                 multiconversion: dict = None, mode_dict: dict = None,
                                 cluster_wt: dict = None) -> Constraint:
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
        multiconversion (dict, optional): unit conversion of resource by production facility. Defaults to {}.
        mode_dict (dict, optional): dictionary with modes available. Defaults to {}.
        cluster_wt (dict, optional): weight of cluster as determined through scenario aggregation. Defaults to None.

    Returns:
        Constraint: inventory_balance
    """

    if multiconversion is None:
        multiconversion = dict()

    if mode_dict is None:
        mode_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=instance.scales.__len__())
    scale_iter = scale_tuple(
        instance=instance, scale_levels=instance.scales.__len__())

    def inventory_balance_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_purch:
            consumption = instance.C[location, resource,
            scale_list[:scheduling_scale_level + 1]]
        else:
            consumption = 0

        if resource in instance.resources_store:
            if scale_list[:scheduling_scale_level + 1] != scale_iter[0]:
                storage = instance.Inv[location, resource, scale_list[:scheduling_scale_level + 1]] \
                          - instance.Inv[location, resource, scale_iter[scale_iter.index(
                    scale_list[:scheduling_scale_level + 1]) - 1]]
            else:
                storage = instance.Inv[location, resource,
                scale_list[:scheduling_scale_level + 1]]
        else:
            storage = 0

        if resource in instance.resources_sell:
            discharge = instance.S[location, resource,
            scale_list[:scheduling_scale_level + 1]]
        else:
            discharge = 0

        if len(instance.locations) > 1:
            if resource in instance.resources_trans:
                transport = sum(
                    instance.Imp[location, source_, resource, scale_list[:scheduling_scale_level + 1]] for source_ in
                    instance.sources if source_ != location if location in instance.sinks) \
                            - sum(
                    instance.Exp[location, sink_, resource, scale_list[:scheduling_scale_level + 1]] for sink_ in
                    instance.sinks if sink_ != location if location in instance.sources)
            else:
                transport = 0
        else:
            transport = 0

        # produced = sum(conversion[process][resource]*instance.P[location, process, scale_list[:scheduling_scale_level+1]] for process in instance.processes_singlem) \
        #     + sum(instance.P[location, process, scale_list[:scheduling_scale_level+1]] for process in instance.processes_multim)

        produced = sum(sum(multiconversion[process][mode][resource] * instance.P_m[location, process, mode,
        scale_list[:scheduling_scale_level + 1]] for mode in mode_dict[process]) for process in
                       instance.processes_full)  # includes processes + discharge

        weight = lambda x: 1 if cluster_wt is None else cluster_wt[x]

        return weight(scale_list[:scheduling_scale_level + 1]) * (
                    consumption + produced - discharge + transport) == storage

    instance.constraint_inventory_balance = Constraint(
        instance.locations, instance.resources, *scales, rule=inventory_balance_rule,
        doc='mass balance across scheduling scale')
    constraint_latex_render(inventory_balance_rule)
    return instance.constraint_inventory_balance


def constraint_demand(instance: ConcreteModel, demand: Union[dict, float], demand_factor: Union[dict, float],
                      demand_scale_level: int = 0, scheduling_scale_level: int = 0,
                      cluster_wt: dict = None) -> Constraint:
    """Ensures that demand for resource is met at chosen temporal scale

    Args:
        instance (ConcreteModel): pyomo instance
        demand_scale_level (int, optional): scale of demand decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        demand_dict (dict, optional): demand at location. Defaults to {}.

    Returns:
        Constraint: demand
    """
    # scales = scale_list(instance= instance, scale_levels = demand_scale_level+1)
    scales = scale_list(instance=instance,
                        scale_levels=instance.scales.__len__())
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level + 1)

    def demand_rule(instance, location, resource, *scale_list):

        if demand_factor[location] is not None:
            if isinstance(demand_factor[location][list(demand_factor[location])[0]], (float, int)):
                discharge = sum(instance.S[location, resource_, scale_list[:scheduling_scale_level + 1]] for
                                resource_ in instance.resources_demand)
            else:
                discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[
                                                                                                   :scheduling_scale_level + 1] == scale_list)

            if isinstance(demand, dict):
                demandtarget = demand[location][resource] * \
                               demand_factor[location][resource][scale_list[:demand_scale_level + 1]]
            else:
                demandtarget = demand * \
                               demand_factor[location][resource][scale_list[:demand_scale_level + 1]]

        else:
            # TODO - doesn't meet demand in first timeperiod
            discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[
                                                                                               :scheduling_scale_level + 1] == scale_list)

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


def constraint_location_production(instance: ConcreteModel, cluster_wt: dict,
                                   network_scale_level: int = 0) -> Constraint:
    """Determines total production capacity utilization at location

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_production
    """

    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=instance.scales.__len__())

    def location_production_rule(instance, location, process, *scale_list):
        weight = lambda x: 1 if cluster_wt is None else cluster_wt[x]
        return instance.P_location[location, process, scale_list] == sum(
            weight(scale_) * instance.P[location, process, scale_] for scale_ in scale_iter)

    instance.constraint_location_production = Constraint(
        instance.locations, instance.processes, *scales, rule=location_production_rule,
        doc='total production at location')
    constraint_latex_render(location_production_rule)
    return instance.constraint_location_production


def constraint_location_discharge(instance: ConcreteModel, cluster_wt: dict,
                                  network_scale_level: int = 0) -> Constraint:
    """Determines total resource discharged/sold at locations in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_discharge
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=instance.scales.__len__())

    def location_discharge_rule(instance, location, resource, *scale_list):
        weight = lambda x: 1 if cluster_wt is None else cluster_wt[x]

        return instance.S_location[location, resource, scale_list] == sum(
            weight(scale_) * instance.S[location, resource, scale_] for scale_ in scale_iter)

    instance.constraint_location_discharge = Constraint(
        instance.locations, instance.resources_sell, *scales, rule=location_discharge_rule,
        doc='total discharge at location')
    constraint_latex_render(location_discharge_rule)
    return instance.constraint_location_discharge


def constraint_location_consumption(instance: ConcreteModel, cluster_wt: dict,
                                    network_scale_level: int = 0) -> Constraint:
    """Determines total resource consumed at locations in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_consumption
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=instance.scales.__len__())

    def location_consumption_rule(instance, location, resource, *scale_list):
        weight = lambda x: 1 if cluster_wt is None else cluster_wt[x]

        return instance.C_location[location, resource, scale_list] == sum(
            weight(scale_) * instance.C[location, resource, scale_] for scale_ in scale_iter)

    instance.constraint_location_consumption = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=location_consumption_rule,
        doc='total consumption at location')
    constraint_latex_render(location_consumption_rule)
    return instance.constraint_location_consumption


def constraint_location_purchase(instance: ConcreteModel, cluster_wt: dict, network_scale_level: int = 0) -> Constraint:
    """Determines total resource purchase expenditure at locations in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_purchase
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=instance.scales.__len__())

    def location_purchase_rule(instance, location, resource, *scale_list):
        weight = lambda x: 1 if cluster_wt is None else cluster_wt[x]

        return instance.B_location[location, resource, scale_list] == sum(
            weight(scale_) * instance.B[location, resource, scale_] for scale_ in scale_iter)

    instance.constraint_location_purchase = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=location_purchase_rule,
        doc='total purchase at location')
    constraint_latex_render(location_purchase_rule)
    return instance.constraint_location_purchase


# *-------------------------Network scale mass balance calculation constraints--------------------------

def constraint_network_production(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Determines total production utilization across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_production
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)

    def network_production_rule(instance, process, *scale_list):
        return instance.P_network[process, scale_list] == sum(
            instance.P_location[location_, process, scale_list] for location_ in instance.locations)

    instance.constraint_network_production = Constraint(
        instance.processes, *scales, rule=network_production_rule, doc='total production from network')
    constraint_latex_render(network_production_rule)
    return instance.constraint_network_production


def constraint_network_discharge(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Determines total resource discharged across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_discharge
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)

    def network_discharge_rule(instance, resource, *scale_list):
        return instance.S_network[resource, scale_list] == sum(
            instance.S_location[location_, resource, scale_list] for location_ in instance.locations)

    instance.constraint_network_discharge = Constraint(
        instance.resources_sell, *scales, rule=network_discharge_rule, doc='total discharge from network')
    constraint_latex_render(network_discharge_rule)
    return instance.constraint_network_discharge


def constraint_network_consumption(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Determines total resource consumed across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_consumption
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)

    def network_consumption_rule(instance, resource, *scale_list):
        return instance.C_network[resource, scale_list] == sum(
            instance.C_location[location_, resource, scale_list] for location_ in instance.locations)

    instance.constraint_network_consumption = Constraint(
        instance.resources_purch, *scales, rule=network_consumption_rule, doc='total consumption from network')
    constraint_latex_render(network_consumption_rule)
    return instance.constraint_network_consumption


def constraint_network_purchase(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Determines total purchase expenditure on resource across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_purchase
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level + 1)

    def network_purchase_rule(instance, resource, *scale_list):
        return instance.B_network[resource, scale_list] == sum(
            instance.B_location[location_, resource, scale_list] for location_ in instance.locations)

    instance.constraint_network_purchase = Constraint(
        instance.resources_purch, *scales, rule=network_purchase_rule, doc='total purchase from network')
    constraint_latex_render(network_purchase_rule)
    return instance.constraint_network_purchase
