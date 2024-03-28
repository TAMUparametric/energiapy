"""resource balance constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
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


def constraint_resource_consumption(instance: ConcreteModel, location_resource_dict: dict = None, cons_max: dict = None,
                                    scheduling_scale_level: int = 0, availability_scale_level: int = 0, availability_factor: dict = None) -> Constraint:
    """Determines consumption of resource at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        location_resource_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        cons_max (dict, optional): maximum allowed consumption of resource at location. Defaults to {}.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        availability_factor (dict, optional): normalized factor for the availability of resource
    Returns:
        Constraint: resource_consumption
    """

    if location_resource_dict is None:
        location_resource_dict = dict()

    if cons_max is None:
        cons_max = dict()

    scales = scale_list(instance=instance,
                        scale_levels=len(instance.scales))

    def resource_consumption_rule(instance, location, resource, *scale_list):
        if resource in location_resource_dict[location]:
            if availability_factor[location] is None:
                return instance.C[location, resource, scale_list[:scheduling_scale_level + 1]] <= cons_max[location][resource]
            else:
                return instance.C[location, resource, scale_list[:scheduling_scale_level + 1]] <= availability_factor[location][resource][scale_list[:availability_scale_level + 1]]*cons_max[location][resource]
        else:
            return instance.C[location, resource, scale_list[:scheduling_scale_level + 1]] <= 0

    instance.constraint_resource_consumption = Constraint(
        instance.locations, instance.resources_purch, *
        scales, rule=resource_consumption_rule,
        doc='resource consumption')
    constraint_latex_render(resource_consumption_rule)
    return instance.constraint_resource_consumption


def constraint_inventory_balance(instance: ConcreteModel, scheduling_scale_level: int = 0,
                                 multiconversion: dict = None, mode_dict: dict = None,
                                 cluster_wt: dict = None, inventory_zero: Dict[Location, Dict[Tuple[Process, Resource], float]] = None,
                                 location_resource_dict: dict = None, location_process_dict: dict = None) -> Constraint:
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
                                       scale_list[:scheduling_scale_level + 1]] - inventory_zero[location][resource]
        else:
            storage = 0

        if resource in instance.resources_sell:
            discharge = instance.S[location, resource,
                                   scale_list[:scheduling_scale_level + 1]]
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

        produced = sum(sum(multiconversion[process][mode][resource] * instance.P_m[location, process, mode,
                                                                                   scale_list[:scheduling_scale_level + 1]] for mode in mode_dict[process]) for process in
                       instance.processes_full if process in location_process_dict[location])  # includes processes + discharge

        def weight(x): return 1 if cluster_wt is None else cluster_wt[x]

        return weight(scale_list[:scheduling_scale_level + 1]) * (
            consumption + produced - discharge + transport) == storage

    instance.constraint_inventory_balance = Constraint(
        instance.locations, instance.resources, *scales, rule=inventory_balance_rule,
        doc='mass balance across scheduling scale')
    constraint_latex_render(inventory_balance_rule)
    return instance.constraint_inventory_balance


def constraint_location_production(instance: ConcreteModel, cluster_wt: dict,
                                   network_scale_level: int = 0, scheduling_scale_level: int = 0) -> Constraint:
    """Determines total production capacity utilization at location

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
    Returns:
        Constraint: location_production
    """

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level+1)

    def location_production_rule(instance, location, process, *scale_list):
        def weight(x): return 1 if cluster_wt is None else cluster_wt[x]
        return instance.P_location[location, process, scale_list] == sum(
            weight(scale_) * instance.P[location, process, scale_[:scheduling_scale_level + 1]] for scale_ in scale_iter if scale_[:network_scale_level + 1] == scale_list)

    instance.constraint_location_production = Constraint(
        instance.locations, instance.processes, *scales, rule=location_production_rule,
        doc='total production at location')
    constraint_latex_render(location_production_rule)
    return instance.constraint_location_production


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
    constraint_latex_render(location_production_material_mode_sum_rule)
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
    constraint_latex_render(location_production_material_mode_rule)
    return instance.constraint_location_production_material_mode


def constraint_location_discharge(instance: ConcreteModel, cluster_wt: dict,
                                  network_scale_level: int = 0, scheduling_scale_level: int = 0) -> Constraint:
    """Determines total resource discharged/sold at locations in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
    Returns:
        Constraint: location_discharge
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=len(instance.scales))

    def location_discharge_rule(instance, location, resource, *scale_list):
        def weight(x): return 1 if cluster_wt is None else cluster_wt[x]

        return instance.S_location[location, resource, scale_list] == sum(
            weight(scale_) * instance.S[location, resource, scale_[:scheduling_scale_level + 1]] for scale_ in scale_iter
            if scale_[:network_scale_level + 1] == scale_list)

    instance.constraint_location_discharge = Constraint(
        instance.locations, instance.resources_sell, *
        scales, rule=location_discharge_rule,
        doc='total discharge at location')
    constraint_latex_render(location_discharge_rule)
    return instance.constraint_location_discharge


def constraint_location_consumption(instance: ConcreteModel, cluster_wt: dict,
                                    network_scale_level: int = 0, scheduling_scale_level: int = 0) -> Constraint:
    """Determines total resource consumed at locations in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: location_consumption
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=len(instance.scales))

    def location_consumption_rule(instance, location, resource, *scale_list):
        def weight(x): return 1 if cluster_wt is None else cluster_wt[x]

        return instance.C_location[location, resource, scale_list] == sum(
            weight(scale_) * instance.C[location, resource, scale_[:scheduling_scale_level + 1]] for scale_ in scale_iter
            if scale_[:network_scale_level + 1] == scale_list)

    instance.constraint_location_consumption = Constraint(
        instance.locations, instance.resources_purch, *
        scales, rule=location_consumption_rule,
        doc='total consumption at location')
    constraint_latex_render(location_consumption_rule)
    return instance.constraint_location_consumption


def constraint_network_production(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Determines total production utilization across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_production
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

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
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

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
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def network_consumption_rule(instance, resource, *scale_list):
        return instance.C_network[resource, scale_list] == sum(
            instance.C_location[location_, resource, scale_list] for location_ in instance.locations)

    instance.constraint_network_consumption = Constraint(
        instance.resources_purch, *scales, rule=network_consumption_rule, doc='total consumption from network')
    constraint_latex_render(network_consumption_rule)
    return instance.constraint_network_consumption


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

    constraint_latex_render(specific_network_discharge_rule)
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

    constraint_latex_render(specific_location_discharge_rule)
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
    constraint_latex_render(inventory_network_rule)

    return instance.constraint_inventory_network
