"""pyomo production constraints
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


def production_facility_constraint(instance: ConcreteModel, prod_max: dict, loc_pro_dict: dict = {}, network_scale_level: int = 0) -> Constraint:
    """Determines where production facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        prod_max (dict): maximum production of process at location
        loc_pro_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: production_facility_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def production_facility_rule(instance, location, process, *scale_list):
        if process in loc_pro_dict[location]:
            return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] <= prod_max[location][process] *\
                instance.X_P[location, process,
                             scale_list[:network_scale_level+1]]
        else:
            return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] == 0
    instance.production_facility_constraint = Constraint(
        instance.locations, instance.processes, *scales, rule=production_facility_rule, doc='production facility sizing and location')
    constraint_latex_render(production_facility_rule)
    return instance.production_facility_constraint


def production_facility_affix_constraint(instance: ConcreteModel, affix_production_cap: dict, loc_pro_dict: dict = {}, network_scale_level: int = 0) -> Constraint:
    """affixes the capacity of production facilities

    Args:
        instance (ConcreteModel): pyomo instance
        prod_max (dict): maximum production of process at location
        loc_pro_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: production_facility_affix_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1) 
    def production_facility_affix_rule(instance, location, process, *scale_list):
        if process in loc_pro_dict[location]:
            if  affix_production_cap[location, process, scale_list[:network_scale_level+1][0]] > 0.0:
                return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] \
                    == affix_production_cap[location, process, scale_list[:network_scale_level+1][0]]
            else:
                return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] >= 0.0
        else:
            return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] == 0
    instance.production_facility_affix_constraint = Constraint(
        instance.locations, instance.processes, *scales, rule=production_facility_affix_rule, doc='production facility sizing and location')
    constraint_latex_render(production_facility_affix_rule)
    return instance.production_facility_affix_constraint


def production_facility_fix_constraint(instance: ConcreteModel, prod_max: dict, production_binaries: dict, loc_pro_dict: dict = {}, network_scale_level: int = 0) -> Constraint:
    """Determines where production facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        prod_max (dict): maximum production of process at location
        loc_pro_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: production_facility_fix_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def production_facility_fix_rule(instance, location, process, *scale_list):
        if process in loc_pro_dict[location]:
            return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] <= prod_max[location][process] *\
                production_binaries[(
                    location, process, *scale_list[:network_scale_level+1])]
        else:
            return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] == 0
    instance.production_facility_fix_constraint = Constraint(
        instance.locations, instance.processes, *scales, rule=production_facility_fix_rule, doc='production facility sizing and location')
    constraint_latex_render(production_facility_fix_rule)
    return instance.production_facility_fix_constraint


def min_production_facility_constraint(instance: ConcreteModel, prod_min: dict, loc_pro_dict: dict = {}, network_scale_level: int = 0) -> Constraint:
    """Determines where production facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        prod_max (dict): maximum production of process at location
        loc_pro_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: min_production_facility_constraint
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def min_production_facility_rule(instance, location, process, *scale_list):
        if process in loc_pro_dict[location]:
            return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] >= prod_min[location][process] *\
                instance.X_P[location, process,
                             scale_list[:network_scale_level+1]]
        else:
            return Constraint.Skip
    instance.min_production_facility_constraint = Constraint(
        instance.locations, instance.processes, *scales, rule=min_production_facility_rule, doc='production facility sizing and location')
    constraint_latex_render(min_production_facility_rule)
    return instance.min_production_facility_constraint

def nameplate_production_constraint(instance: ConcreteModel, capacity_factor: dict = {}, network_scale_level: int = 0, scheduling_scale_level: int = 0) -> Constraint:
    """Determines production capacity utilization of facilities at location in network and capacity of facilities 

    Args:
        instance (ConcreteModel): pyomo instance
        capacity_factor (dict, optional): uncertain capacity availability training data. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: nameplate_production_constraint
    """
    scales = scale_list(instance=instance,
                        scale_levels=instance.scales.__len__())

    def nameplate_production_rule(instance, location, process, *scale_list):
        if process in instance.processes_varying:
            return instance.P[location, process, scale_list[:scheduling_scale_level+1]] <= \
                capacity_factor[location][process][scale_list[:scheduling_scale_level+1]] * \
                instance.Cap_P[location, process,
                               scale_list[:network_scale_level+1]]
        else:
            return instance.P[location, process, scale_list[:scheduling_scale_level+1]] <= instance.Cap_P[location, process, scale_list[:network_scale_level+1]]
    instance.nameplate_production_constraint = Constraint(
        instance.locations, instance.processes, *scales, rule=nameplate_production_rule, doc='nameplate production capacity constraint')
    constraint_latex_render(nameplate_production_rule)
    return instance.nameplate_production_constraint

