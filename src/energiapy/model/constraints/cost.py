"""pyomo cost constraints
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


class Costdynamics(Enum):
    constant = auto()
    pwl = auto()
    scaled = auto()
    wind = auto () #TODO allow user to give equation
    battery = auto () #TODO allow user to give equation
    solar = auto()


def transport_exp_cost_constraint(instance: ConcreteModel, scheduling_scale_level: int = 0, trans_cost: dict = {}, distance_dict: dict = {}) -> Constraint:
    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level+1)

    def transport_exp_cost_rule(instance, source, sink, resource, transport, *scale_list):
        return instance.Trans_exp_cost[source, sink, resource, transport, scale_list[:scheduling_scale_level+1]] == \
            trans_cost[transport]*distance_dict[(source, sink)]*instance.Trans_exp[source,
                                                                                   sink, resource, transport, scale_list[:scheduling_scale_level+1]]
    instance.transport_exp_cost_constraint = Constraint(instance.sources, instance.sinks, instance.resources_trans,
                                                        instance.transports, *scales, rule=transport_exp_cost_rule, doc='import of resource from sink to source')
    constraint_latex_render(transport_exp_cost_rule)
    return instance.transport_exp_cost_constraint


def transport_imp_cost_constraint(instance: ConcreteModel, scheduling_scale_level: int = 0, trans_cost: dict = {}, distance_dict: dict = {}) -> Constraint:
    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level+1)

    def transport_imp_cost_rule(instance, sink, source, resource, transport, *scale_list):
        return instance.Trans_imp_cost[sink, source, resource, transport, scale_list[:scheduling_scale_level+1]] == \
            trans_cost[transport]*distance_dict[(source, sink)]*instance.Trans_imp[sink,
                                                                                   source, resource, transport, scale_list[:scheduling_scale_level+1]]
    instance.transport_imp_cost_constraint = Constraint(instance.sinks, instance.sources, instance.resources_trans,
                                                        instance.transports, *scales, rule=transport_imp_cost_rule, doc='import of resource from sink to source')
    constraint_latex_render(transport_imp_cost_rule)
    return instance.transport_imp_cost_constraint

# *-------------------------Transport costing constraints--------------------------


def transport_cost_constraint(instance: ConcreteModel, scheduling_scale_level: int = 0):
    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level+1)

    def transport_cost_rule(instance, transport, *scale_list):
        return instance.Trans_cost[transport, scale_list[:scheduling_scale_level+1]] == \
            sum(instance.Trans_imp_cost[sink, source, resource, transport, scale_list[:scheduling_scale_level+1]] +
                instance.Trans_exp_cost[source, sink, resource,
                                        transport, scale_list[:scheduling_scale_level+1]]
                for sink, source, resource in product(instance.sinks, instance.sources, instance.resources_trans))
    instance.transport_cost_constraint = Constraint(
        instance.transports, *scales, rule=transport_cost_rule, doc='total transport cost')
    constraint_latex_render(transport_cost_rule)
    return instance.transport_cost_constraint


def transport_cost_network_constraint(instance: ConcreteModel, network_scale_level: int = 0):
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=instance.scales.__len__())

    def transport_cost_network_rule(instance, transport, *scale_list):
        return instance.Trans_cost_network[transport, scale_list] == sum(instance.Trans_cost[transport, scale_] for scale_ in scale_iter)
    instance.transport_cost_network_constraint = Constraint(
        instance.transports, *scales, rule=transport_cost_network_rule, doc='total transport cost across scale')
    constraint_latex_render(transport_cost_network_rule)
    return instance.transport_cost_network_constraint


def process_capex_constraint(instance: ConcreteModel, capex_dict: dict, network_scale_level: int = 0, annualization_factor: float = 1,\
    cost_dynamics: Costdynamics = Costdynamics.constant) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        capex_dict (dict): capex at location #TODO
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): Annual depreciation of asset. Defaults to 1.

    Returns:
        Constraint: process_capex_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)
    
    def process_capex_rule(instance, location, process, *scale_list):
        if capex_dict[process] is not None:
            return instance.Capex_process[location, process, scale_list] == annualization_factor*capex_dict[process]*instance.Cap_P[location, process, scale_list]
        else:
            return instance.Capex_process[location, process, scale_list] == 0
    instance.process_capex_constraint = Constraint(
        instance.locations, instance.processes, *scales, rule=process_capex_rule, doc='total purchase from network')
    
    constraint_latex_render(process_capex_rule)
    return instance.process_capex_constraint

def process_incidental_constraint(instance: ConcreteModel, incidental_dict: dict, network_scale_level: int = 0, annualization_factor: float = 1,\
    cost_dynamics: Costdynamics = Costdynamics.constant) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        capex_dict (dict): capex at location #TODO
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): Annual depreciation of asset. Defaults to 1.

    Returns:
        Constraint: process_capex_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)
    
    def process_incidental_rule(instance, location, process, *scale_list):
        if incidental_dict[process] is not None:
            return instance.Incidental_process[location, process, scale_list] ==incidental_dict[process]
        else:
            return instance.Incidental_process[location, process, scale_list] == 0
    instance.process_incidental_constraint = Constraint(
        instance.locations, instance.processes, *scales, rule=process_incidental_rule, doc='total incidental costs from processes')
    
    constraint_latex_render(process_incidental_rule)
    return instance.process_incidental_constraint


def process_fopex_constraint(instance: ConcreteModel, fopex_dict: dict, network_scale_level: int = 0, annualization_factor: float = 1) -> Constraint:
    """Fixed operational expenditure for each process at location in network
    Args:
        instance (ConcreteModel): pyomo instance
        fopex_dict (dict): fixed opex at location #TODO
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): Annual depreciation of asset. Defaults to 1.

    Returns:
        Constraint: process_fopex_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def process_fopex_rule(instance, location, process, *scale_list):
        if fopex_dict[process] is not None:
            return instance.Fopex_process[location, process, scale_list] == annualization_factor*fopex_dict[process]*instance.Cap_P[location, process, scale_list]
        else:
            return instance.Fopex_process[location, process, scale_list] == 0 
    instance.process_fopex_constraint = Constraint(
        instance.locations, instance.processes, *scales, rule=process_fopex_rule, doc='total purchase from network')
    constraint_latex_render(process_fopex_rule)
    return instance.process_fopex_constraint


def process_vopex_constraint(instance: ConcreteModel, vopex_dict: dict, network_scale_level: int = 0, annualization_factor: float = 1) -> Constraint:
    """Fixed operational expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: process_vopex_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def process_vopex_rule(instance, location, process, *scale_list):
        if vopex_dict[process] is not None:
            return instance.Vopex_process[location, process, scale_list] == annualization_factor*vopex_dict[process]*instance.P_location[location, process, scale_list]
        else:
            return instance.Vopex_process[location, process, scale_list] == 0
    instance.process_vopex_constraint = Constraint(
        instance.locations, instance.processes, *scales, rule=process_vopex_rule, doc='total purchase from network')
    constraint_latex_render(process_vopex_rule)
    return instance.process_vopex_constraint


# *-------------------------Location costing constraints--------------------------------------

def location_capex_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_capex_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def location_capex_rule(instance, location, *scale_list):
        return instance.Capex_location[location, scale_list] == sum(instance.Capex_process[location, process_, scale_list] for process_ in instance.processes)
    instance.location_capex_constraint = Constraint(
        instance.locations, *scales, rule=location_capex_rule, doc='total purchase from network')
    constraint_latex_render(location_capex_rule)
    return instance.location_capex_constraint

def location_incidental_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_incidental_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def location_incidental_rule(instance, location, *scale_list):
        return instance.Incidental_location[location, scale_list] == sum(instance.Incidental_process[location, process_, scale_list] for process_ in instance.processes)
    instance.location_incidental_constraint = Constraint(
        instance.locations, *scales, rule=location_incidental_rule, doc='total purchase from network')
    constraint_latex_render(location_incidental_rule)
    return instance.location_incidental_constraint

def location_fopex_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Fixed operational expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_fopex_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def location_fopex_rule(instance, location, *scale_list):
        return instance.Fopex_location[location, scale_list] == sum(instance.Fopex_process[location, process_, scale_list] for process_ in instance.processes)
    instance.location_fopex_constraint = Constraint(
        instance.locations, *scales, rule=location_fopex_rule, doc='total purchase from network')
    constraint_latex_render(location_fopex_rule)
    return instance.location_fopex_constraint


def location_vopex_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Fixed operational expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_vopex_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def location_vopex_rule(instance, location, *scale_list):
        return instance.Vopex_location[location, scale_list] == sum(instance.Vopex_process[location, process_, scale_list] for process_ in instance.processes)
    instance.location_vopex_constraint = Constraint(
        instance.locations, *scales, rule=location_vopex_rule, doc='total purchase from network')
    constraint_latex_render(location_vopex_rule)
    return instance.location_vopex_constraint


# *-------------------------Network costing constraints--------------------------------------

def network_capex_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_capex_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_capex_rule(instance, *scale_list):
        return instance.Capex_network[scale_list] == sum(instance.Capex_location[location_, scale_list] for location_ in instance.locations)
    instance.network_capex_constraint = Constraint(
        *scales, rule=network_capex_rule, doc='total purchase from network')
    constraint_latex_render(network_capex_rule)
    return instance.network_capex_constraint


def network_incidental_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_incidental_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_incidental_rule(instance, *scale_list):
        return instance.Incidental_network[scale_list] == sum(instance.Incidental_location[location_, scale_list] for location_ in instance.locations)
    instance.network_incidental_constraint = Constraint(
        *scales, rule=network_incidental_rule, doc='total purchase from network')
    constraint_latex_render(network_incidental_rule)
    return instance.network_incidental_constraint


def network_vopex_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Variable operational expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_vopex_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_vopex_rule(instance, *scale_list):
        return instance.Vopex_network[scale_list] == sum(instance.Vopex_location[location_, scale_list] for location_ in instance.locations)
    instance.network_vopex_constraint = Constraint(
        *scales, rule=network_vopex_rule, doc='total purchase from network')
    constraint_latex_render(network_vopex_rule)
    return instance.network_vopex_constraint


def network_fopex_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Fixed operational for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_fopex_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_fopex_rule(instance, *scale_list):
        return instance.Fopex_network[scale_list] == sum(instance.Fopex_location[location_, scale_list] for location_ in instance.locations)
    instance.network_fopex_constraint = Constraint(
        *scales, rule=network_fopex_rule, doc='total purchase from network')
    constraint_latex_render(network_fopex_rule)
    return instance.network_fopex_constraint


def process_land_cost_constraint(instance: ConcreteModel, land_dict: dict, land_cost_dict:dict, network_scale_level: int = 0) -> Constraint:
    """Land cost for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        land_dict (dict): land required at location
        land_cost_dict (dict): land cost at location
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: process_land_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def process_land_cost_rule(instance, location, process, *scale_list):
        return instance.Land_cost_process[location, process, scale_list] == land_cost_dict[location]*land_dict[process]*instance.Cap_P[location, process, scale_list]
    instance.process_land_cost_constraint = Constraint(
        instance.locations, instance.processes, *scales, rule=process_land_cost_rule, doc='land cost for process at location')
    constraint_latex_render(process_land_cost_rule)
    return instance.process_land_cost_constraint



def location_land_cost_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Land cost each location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_land_cost_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def location_land_cost_rule(instance, location, *scale_list):
        return instance.Land_cost_location[location, scale_list] == sum(instance.Land_cost_process[location, process_, scale_list] for process_ in instance.processes)
    instance.location_land_cost_constraint = Constraint(
        instance.locations, *scales, rule=location_land_cost_rule, doc='land cost at location')
    constraint_latex_render(location_land_cost_rule)
    return instance.location_land_cost_constraint



def network_land_cost_constraint(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Land cost by network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_land_cost_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def network_land_cost_rule(instance, *scale_list):
        return instance.Land_cost_network[scale_list] == sum(instance.Land_cost_location[location_, scale_list] for location_ in instance.locations)
    instance.network_land_cost_constraint = Constraint(
        *scales, rule=network_land_cost_rule, doc='land cost for process')
    constraint_latex_render(network_land_cost_rule)
    return instance.network_land_cost_constraint