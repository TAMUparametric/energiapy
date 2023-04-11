"""pyomo production constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Constraint

from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list


def constraint_production_facility(instance: ConcreteModel, prod_max: dict, loc_pro_dict: dict = None,
                                   network_scale_level: int = 0) -> Constraint:
    """Determines where production facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        prod_max (dict): maximum production of process at location
        loc_pro_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: production_facility
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def production_facility_rule(instance, location, process, *scale_list):
        if loc_pro_dict is not None:
            if process in loc_pro_dict[location]:
                return instance.Cap_P[location, process, scale_list[:network_scale_level + 1]] <= \
                    prod_max[location][process][list(prod_max[location][process].keys())[-1:][0]] * \
                    instance.X_P[location, process,
                                 scale_list[:network_scale_level + 1]]
            else:
                return instance.Cap_P[location, process, scale_list[:network_scale_level + 1]] == 0
        else:
            return Constraint.Skip

    instance.constraint_production_facility = Constraint(
        instance.locations, instance.processes, *scales, rule=production_facility_rule,
        doc='production facility sizing and location')
    constraint_latex_render(production_facility_rule)
    return instance.constraint_production_facility


def constraint_storage_facility(instance: ConcreteModel, store_max: dict, loc_res_dict: dict = None,
                                network_scale_level: int = 0) -> Constraint:
    """Determines where storage facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        store_max (dict): maximum storage capacity of resource at location
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: storage_facility
    """

    if loc_res_dict is None:
        loc_res_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def storage_facility_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level + 1]] <= store_max[location][
                resource]*instance.X_S[location, resource,
                                       scale_list[:network_scale_level + 1]]
        else:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level + 1]] == 0

    instance.constraint_storage_facility = Constraint(
        instance.locations, instance.resources_store, *
        scales, rule=storage_facility_rule,
        doc='storage facility sizing and location')
    constraint_latex_render(storage_facility_rule)
    return instance.constraint_storage_facility


def constraint_min_storage_facility(instance: ConcreteModel, store_min: dict, loc_res_dict: dict = None,
                                    network_scale_level: int = 0) -> Constraint:
    """Determines where storage facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        store_max (dict): maximum storage capacity of resource at location
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.


    Returns:
        Constraint: min_storage_facility
    """

    if loc_res_dict is None:
        loc_res_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def min_storage_facility_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level + 1]] >= store_min[location][
                resource] * \
                instance.X_S[location, resource,
                             scale_list[:network_scale_level + 1]]
        else:
            return Constraint.Skip

    instance.constraint_min_storage_facility = Constraint(
        instance.locations, instance.resources_store, *
        scales, rule=min_storage_facility_rule,
        doc='storage facility sizing and location')
    constraint_latex_render(min_storage_facility_rule)
    return instance.constraint_min_storage_facility


def constraint_min_production_facility(instance: ConcreteModel, prod_min: dict, loc_pro_dict: dict = None,
                                       network_scale_level: int = 0) -> Constraint:
    """Determines where production facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        prod_max (dict): maximum production of process at location
        loc_pro_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: min_production_facility
    """

    if loc_pro_dict is None:
        loc_pro_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def min_production_facility_rule(instance, location, process, *scale_list):
        if loc_pro_dict is not None:
            if process in loc_pro_dict[location]:
                return instance.Cap_P[location, process, scale_list[:network_scale_level + 1]] >= prod_min[location][process][list(prod_min[location][process].keys())[:1][0]] * instance.X_P[location, process, scale_list[:network_scale_level + 1]]
            else:
                return instance.Cap_P[location, process, scale_list[:network_scale_level + 1]] == 0
        else:
            return Constraint.Skip

    instance.constraint_min_production_facility = Constraint(
        instance.locations, instance.processes, *
        scales, rule=min_production_facility_rule,
        doc='production facility sizing and location')
    constraint_latex_render(min_production_facility_rule)
    return instance.constraint_min_production_facility
