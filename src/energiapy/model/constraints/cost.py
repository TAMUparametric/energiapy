from enum import Enum, auto
from itertools import product
from typing import Set

from pyomo.environ import ConcreteModel, Constraint

from ...components.scenario import Scenario
from ...utils.data_utils import get_depth
from ...utils.scale_utils import scale_list, scale_tuple
from .constraints import Constraints


class Costdynamics(Enum):
    constant = auto()
    pwl = auto()
    scaled = auto()
    wind = auto()  # TODO allow user to give equation
    battery = auto()  # TODO allow user to give equation
    solar = auto()


# *-------------------------resource purchase costing constraint------------------

def constraint_total_purchase(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Determines total purchase expenditure

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: total_purchase
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)

    def total_purchase_rule(instance):
        return instance.B_total == sum(instance.B_network[resource_, scale_] for resource_, scale_ in
                                       product(instance.resources_purch, scale_iter))

    return Constraint(
        rule=total_purchase_rule, doc='calculates total purchase expenditure')


# *-------------------------revenue costing constraints--------------------------

def constraint_total_revenue(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Determines total revenue expenditure

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: total_revenue
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)

    def total_revenue_rule(instance):
        return instance.R_total == sum(instance.R_network[resource_, scale_] for resource_, scale_ in
                                       product(instance.resources_sell, scale_iter))

    return Constraint(rule=total_revenue_rule, doc='calculates total revenue earned')

# *-------------------------land costing constraints-----------------------------


def constraint_process_land_cost(instance: ConcreteModel, land_dict: dict, land_cost_dict: dict, network_scale_level: int = 0) -> Constraint:
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
    instance.constraint_process_land_cost = Constraint(
        instance.locations, instance.processes, *scales, rule=land_process_cost_rule, doc='land cost for process at location')
    return instance.constraint_process_land_cost

###


def constraint_location_land_cost(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
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
    instance.constraint_location_land_cost = Constraint(
        instance.locations, *scales, rule=land_location_cost_rule, doc='land cost at location')
    return instance.constraint_location_land_cost

###


def constraint_network_land_cost(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
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
    instance.constraint_network_land_cost = Constraint(
        *scales, rule=land_network_cost_rule, doc='land cost for process')
    return instance.constraint_network_land_cost


# *-------------------------capex costing constraints----------------------------


def constraint_process_capex(instance: ConcreteModel, capex_dict: dict, network_scale_level: int = 0, annualization_factor: float = 1, capex_factor: dict = None, cost_dynamics: Costdynamics = Costdynamics.constant, location_process_dict: dict = None) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        capex_dict (dict): capex at location
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): Annualization of capital investment. Defaults to 1.

    Returns:
        Constraint: process_capex
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def process_capex_rule(instance, location, process, *scale_list):

        if capex_dict[process] is not None:
            Cap_P = instance.Cap_P[location, process, scale_list]
        else:
            Cap_P = 0
        capex_fact = 1
        if capex_factor is not None:
            if capex_factor[location] is not None:
                if process in list(capex_factor[location].keys()):
                    capex_fact = capex_factor[location][process][scale_list]

        if get_depth(capex_dict) == 1:
            return instance.Capex_process[location, process, scale_list] == annualization_factor*capex_fact*capex_dict[process]*Cap_P
        else:
            if hasattr(instance, 'X_M') is True:
                return instance.Capex_process[location, process, scale_list] == sum(annualization_factor*capex_fact*capex_dict[i[0]][i[1]]*instance.Cap_P_M[location, i[0], i[1], scale_list] for i in instance.process_material_modes if i[0] == process)
            if hasattr(instance, 'X_P_m') is True:
                return instance.Capex_process[location, process, scale_list] == sum(annualization_factor*capex_fact*capex_dict[i[0]][i[1]]*Cap_P for i in instance.process_material_modes if i[0] == process)
    instance.constraint_process_capex = Constraint(
        instance.locations, instance.processes, *scales, rule=process_capex_rule, doc='capex for process')
    return instance.constraint_process_capex

# *-------------------------vopex costing constraints----------------------------


def constraint_process_vopex(instance: ConcreteModel, vopex_dict: dict, network_scale_level: int = 0, vopex_factor: dict = None, cost_dynamics: Costdynamics = Costdynamics.constant, location_process_dict: dict = None) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        vopex_dict (dict): vopex at location
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: process_vopex
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def process_vopex_rule(instance, location, process, *scale_list):

        if vopex_dict[process] is not None:
            P_location = instance.P_location[location, process, scale_list]
        else:
            P_location = 0

        vopex_fact = 1
        if vopex_factor is not None:
            if vopex_factor[location] is not None:
                if process in list(vopex_factor[location].keys()):
                    vopex_fact = vopex_factor[location][process][scale_list]

        if get_depth(vopex_dict) == 1:
            return instance.Vopex_process[location, process, scale_list] == vopex_fact*vopex_dict[process]*P_location
        else:
            if hasattr(instance, 'X_M') is True:
                return instance.Vopex_process[location, process, scale_list] == sum(vopex_fact*vopex_dict[i[0]][i[1]]*instance.P_location_material_m[location, i[0], i[1], scale_list] for i in instance.process_material_modes if i[0] == process)
            if hasattr(instance, 'X_P_m') is True:
                return instance.Vopex_process[location, process, scale_list] == sum(vopex_fact*vopex_dict[i[0]][i[1]]*P_location for i in instance.process_material_modes if i[0] == process)
    instance.constraint_process_vopex = Constraint(
        instance.locations, instance.processes, *scales, rule=process_vopex_rule, doc='vopex for process')
    return instance.constraint_process_vopex


# *-------------------------fopex costing constraints----------------------------


def constraint_process_fopex(instance: ConcreteModel, fopex_dict: dict, network_scale_level: int = 0, fopex_factor: dict = None, cost_dynamics: Costdynamics = Costdynamics.constant, location_process_dict: dict = None) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        fopex_dict (dict): fopex at location
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: process_fopex
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def process_fopex_rule(instance, location, process, *scale_list):

        if fopex_dict[process] is not None:
            Cap_P = instance.Cap_P[location, process, scale_list]
        else:
            Cap_P = 0
        fopex_fact = 1
        if fopex_factor is not None:
            if fopex_factor[location] is not None:
                if process in list(fopex_factor[location].keys()):
                    fopex_fact = fopex_factor[location][process][scale_list]

        if get_depth(fopex_dict) == 1:
            return instance.Fopex_process[location, process, scale_list] == fopex_fact*fopex_dict[process]*Cap_P
        else:
            if hasattr(instance, 'X_M') is True:
                return instance.Fopex_process[location, process, scale_list] == sum(fopex_fact*fopex_dict[i[0]][i[1]]*instance.Cap_P_M[location, i[0], i[1], scale_list] for i in instance.process_material_modes if i[0] == process)
            if hasattr(instance, 'X_P_m') is True:
                return instance.Fopex_process[location, process, scale_list] == sum(fopex_fact*fopex_dict[i[0]][i[1]]*Cap_P for i in instance.process_material_modes if i[0] == process)
    instance.constraint_process_fopex = Constraint(
        instance.locations, instance.processes, *scales, rule=process_fopex_rule, doc='fopex for process')
    return instance.constraint_process_fopex


# *-------------------------Incidental costing constraints--------------------------

def constraint_process_incidental(instance: ConcreteModel, incidental_dict: dict, network_scale_level: int = 0, incidental_factor: dict = None, cost_dynamics: Costdynamics = Costdynamics.constant, location_process_dict: dict = None) -> Constraint:
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
    return instance.constraint_process_incidental

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
    return instance.constraint_transport_cost_network


# *-------------------------Inventory penalty --------------------------


def constraint_storage_cost(instance: ConcreteModel, location_resource_dict: dict, storage_cost: dict, network_scale_level: int = 0) -> Constraint:
    """Inventory penalty incurred at the network scale

    Args:
        instance (ConcreteModel): pyomo instance
        location_resource_dict (dict): dictionary with resources available at locations.
        storage_cost (dict): dictionary with storage penalty at location.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: total network cost
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def storage_cost_rule(instance, location, resource, *scale_list):
        if resource in location_resource_dict[location]:
            if resource in storage_cost[location]:
                return instance.Inv_cost_resource[location, resource, scale_list[:network_scale_level + 1]] == storage_cost[location][resource]*instance.Inv_network[location, resource, scale_list[:network_scale_level + 1]]
            else:
                return instance.Inv_cost_resource[location, resource, scale_list[:network_scale_level + 1]] == 0
        else:
            return instance.Inv_cost_resource[location, resource, scale_list] == 0
    instance.constraint_storage_cost = Constraint(
        instance.locations, instance.resources_store, *
        scales, rule=storage_cost_rule,
        doc='penalty for stored resources')
    return instance.constraint_storage_cost


def constraint_location_storage_cost(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Inventory penalty incurred at the network scale across location

    Args:
        instance (ConcreteModel): pyomo instance

        storage_cost (dict): dictionary with storage penalty at location.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: total network cost
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def storage_cost_location_rule(instance, location, *scale_list):
        return instance.Inv_cost_location[location, scale_list[:network_scale_level + 1]] == sum(instance.Inv_cost_resource[location, resource_, scale_list[:network_scale_level + 1]] for resource_ in instance.resources_store)
    instance.constraint_location_storage_cost = Constraint(
        instance.locations, *scales, rule=storage_cost_location_rule,
        doc='penalty for stored resources across location')
    return instance.constraint_location_storage_cost


def constraint_network_storage_cost(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Inventory penalty incurred at the network scale across network

    Args:
        instance (ConcreteModel): pyomo instance

        storage_cost (dict): dictionary with storage penalty at network.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: total network cost
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def storage_cost_network_rule(instance, *scale_list):
        return instance.Inv_cost_network[scale_list[:network_scale_level + 1]] == sum(instance.Inv_cost_location[location_, scale_list[:network_scale_level + 1]] for location_ in instance.locations)
    instance.constraint_network_storage_cost = Constraint(*scales, rule=storage_cost_network_rule,
                                                          doc='penalty for stored resources across network')
    return instance.constraint_network_storage_cost


# *-------------------------Total network cost--------------------------


def constraint_total_cost(instance: ConcreteModel, constraints: Set[Constraints], scenario: Scenario) -> Constraint:
    """Total cost

    Args:
        instance (ConcreteModel): pyomo instance
        constraints (Set[Constraints]): list of constraint blocks to consider
        scenario (Scenario): self explanatory
    Returns:
        Constraint: total cost
    """
    def constraint_total_cost_rule(instance):
        if scenario.consider_capex is True:
            capex = instance.Capex_total
        else:
            capex = 0

        if scenario.consider_fopex is True:
            fopex = instance.Fopex_total
        else:
            fopex = 0

        if scenario.consider_vopex is True:
            vopex = instance.Vopex_total
        else:
            vopex = 0

        if scenario.consider_incidental is True:
            incidental = instance.Incidental_total
        else:
            incidental = 0

        cost_purch = instance.B_total

        if scenario.consider_storage_cost is True:
            storage_cost = instance.Inv_cost_total
        else:
            storage_cost = 0

        if Constraints.LAND in constraints:
            land_cost = instance.Land_cost_total
        else:
            land_cost = 0

        if Constraints.CREDIT in constraints:
            credit = instance.Credit_total
        else:
            credit = 0

        if len(instance.locations) > 1:
            cost_trans_capex = instance.Capex_transport_total
            cost_trans_vopex = instance.Vopex_transport_total
            cost_trans_fopex = instance.Fopex_transport_total
        else:
            cost_trans_capex = 0
            cost_trans_vopex = 0
            cost_trans_fopex = 0

        return instance.Cost_total == capex + cost_trans_capex + vopex + fopex + cost_purch + cost_trans_vopex + cost_trans_fopex + incidental + land_cost - credit + storage_cost

    instance.constraint_total_cost = Constraint(
        rule=constraint_total_cost_rule, doc='total network cost')
    return instance.constraint_total_cost
