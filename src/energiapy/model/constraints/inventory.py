"""pyomo inventory constraints
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


def storage_facility_constraint(instance: ConcreteModel, store_max: dict, loc_res_dict: dict = {},  network_scale_level: int = 0) -> Constraint:
    """Determines where storage facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        store_max (dict): maximum storage capacity of resource at location
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: storage_facility_constraint
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def storage_facility_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] <= store_max[location][resource] *\
                instance.X_S[location, resource,
                             scale_list[:network_scale_level+1]]
        else:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] == 0
    instance.storage_facility_constraint = Constraint(
        instance.locations, instance.resources_store, *scales, rule=storage_facility_rule, doc='storage facility sizing and location')
    constraint_latex_render(storage_facility_rule)
    return instance.storage_facility_constraint

def storage_facility_affix_constraint(instance: ConcreteModel, affix_storage_cap: dict, loc_res_dict: dict = {},  network_scale_level: int = 0) -> Constraint:
    """Determines where storage facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        store_max (dict): maximum storage capacity of resource at location
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: storage_facility_affix_constraint
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def storage_facility_affix_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            if affix_storage_cap[location, resource, scale_list[:network_scale_level+1][0]] > 0.0:
                return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] \
                    == affix_storage_cap[location, resource, scale_list[:network_scale_level+1][0]] 
            else:
                return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] >= 0.0
        else:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] == 0
    instance.storage_facility_affix_constraint = Constraint(
        instance.locations, instance.resources_store, *scales, rule=storage_facility_affix_rule, doc='storage facility sizing and location')
    constraint_latex_render(storage_facility_affix_rule)
    return instance.storage_facility_affix_constraint


def storage_facility_fix_constraint(instance: ConcreteModel, store_max: dict, storage_binaries: dict, loc_res_dict: dict = {},  network_scale_level: int = 0) -> Constraint:
    """Determines where storage facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        store_max (dict): maximum storage capacity of resource at location
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.


    Returns:
        Constraint: storage_facility_fix_constraint
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def storage_facility_fix_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] <= store_max[location][resource] *\
                storage_binaries[(location, resource, *
                                  scale_list[:network_scale_level+1])]
        else:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] == 0
    instance.storage_facility_fix_constraint = Constraint(
        instance.locations, instance.resources_store, *scales, rule=storage_facility_fix_rule, doc='storage facility sizing and location')
    constraint_latex_render(storage_facility_fix_rule)
    return instance.storage_facility_fix_constraint


def min_storage_facility_constraint(instance: ConcreteModel, store_min: dict, loc_res_dict: dict = {},  network_scale_level: int = 0) -> Constraint:
    """Determines where storage facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        store_max (dict): maximum storage capacity of resource at location
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.


    Returns:
        Constraint: min_storage_facility_constraint
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def min_storage_facility_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] >= store_min[location][resource] *\
                instance.X_S[location, resource,
                             scale_list[:network_scale_level+1]]
        else:
            return Constraint.Skip
    instance.min_storage_facility_constraint = Constraint(
        instance.locations, instance.resources_store, *scales, rule=min_storage_facility_rule, doc='storage facility sizing and location')
    constraint_latex_render(min_storage_facility_rule)
    return instance.min_storage_facility_constraint


def nameplate_inventory_constraint(instance: ConcreteModel, loc_res_dict: dict = {}, network_scale_level: int = 0, scheduling_scale_level: int = 0) -> Constraint:
    """Determines storage capacity utilization for resource at location in network and capacity of facilities 

    Args:
        instance (ConcreteModel): pyomo instance
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: nameplate_inventory_constraint
    """
    scales = scale_list(instance=instance,
                        scale_levels=instance.scales.__len__())

    def nameplate_inventory_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] <= instance.Cap_S[location, resource, scale_list[:network_scale_level+1]]
        else:
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] <= 0
    instance.nameplate_inventory_constraint = Constraint(
        instance.locations, instance.resources_store, *scales, rule=nameplate_inventory_rule, doc='nameplate inventory capacity constraint')
    constraint_latex_render(nameplate_inventory_rule)
    return instance.nameplate_inventory_constraint
