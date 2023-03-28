"""pyomo cost constraints
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

from pyomo.environ import ConcreteModel, Constraint

from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list, scale_tuple


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


def constraint_transport_imp_cost(instance: ConcreteModel, scheduling_scale_level: int = 0, trans_cost: dict = None, distance_dict: dict = None) -> Constraint:
    """Calculates the expenditure on importing resource throught transport

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

        if distance_dict is None:
            return Constraint.Skip

        return instance.Trans_imp_cost[sink, source, resource, transport, scale_list[:scheduling_scale_level+1]] == trans_cost[transport]*distance_dict[(source, sink)]*instance.Trans_imp[sink, source, resource, transport, scale_list[:scheduling_scale_level+1]]

    instance.constraint_transport_imp_cost = Constraint(instance.sinks, instance.sources, instance.resources_trans,
                                                        instance.transports, *scales, rule=transport_imp_cost_rule, doc='import of resource from sink to source')

    constraint_latex_render(transport_imp_cost_rule)
    return instance.constraint_transport_imp_cost

# *-------------------------Transport costing constraints--------------------------


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
        instance=instance, scale_levels=instance.scales.__len__())

    def transport_cost_network_rule(instance, transport, *scale_list):
        return instance.Trans_cost_network[transport, scale_list] == sum(instance.Trans_cost[transport, scale_] for scale_ in scale_iter)
    instance.constraint_transport_cost_network = Constraint(
        instance.transports, *scales, rule=transport_cost_network_rule, doc='total transport cost across scale')
    constraint_latex_render(transport_cost_network_rule)
    return instance.constraint_transport_cost_network


def constraint_process_capex(instance: ConcreteModel, capex_dict: dict, network_scale_level: int = 0, annualization_factor: float = 1, cost_dynamics: Costdynamics = Costdynamics.constant) -> Constraint:
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
            return instance.Capex_process[location, process, scale_list] == annualization_factor*capex_dict[process]*instance.Cap_P[location, process, scale_list]
        else:
            return instance.Capex_process[location, process, scale_list] == 0
    instance.constraint_process_capex = Constraint(
        instance.locations, instance.processes, *scales, rule=process_capex_rule, doc='total purchase from network')

    constraint_latex_render(process_capex_rule)
    return instance.constraint_process_capex


def constraint_process_incidental(instance: ConcreteModel, incidental_dict: dict, network_scale_level: int = 0, annualization_factor: float = 1, cost_dynamics: Costdynamics = Costdynamics.constant) -> Constraint:
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

    def process_incidental_rule(instance, location, process, *scale_list):
        if incidental_dict[process] is not None:
            return instance.Incidental_process[location, process, scale_list] == incidental_dict[process]
        else:
            return instance.Incidental_process[location, process, scale_list] == 0
    instance.constraint_process_incidental = Constraint(
        instance.locations, instance.processes, *scales, rule=process_incidental_rule, doc='total incidental costs from processes')

    constraint_latex_render(process_incidental_rule)
    return instance.constraint_process_incidental


def constraint_process_fopex(instance: ConcreteModel, fopex_dict: dict, network_scale_level: int = 0, annualization_factor: float = 1) -> Constraint:
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
            return instance.Fopex_process[location, process, scale_list] == annualization_factor*fopex_dict[process]*instance.Cap_P[location, process, scale_list]
        else:
            return instance.Fopex_process[location, process, scale_list] == 0
    instance.constraint_process_fopex = Constraint(
        instance.locations, instance.processes, *scales, rule=process_fopex_rule, doc='total purchase from network')
    constraint_latex_render(process_fopex_rule)
    return instance.constraint_process_fopex


def constraint_process_vopex(instance: ConcreteModel, vopex_dict: dict, network_scale_level: int = 0, annualization_factor: float = 1) -> Constraint:
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
            return instance.Vopex_process[location, process, scale_list] == annualization_factor*vopex_dict[process]*instance.P_location[location, process, scale_list]
        else:
            return instance.Vopex_process[location, process, scale_list] == 0
    instance.constraint_process_vopex = Constraint(
        instance.locations, instance.processes, *scales, rule=process_vopex_rule, doc='total purchase from network')
    constraint_latex_render(process_vopex_rule)
    return instance.constraint_process_vopex


# *-------------------------Location costing constraints--------------------------------------

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
        instance.locations, *scales, rule=location_capex_rule, doc='total purchase from network')
    constraint_latex_render(location_capex_rule)
    return instance.constraint_location_capex


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
        instance.locations, *scales, rule=location_incidental_rule, doc='total purchase from network')
    constraint_latex_render(location_incidental_rule)
    return instance.constraint_location_incidental


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
        instance.locations, *scales, rule=location_fopex_rule, doc='total purchase from network')
    constraint_latex_render(location_fopex_rule)
    return instance.constraint_location_fopex


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
        instance.locations, *scales, rule=location_vopex_rule, doc='total purchase from network')
    constraint_latex_render(location_vopex_rule)
    return instance.constraint_location_vopex


# *-------------------------Network costing constraints--------------------------------------

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
        *scales, rule=network_capex_rule, doc='total purchase from network')
    constraint_latex_render(network_capex_rule)
    return instance.constraint_network_capex


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
        *scales, rule=network_incidental_rule, doc='total purchase from network')
    constraint_latex_render(network_incidental_rule)
    return instance.constraint_network_incidental


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
        *scales, rule=network_vopex_rule, doc='total purchase from network')
    constraint_latex_render(network_vopex_rule)
    return instance.constraint_network_vopex


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
        *scales, rule=network_fopex_rule, doc='total purchase from network')
    constraint_latex_render(network_fopex_rule)
    return instance.constraint_network_fopex


def constraint_process_land_cost(instance: ConcreteModel, land_dict: dict, land_cost_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Land cost for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        land_dict (dict): land required at location
        land_cost_dict (dict): land cost at location
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: process_land
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def process_land_cost_rule(instance, location, process, *scale_list):
        return instance.Land_cost_process[location, process, scale_list] == land_cost_dict[location]*land_dict[process]*instance.Cap_P[location, process, scale_list]
    instance.constraint_process_land_cost = Constraint(
        instance.locations, instance.processes, *scales, rule=process_land_cost_rule, doc='land cost for process at location')
    constraint_latex_render(process_land_cost_rule)
    return instance.constraint_process_land_cost


def constraint_location_land_cost(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Land cost each location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_land_cost
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def location_land_cost_rule(instance, location, *scale_list):
        return instance.Land_cost_location[location, scale_list] == sum(instance.Land_cost_process[location, process_, scale_list] for process_ in instance.processes)
    instance.constraint_location_land_cost = Constraint(
        instance.locations, *scales, rule=location_land_cost_rule, doc='land cost at location')
    constraint_latex_render(location_land_cost_rule)
    return instance.constraint_location_land_cost


def constraint_network_land_cost(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Land cost by network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_land_cost
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_land_cost_rule(instance, *scale_list):
        return instance.Land_cost_network[scale_list] == sum(instance.Land_cost_location[location_, scale_list] for location_ in instance.locations)
    instance.constraint_network_land_cost = Constraint(
        *scales, rule=network_land_cost_rule, doc='land cost for process')
    constraint_latex_render(network_land_cost_rule)
    return instance.constraint_network_land_cost
