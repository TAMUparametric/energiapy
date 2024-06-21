from typing import Dict, Tuple, Union

from pyomo.environ import ConcreteModel, Constraint

from ...components.location import Location
from ...components.process import Process
from ...components.resource import Resource
from ...utils.scale_utils import scale_list, scale_tuple


def constraint_inventory_balance(instance: ConcreteModel, scheduling_scale_level: int = 0,
                                 multiconversion: dict = None, mode_dict: dict = None,
                                 cluster_wt: dict = None, inventory_zero: Dict[Location, Dict[Tuple[Process, Resource], float]] = None,
                                 location_resource_dict: dict = None, location_process_dict: dict = None, location_resource_sell_dict: dict = None, location_resource_purch_dict: dict = None, location_resource_store_dict: dict = None) -> Constraint:
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
        inventory_zero (Dict[Location, Dict[Tuple[Process, Resource], float]], optional): inventory at the start of the scheduling horizon. Defaults to None.
        location_resource_dict (dict, optional): dict with resources in locations. Defaults to None.
        location_process_dict (dict, optional): dict with processes in locations. Defaults to None.
        location_resources_sell_dict (dict, optional): dict with resources in locations which can be sold. Defaults to None.
        location_resources_purch_dict (dict, optional): dict with resources in locations which can be purchased/consumed. Defaults to None.
        location_resources_store_dict (dict, optional): dict with resources in locations which can be stored. Defaults to None.

    Returns:
        Constraint: inventory_balance
    """

    if multiconversion is None:
        multiconversion = dict()

    if mode_dict is None:
        mode_dict = dict()

    if inventory_zero is None:
        inventory_zero = {j: {i: 0 for i in instance.resources_store}
                          for j in instance.locations}

    else:
        inventory_zero = {j.name: {(i[0].name, i[1].name): inventory_zero[j][i] for i in inventory_zero[j].keys(
        )} for j in inventory_zero.keys()}

        inventory_zero = {i: {f"{j[0]}_{j[1]}_stored": inventory_zero[i][(
            j[0], j[1])] for j in inventory_zero[i]} for i in inventory_zero.keys()}

        inventory_zero = {i: {
            j: inventory_zero[i][j] if j in inventory_zero[i].keys() else 0 for j in instance.resources_store} for i in inventory_zero.keys()}

    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level + 1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level + 1)

    def inventory_balance_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_purch:
            if resource in location_resource_purch_dict[location]:
                consumption = instance.C[location, resource,
                                         scale_list[:scheduling_scale_level + 1]]
            else:
                consumption = 0
        else:
            consumption = 0

        if resource in instance.resources_store:
            if resource in location_resource_store_dict[location]:
                if scale_list[:scheduling_scale_level + 1] != scale_iter[0]:
                    storage = instance.Inv[location, resource, scale_list[:scheduling_scale_level + 1]] \
                        - instance.Inv[location, resource, scale_iter[scale_iter.index(
                            scale_list[:scheduling_scale_level + 1]) - 1]]
                else:
                    storage = instance.Inv[location, resource,
                                           scale_list[:scheduling_scale_level + 1]] - inventory_zero[location][resource]
            else:
                storage = 0
        else:
            storage = 0

        if resource in instance.resources_sell:
            if resource in location_resource_sell_dict[location]:
                discharge = instance.S[location, resource,
                                       scale_list[:scheduling_scale_level + 1]]
            else:
                discharge = 0
        else:
            discharge = 0

        if len(instance.locations) > 1:
            if resource in instance.resources_trans:
                if resource in location_resource_dict[location]:
                    transport = sum(
                        instance.Exp_R[source_, location, resource, scale_list[:scheduling_scale_level + 1]] for source_ in
                        instance.sources if source_ != location if location in instance.sinks) \
                        - sum(
                        instance.Exp_R[location, sink_, resource, scale_list[:scheduling_scale_level + 1]] for sink_ in
                        instance.sinks if sink_ != location if location in instance.sources)
                else:
                    transport = 0
            else:
                transport = 0
        else:
            transport = 0

        # produced = sum(conversion[process][resource]*instance.P[location, process, scale_list[:scheduling_scale_level+1]] for process in instance.processes_singlem) \
        #     + sum(instance.P[location, process, scale_list[:scheduling_scale_level+1]] for process in instance.processes_multim)

        # produced = sum(sum(multiconversion[process][mode][resource] * instance.P_m[location, process, mode,
        #                                                                            scale_list[:scheduling_scale_level + 1]] for mode in mode_dict[process]) for process in
        #                instance.processes_full if process in location_process_dict[location])  # includes processes + discharge
        produced = 0
        for process in instance.processes_full:
            if process in location_process_dict[location]:
                for mode in mode_dict[process]:
                    if multiconversion[process][mode][resource]:
                        produced = produced + multiconversion[process][mode][resource] * instance.P_m[location, process, mode,
                                                                                                      scale_list[:scheduling_scale_level + 1]]
                    else:
                        produced = produced + 0

        def weight(x): return 1 if cluster_wt is None else cluster_wt[x]

        if isinstance(produced, int):
            if produced == 0:  # slightly unecessary
                return Constraint.Skip

        else:
            return weight(scale_list[:scheduling_scale_level + 1]) * (
                consumption + produced - discharge + transport) == storage

    instance.constraint_inventory_balance = Constraint(
        instance.locations, instance.resources, *scales, rule=inventory_balance_rule,
        doc='mass balance across scheduling scale')
    return instance.constraint_inventory_balance


def constraint_location_production_material_mode_sum(instance: ConcreteModel, process_material_mode_material_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Determines total production capacity utilization at location

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
    Returns:
        Constraint: location_production_material_mode_sum
    """

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def location_production_material_mode_sum_rule(instance, location, process, *scale_list):
        return instance.P_location[location, process, scale_list] == sum(
            instance.P_location_material_m[location, process, material_mode_, scale_list] for material_mode_ in instance.material_modes if material_mode_ in process_material_mode_material_dict[process].keys())

    instance.constraint_location_production_material_mode_sum = Constraint(
        instance.locations, instance.processes, *
        scales, rule=location_production_material_mode_sum_rule,
        doc='total production at location')
    return instance.constraint_location_production_material_mode_sum


def constraint_location_production_material_mode(instance: ConcreteModel, cluster_wt: dict,
                                                 network_scale_level: int = 0, scheduling_scale_level: int = 0) -> Constraint:
    """Determines total production capacity utilization at location

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
    Returns:
        Constraint: location_production_material_mode
    """

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level+1)

    def location_production_material_mode_rule(instance, location, process, material_mode,  *scale_list):
        def weight(x): return 1 if cluster_wt is None else cluster_wt[x]
        return instance.P_location_material_m[location, process, material_mode, scale_list] == sum(
            weight(scale_) * instance.P_material_m[location, process, material_mode, scale_[:scheduling_scale_level + 1]] for scale_ in scale_iter if scale_[:network_scale_level + 1] == scale_list)

    instance.constraint_location_production_material_mode = Constraint(
        instance.locations, instance.processes, instance.material_modes, *
        scales, rule=location_production_material_mode_rule,
        doc='total production at location')
    return instance.constraint_location_production_material_mode


def constraint_specific_network_discharge(instance: ConcreteModel, bounds: Dict[Resource, float], network_scale_level: int = 0, ) -> Constraint:
    """Determines total resource discharged across specificnetwork

    Args:
        instance (ConcreteModel): pyomo instance
        specific_network_scale_level (int, optional): scale of specific_network decisions. Defaults to 0.

    Returns:
        Constraint: specific_network_discharge
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)
    resource_list = [i.name for i in bounds.keys()]
    bounds_dict = {i.name: bounds[i] for i in bounds.keys()}

    def specific_network_discharge_rule(instance, resource, *scale_list):
        if resource in resource_list:
            return instance.S_network[resource, scale_list] <= bounds_dict[resource]
        else:
            return Constraint.Skip
    return Constraint(instance.resources_sell, *scales, rule=specific_network_discharge_rule, doc='restrict discharge of resource at network level')


def constraint_specific_location_discharge(instance: ConcreteModel, location: Location, bounds: Dict[Resource, float], network_scale_level: int = 0, ) -> Constraint:
    """Determines total resource discharged across specific location

    Args:
        instance (ConcreteModel): pyomo instance
        location (Location): location
        specific_location_scale_level (int, optional): scale of specific_location decisions. Defaults to 0.

    Returns:
        Constraint: specific_location_discharge
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)
    resource_list = [i.name for i in bounds.keys()]
    bounds_dict = {i.name: bounds[i] for i in bounds.keys()}

    def specific_location_discharge_rule(instance, resource, *scale_list):
        if resource in resource_list:
            return instance.S_location[location.name, resource, scale_list] <= bounds_dict[resource]
        else:
            return Constraint.Skip
    return Constraint(instance.resources_sell, *scales, rule=specific_location_discharge_rule, doc='restrict discharge of resource at location level')


def constraint_inventory_network(instance: ConcreteModel, network_scale_level: int = 0, scheduling_scale_level: int = 0) -> Constraint:
    """calculates total inventory stored over the network scale

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: _description_
    """

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level + 1)

    def inventory_network_rule(instance, location, resource, *scale_list):
        return instance.Inv_network[location, resource, scale_list[:network_scale_level + 1]] == sum(instance.Inv[location, resource, scale_] for scale_ in scale_iter if scale_[:network_scale_level + 1] == scale_list)

    instance.constraint_inventory_network = Constraint(
        instance.locations, instance.resources_store, *scales, rule=inventory_network_rule, doc='total inventory at network')
    return instance.constraint_inventory_network
