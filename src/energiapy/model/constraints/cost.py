"""cost constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from enum import Enum, auto
from itertools import product
from typing import Set

from pyomo.environ import ConcreteModel, Constraint

from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list, scale_tuple
from .constraints import Constraints


class Costdynamics(Enum):
    constant = auto()
    pwl = auto()
    scaled = auto()
    wind = auto()  # TODO allow user to give equation
    battery = auto()  # TODO allow user to give equation
    solar = auto()


# def constraint_transport_exp_cost(instance: ConcreteModel, scheduling_scale_level: int = 0, trans_cost: dict = {}, distance_dict: dict = {}) -> Constraint:
#     """Calculates the expenditure on exporting resource throught transport

#     Args:
#         instance (ConcreteModel): pyomo instance
#         scheduling_scale_level (int, optional): scheduling scale level. Defaults to 0.
#         trans_cost (dict, optional): dictionary with transport costs. Defaults to {}.
#         distance_dict (dict, optional): dictionary with distances. Defaults to {}.

#     Returns:
#         Constraint: transport_exp_cost
#     """
#     scales = scale_list(instance=instance,
#                         scale_levels=scheduling_scale_level+1)

#     def transport_exp_cost_rule(instance, source, sink, resource, transport, *scale_list):
#         return instance.Trans_exp_cost[source, sink, resource, transport, scale_list[:scheduling_scale_level+1]] == \
#             trans_cost[transport]*distance_dict[(source, sink)]*instance.Trans_exp[source,
#                                                                                    sink, resource, transport, scale_list[:scheduling_scale_level+1]]
#     instance.constraint_transport_exp_cost = Constraint(instance.sources, instance.sinks, instance.resources_trans,
#                                                         instance.transports, *scales, rule=transport_exp_cost_rule, doc='import of resource from sink to source')
#     constraint_latex_render(transport_exp_cost_rule)
#     return instance.constraint_transport_exp_cost


# *-------------------------purchase costing constraints-------------------------


def constraint_resource_purchase(instance: ConcreteModel, price_factor: dict = None, price: dict = None,
                                 location_resource_dict: dict = None, scheduling_scale_level: int = 0,
                                 purchase_scale_level: int = 0) -> Constraint:
    """Determines expenditure on resource at location in network at the scheduling/expenditure scale

    Args:
        instance (ConcreteModel): pyomo instance
        price_factor (dict, optional): uncertain cost training data. Defaults to {}.
        price (dict, optional): base price of resource. Defaults to {}.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        purchase_scale_level (int, optional): scale of resource purchase decisions. Defaults to 0.

    Returns:
        Constraint: resource_purchase
    """

    if location_resource_dict is None:
        location_resource_dict = dict()

    if price_factor is None:
        price_factor = dict()

    if price is None:
        price = dict()

    scales = scale_list(instance=instance, scale_levels=len(instance.scales))

    def resource_purchase_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_varying_price.intersection(location_resource_dict[location]):
            return instance.B[location, resource, scale_list[:scheduling_scale_level + 1]] == price[location][resource]*price_factor[location][resource][scale_list[:purchase_scale_level + 1]] * instance.C[location, resource, scale_list[:scheduling_scale_level + 1]]
        else:
            if resource in instance.resources_purch.intersection(location_resource_dict[location]):
                return instance.B[location, resource, scale_list[:scheduling_scale_level + 1]] == price[location][
                    resource] * instance.C[location, resource, scale_list[:scheduling_scale_level + 1]]
            else:
                return instance.B[location, resource, scale_list[:scheduling_scale_level + 1]] == 0

    instance.constraint_resource_purchase = Constraint(
        instance.locations, instance.resources_purch, *
        scales, rule=resource_purchase_rule,
        doc='expenditure on purchase of resource')
    constraint_latex_render(resource_purchase_rule)
    return instance.constraint_resource_purchase


def constraint_location_purchase(instance: ConcreteModel, cluster_wt: dict, network_scale_level: int = 0, scheduling_scale_level: int = 0) -> Constraint:
    """Determines total resource purchase expenditure at locations in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_purchase
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level + 1)

    def location_purchase_rule(instance, location, resource, *scale_list):
        def weight(x): return 1 if cluster_wt is None else cluster_wt[x]

        return instance.B_location[location, resource, scale_list] == sum(
            weight(scale_) * instance.B[location, resource,  scale_[:scheduling_scale_level + 1]] for scale_ in scale_iter
            if scale_[:network_scale_level + 1] == scale_list)

    instance.constraint_location_purchase = Constraint(
        instance.locations, instance.resources_purch, *
        scales, rule=location_purchase_rule,
        doc='total purchase at location')
    constraint_latex_render(location_purchase_rule)
    return instance.constraint_location_purchase


def constraint_network_purchase(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Determines total purchase expenditure on resource across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_purchase
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def network_purchase_rule(instance, resource, *scale_list):
        return instance.B_network[resource, scale_list] == sum(
            instance.B_location[location_, resource, scale_list] for location_ in instance.locations)

    instance.constraint_network_purchase = Constraint(
        instance.resources_purch, *scales, rule=network_purchase_rule, doc='total purchase from network')
    constraint_latex_render(network_purchase_rule)
    return instance.constraint_network_purchase


# *-------------------------revenue costing constraints--------------------------


def constraint_resource_revenue(instance: ConcreteModel, revenue_factor: dict = None, revenue: dict = None,
                                location_resource_dict: dict = None, scheduling_scale_level: int = 0) -> Constraint:
    """Determines revenue resource at location in network at the scheduling/expenditure scale

    Args:
        instance (ConcreteModel): pyomo instance
        revenue_factor (dict, optional): uncertain revenue training data. Defaults to {}.
        revenue (dict, optional): base revenue of resource. Defaults to {}.
        scheduling_scale_level  (int, optional): scale of scheduling decisions. Defaults to 0.


    Returns:
        Constraint: resource_revenue
    """

    if location_resource_dict is None:
        location_resource_dict = dict()

    if revenue_factor is None:
        revenue_factor = dict()

    if revenue is None:
        revenue = dict()

    scales = scale_list(instance=instance, scale_levels=len(instance.scales))

    def resource_revenue_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_varying_revenue.intersection(location_resource_dict[location]):
            return instance.R[location, resource, scale_list[:scheduling_scale_level + 1]] == revenue[location][resource]*revenue_factor[location][resource][scale_list[:scheduling_scale_level + 1]] * instance.S[location, resource, scale_list[:scheduling_scale_level + 1]]
        else:
            if resource in instance.resources_sell.intersection(location_resource_dict[location]):
                return instance.R[location, resource, scale_list[:scheduling_scale_level + 1]] == revenue[location][
                    resource] * instance.S[location, resource, scale_list[:scheduling_scale_level + 1]]
            else:
                return instance.R[location, resource, scale_list[:scheduling_scale_level + 1]] == 0

    instance.constraint_resource_revenue = Constraint(
        instance.locations, instance.resources_sell, *
        scales, rule=resource_revenue_rule,
        doc='revenue from resource')
    constraint_latex_render(resource_revenue_rule)
    return instance.constraint_resource_revenue


def constraint_location_revenue(instance: ConcreteModel, cluster_wt: dict, network_scale_level: int = 0, scheduling_scale_level: int = 0) -> Constraint:
    """Determines total resource revenue at locations in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.


    Returns:
        Constraint: location_revenue
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level + 1)

    def location_revenue_rule(instance, location, resource, *scale_list):
        def weight(x): return 1 if cluster_wt is None else cluster_wt[x]

        return instance.R_location[location, resource, scale_list] == sum(
            weight(scale_) * instance.R[location, resource, scale_[:scheduling_scale_level + 1]] for scale_ in scale_iter
            if scale_[:network_scale_level + 1] == scale_list)

    instance.constraint_location_revenue = Constraint(
        instance.locations, instance.resources_sell, *
        scales, rule=location_revenue_rule,
        doc='total revenue at location')
    constraint_latex_render(location_revenue_rule)
    return instance.constraint_location_revenue


def constraint_network_revenue(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Determines total revenue expenditure on resource across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_revenue
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def network_revenue_rule(instance, resource, *scale_list):
        return instance.R_network[resource, scale_list] == sum(
            instance.R_location[location_, resource, scale_list] for location_ in instance.locations)

    instance.constraint_network_revenue = Constraint(
        instance.resources_sell, *scales, rule=network_revenue_rule, doc='total revenue from network')
    constraint_latex_render(network_revenue_rule)
    return instance.constraint_network_revenue


# *-------------------------land costing constraints-----------------------------

def constraint_land_process_cost(instance: ConcreteModel, land_dict: dict, land_cost_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Land cost for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        land_dict (dict): land required at location
        land_cost_dict (dict): land cost at location
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: land_process
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def land_process_cost_rule(instance, location, process, *scale_list):
        return instance.Land_cost_process[location, process, scale_list] == land_cost_dict[location]*land_dict[process]*instance.Cap_P[location, process, scale_list]
    instance.constraint_land_process_cost = Constraint(
        instance.locations, instance.processes, *scales, rule=land_process_cost_rule, doc='land cost for process at location')
    constraint_latex_render(land_process_cost_rule)
    return instance.constraint_land_process_cost


def constraint_land_location_cost(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Land cost each location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: land_location_cost
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def land_location_cost_rule(instance, location, *scale_list):
        return instance.Land_cost_location[location, scale_list] == sum(instance.Land_cost_process[location, process_, scale_list] for process_ in instance.processes)
    instance.constraint_land_location_cost = Constraint(
        instance.locations, *scales, rule=land_location_cost_rule, doc='land cost at location')
    constraint_latex_render(land_location_cost_rule)
    return instance.constraint_land_location_cost


def constraint_land_network_cost(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Land cost by network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: land_network_cost
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def land_network_cost_rule(instance, *scale_list):
        return instance.Land_cost_network[scale_list] == sum(instance.Land_cost_location[location_, scale_list] for location_ in instance.locations)
    instance.constraint_land_network_cost = Constraint(
        *scales, rule=land_network_cost_rule, doc='land cost for process')
    constraint_latex_render(land_network_cost_rule)
    return instance.constraint_land_network_cost


# *-------------------------capex costing constraints----------------------------


def constraint_process_capex(instance: ConcreteModel, capex_dict: dict, network_scale_level: int = 0, annualization_factor: float = 1, capex_factor: dict = None, cost_dynamics: Costdynamics = Costdynamics.constant, location_process_dict: dict = None) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        capex_dict (dict): capex at location
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): Annual depreciation of asset. Defaults to 1.

    Returns:
        Constraint: process_capex
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def process_capex_rule(instance, location, process, *scale_list):
        if capex_dict[process] is not None:
            if capex_factor[location] is not None:
                if process in list(capex_factor[location].keys()):
                    return instance.Capex_process[location, process, scale_list] == annualization_factor*capex_factor[location][process][scale_list]*capex_dict[process]*instance.Cap_P[location, process, scale_list]
                else:
                    return instance.Capex_process[location, process, scale_list] == annualization_factor*capex_dict[process]*instance.Cap_P[location, process, scale_list]
            else:
                return instance.Capex_process[location, process, scale_list] == annualization_factor*capex_dict[process]*instance.Cap_P[location, process, scale_list]
        else:
            return instance.Capex_process[location, process, scale_list] == 0
    instance.constraint_process_capex = Constraint(
        instance.locations, instance.processes, *scales, rule=process_capex_rule, doc='capex for process')

    constraint_latex_render(process_capex_rule)
    return instance.constraint_process_capex


def constraint_location_capex(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_capex
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def location_capex_rule(instance, location, *scale_list):
        return instance.Capex_location[location, scale_list] == sum(instance.Capex_process[location, process_, scale_list] for process_ in instance.processes)
    instance.constraint_location_capex = Constraint(
        instance.locations, *scales, rule=location_capex_rule, doc='total location cost from network')
    constraint_latex_render(location_capex_rule)
    return instance.constraint_location_capex


def constraint_network_capex(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_capex
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_capex_rule(instance, *scale_list):
        return instance.Capex_network[scale_list] == sum(instance.Capex_location[location_, scale_list] for location_ in instance.locations)
    instance.constraint_network_capex = Constraint(
        *scales, rule=network_capex_rule, doc='total capex from network')
    constraint_latex_render(network_capex_rule)
    return instance.constraint_network_capex

# *-------------------------vopex costing constraints----------------------------


def constraint_process_vopex(instance: ConcreteModel, vopex_dict: dict, network_scale_level: int = 0, vopex_factor: dict = None, location_process_dict: dict = None) -> Constraint:
    """Fixed operational expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: process_vopex
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def process_vopex_rule(instance, location, process, *scale_list):
        if vopex_dict[process] is not None:
            if vopex_factor[location] is not None:
                return instance.Vopex_process[location, process, scale_list] == vopex_factor[location][process][scale_list]*vopex_dict[process]*instance.P_location[location, process, scale_list]
            else:
                return instance.Vopex_process[location, process, scale_list] == vopex_dict[process]*instance.P_location[location, process, scale_list]
        else:
            return instance.Vopex_process[location, process, scale_list] == 0
    instance.constraint_process_vopex = Constraint(
        instance.locations, instance.processes, *scales, rule=process_vopex_rule, doc='total vopex from network')
    constraint_latex_render(process_vopex_rule)
    return instance.constraint_process_vopex


def constraint_location_vopex(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Fixed operational expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_vopex
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def location_vopex_rule(instance, location, *scale_list):
        return instance.Vopex_location[location, scale_list] == sum(instance.Vopex_process[location, process_, scale_list] for process_ in instance.processes)
    instance.constraint_location_vopex = Constraint(
        instance.locations, *scales, rule=location_vopex_rule, doc='total vopex from location')
    constraint_latex_render(location_vopex_rule)
    return instance.constraint_location_vopex


def constraint_network_vopex(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Variable operational expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_vopex
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_vopex_rule(instance, *scale_list):
        return instance.Vopex_network[scale_list] == sum(instance.Vopex_location[location_, scale_list] for location_ in instance.locations)
    instance.constraint_network_vopex = Constraint(
        *scales, rule=network_vopex_rule, doc='total vopex from network')
    constraint_latex_render(network_vopex_rule)
    return instance.constraint_network_vopex


# *-------------------------fopex costing constraints----------------------------


def constraint_process_fopex(instance: ConcreteModel, fopex_dict: dict, network_scale_level: int = 0, fopex_factor: dict = None, annualization_factor: float = 1, location_process_dict: dict = None) -> Constraint:
    """Fixed operational expenditure for each process at location in network
    Args:
        instance (ConcreteModel): pyomo instance
        fopex_dict (dict): fixed opex at location
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): Annual depreciation of asset. Defaults to 1.

    Returns:
        Constraint: process_fopex
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def process_fopex_rule(instance, location, process, *scale_list):
        if fopex_dict[process] is not None:
            if fopex_factor[location] is not None:
                return instance.Fopex_process[location, process, scale_list] == annualization_factor*fopex_factor[location][process][scale_list]*fopex_dict[process]*instance.Cap_P[location, process, scale_list]
            else:
                return instance.Fopex_process[location, process, scale_list] == annualization_factor*fopex_dict[process]*instance.Cap_P[location, process, scale_list]
        else:
            return instance.Fopex_process[location, process, scale_list] == 0
    instance.constraint_process_fopex = Constraint(
        instance.locations, instance.processes, *scales, rule=process_fopex_rule, doc='fopex for process')
    constraint_latex_render(process_fopex_rule)
    return instance.constraint_process_fopex


def constraint_location_fopex(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Fixed operational expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_fopex
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def location_fopex_rule(instance, location, *scale_list):
        return instance.Fopex_location[location, scale_list] == sum(instance.Fopex_process[location, process_, scale_list] for process_ in instance.processes)
    instance.constraint_location_fopex = Constraint(
        instance.locations, *scales, rule=location_fopex_rule, doc='total fopex from network')
    constraint_latex_render(location_fopex_rule)
    return instance.constraint_location_fopex


def constraint_network_fopex(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Fixed operational for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_fopex
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_fopex_rule(instance, *scale_list):
        return instance.Fopex_network[scale_list] == sum(instance.Fopex_location[location_, scale_list] for location_ in instance.locations)
    instance.constraint_network_fopex = Constraint(
        *scales, rule=network_fopex_rule, doc='total fopex from network')
    constraint_latex_render(network_fopex_rule)
    return instance.constraint_network_fopex


# *-------------------------Transport costing constraints--------------------------

def constraint_transport_imp_cost(instance: ConcreteModel, scheduling_scale_level: int = 0, trans_cost: dict = None, distance_dict: dict = None) -> Constraint:
    """Calculates the expenditure on importing resource through transport

    Args:
        instance (ConcreteModel): pyomo instance
        scheduling_scale_level (int, optional): scheduling scale level. Defaults to 0.
        trans_cost (dict, optional): dictionary with transport costs. Defaults to None.
        distance_dict (dict, optional): dictionary with distances. Defaults to Non.

    Returns:
        Constraint: transport_imp_cost
    """
    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level+1)

    def transport_imp_cost_rule(instance, sink, source, resource, transport, *scale_list):
        if trans_cost is None:
            return Constraint.Skip
        else:
            if distance_dict is None:
                return Constraint.Skip
            else:
                return instance.Trans_imp_cost[sink, source, resource, transport, scale_list[:scheduling_scale_level+1]] == trans_cost[transport]*distance_dict[(source, sink)]*instance.Trans_imp[sink, source, resource, transport, scale_list[:scheduling_scale_level+1]]

    instance.constraint_transport_imp_cost = Constraint(instance.sinks, instance.sources, instance.resources_trans,
                                                        instance.transports, *scales, rule=transport_imp_cost_rule, doc='import of resource from sink to source')

    constraint_latex_render(transport_imp_cost_rule)
    return instance.constraint_transport_imp_cost


def constraint_transport_cost(instance: ConcreteModel, scheduling_scale_level: int = 0) -> Constraint:
    """Total cost for transport mode for all resources

    Args:
        instance (ConcreteModel): pyomo instance
        scheduling_scale_level (int, optional): scale for scheduling decisions. Defaults to 0.

    Returns:
        Constraint: transport_cost
    """
    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level+1)

    def transport_cost_rule(instance, transport, *scale_list):
        return instance.Trans_cost[transport, scale_list[:scheduling_scale_level+1]] == sum(instance.Trans_imp_cost[sink, source, resource, transport, scale_list[:scheduling_scale_level+1]]
                                                                                            for sink, source, resource in product(instance.sinks, instance.sources, instance.resources_trans))
    instance.constraint_transport_cost = Constraint(
        instance.transports, *scales, rule=transport_cost_rule, doc='total transport cost')
    constraint_latex_render(transport_cost_rule)
    return instance.constraint_transport_cost


def constraint_transport_cost_network(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Constraint for transport of all resources at network level

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: transport_cost_network
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=len(instance.scales))

    def transport_cost_network_rule(instance, transport, *scale_list):
        return instance.Trans_cost_network[transport, scale_list] == sum(instance.Trans_cost[transport, scale_] for scale_ in scale_iter)
    instance.constraint_transport_cost_network = Constraint(
        instance.transports, *scales, rule=transport_cost_network_rule, doc='total transport cost across scale')
    constraint_latex_render(transport_cost_network_rule)
    return instance.constraint_transport_cost_network


# *-------------------------Incidental costing constraints--------------------------

def constraint_process_incidental(instance: ConcreteModel, incidental_dict: dict, network_scale_level: int = 0, cost_dynamics: Costdynamics = Costdynamics.constant, location_process_dict: dict = None) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        incidental_dict (dict): incidental at location
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: process_incidental
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def process_incidental_rule(instance, location, process, *scale_list):
        if incidental_dict[process] is not None:
            return instance.Incidental_process[location, process, scale_list] == incidental_dict[process]
        else:
            return instance.Incidental_process[location, process, scale_list] == 0
    instance.constraint_process_incidental = Constraint(
        instance.locations, instance.processes, *scales, rule=process_incidental_rule, doc='total incidental costs from processes')

    constraint_latex_render(process_incidental_rule)
    return instance.constraint_process_incidental


def constraint_location_incidental(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_incidental
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def location_incidental_rule(instance, location, *scale_list):
        return instance.Incidental_location[location, scale_list] == sum(instance.Incidental_process[location, process_, scale_list] for process_ in instance.processes)
    instance.constraint_location_incidental = Constraint(
        instance.locations, *scales, rule=location_incidental_rule, doc='total incidental cost from network')
    constraint_latex_render(location_incidental_rule)
    return instance.constraint_location_incidental


def constraint_network_incidental(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_incidental
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_incidental_rule(instance, *scale_list):
        return instance.Incidental_network[scale_list] == sum(instance.Incidental_location[location_, scale_list] for location_ in instance.locations)
    instance.constraint_network_incidental = Constraint(
        *scales, rule=network_incidental_rule, doc='total incidental costs from network')
    constraint_latex_render(network_incidental_rule)
    return instance.constraint_network_incidental

# *-------------------------Total network cost--------------------------


def constraint_network_cost(instance: ConcreteModel, constraints=Set[Constraints], network_scale_level: int = 0) -> Constraint:
    """Total network costs

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: total network cost
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)

    def constraint_network_cost_rule(instance):
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
        return instance.Cost == capex + vopex + fopex + cost_purch + cost_trans + incidental + land_cost + credit

    instance.constraint_network_cost = Constraint(
        rule=constraint_network_cost_rule, doc='total network cost')
    constraint_latex_render(constraint_network_cost_rule)
    return instance.constraint_network_cost

# *-------------------------Inventory penalty --------------------------


def constraint_inventory_penalty(instance: ConcreteModel, location_resource_dict: dict, storage_penalty_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Inventory penalty incurred at the network scale

    Args:
        instance (ConcreteModel): pyomo instance
        location_resource_dict (dict): dictionary with resources available at locations.
        storage_penalty_dict (dict): dictionary with storage penalty at location.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: total network cost
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def inventory_penalty_rule(instance, location, resource, *scale_list):
        if resource in location_resource_dict[location]:
            return instance.Inv_penalty[location, resource, scale_list[:network_scale_level + 1]] == storage_penalty_dict[location][resource]*instance.Inv_network[location, resource, scale_list[:network_scale_level + 1]]
        else:
            return instance.Inv_penalty[location, resource, scale_list] == 0
    instance.constraint_inventory_penalty = Constraint(
        instance.locations, instance.resources_store, *
        scales, rule=inventory_penalty_rule,
        doc='penalty for stored resources')
    constraint_latex_render(inventory_penalty_rule)
    return instance.constraint_inventory_penalty


def constraint_inventory_penalty_location(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Inventory penalty incurred at the network scale across location

    Args:
        instance (ConcreteModel): pyomo instance

        storage_penalty_dict (dict): dictionary with storage penalty at location.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: total network cost
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def inventory_penalty_location_rule(instance, location, *scale_list):
        return instance.Inv_penalty_location[location, scale_list[:network_scale_level + 1]] == sum(instance.Inv_penalty[location, resource_, scale_list[:network_scale_level + 1]] for resource_ in instance.resources_store)
    instance.constraint_inventory_penalty_location = Constraint(
        instance.locations, *scales, rule=inventory_penalty_location_rule,
        doc='penalty for stored resources across location')
    constraint_latex_render(inventory_penalty_location_rule)
    return instance.constraint_inventory_penalty_location


def constraint_inventory_penalty_network(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Inventory penalty incurred at the network scale across network

    Args:
        instance (ConcreteModel): pyomo instance

        storage_penalty_dict (dict): dictionary with storage penalty at network.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: total network cost
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def inventory_penalty_network_rule(instance, *scale_list):
        return instance.Inv_penalty_network[scale_list[:network_scale_level + 1]] == sum(instance.Inv_penalty_location[location_, scale_list[:network_scale_level + 1]] for location_ in instance.locations)
    instance.constraint_inventory_penalty_network = Constraint(*scales, rule=inventory_penalty_network_rule,
                                                               doc='penalty for stored resources across network')
    constraint_latex_render(inventory_penalty_network_rule)
    return instance.constraint_inventory_penalty_network
