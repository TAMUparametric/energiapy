from pyomo.environ import ConcreteModel, Constraint
from ...utils.scale_utils import scale_list, scale_tuple
from ...model.bounds import CapacityBounds


def constraint_production_facility(instance: ConcreteModel, cap_max: dict, location_process_dict: dict = None,
                                   network_scale_level: int = 0) -> Constraint:
    """Determines where production facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        cap_max (dict): maximum production of process at location
        location_process_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: production_facility
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def production_facility_rule(instance, location, process, *scale_list):
        if location_process_dict is not None:
            if process in location_process_dict[location]:
                return instance.Cap_P[location, process, scale_list[:network_scale_level + 1]] <= cap_max[location][process][list(cap_max[location][process].keys())[-1:][0]]*instance.X_P[location, process, scale_list[:network_scale_level + 1]]
            else:
                return instance.Cap_P[location, process, scale_list[:network_scale_level + 1]] == 0
        else:
            return Constraint.Skip

    instance.constraint_production_facility = Constraint(
        instance.locations, instance.processes, *scales, rule=production_facility_rule,
        doc='production facility sizing and location')
    return instance.constraint_production_facility


def constraint_storage_facility(instance: ConcreteModel, store_max: dict, location_resource_dict: dict = None,
                                network_scale_level: int = 0) -> Constraint:
    """Determines where storage facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        store_max (dict): maximum storage capacity of resource at location
        location_resource_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: storage_facility
    """

    if location_resource_dict is None:
        location_resource_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def storage_facility_rule(instance, location, resource, *scale_list):
        if resource in location_resource_dict[location]:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level + 1]] <= store_max[location][
                resource]*instance.X_S[location, resource,
                                       scale_list[:network_scale_level + 1]]
        else:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level + 1]] == 0

    instance.constraint_storage_facility = Constraint(
        instance.locations, instance.resources_store, *scales, rule=storage_facility_rule, doc='storage facility sizing and location')
    return instance.constraint_storage_facility


def constraint_min_storage_facility(instance: ConcreteModel, store_min: dict, location_resource_dict: dict = None,
                                    network_scale_level: int = 0) -> Constraint:
    """Determines where storage facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        store_max (dict): maximum storage capacity of resource at location
        location_resource_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.


    Returns:
        Constraint: min_storage_facility
    """

    if location_resource_dict is None:
        location_resource_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def min_storage_facility_rule(instance, location, resource, *scale_list):
        if resource in location_resource_dict[location]:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level + 1]] >= store_min[location][
                resource] * instance.X_S[location, resource, scale_list[:network_scale_level + 1]]
        else:
            return Constraint.Skip

    instance.constraint_min_storage_facility = Constraint(
        instance.locations, instance.resources_store, *
        scales, rule=min_storage_facility_rule,
        doc='storage facility sizing and location')
    return instance.constraint_min_storage_facility


def constraint_min_production_facility(instance: ConcreteModel, cap_min: dict, location_process_dict: dict = None,
                                       network_scale_level: int = 0) -> Constraint:
    """Determines where production facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        cap_min (dict): minimum production of process at location
        location_process_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: min_production_facility
    """

    if location_process_dict is None:
        location_process_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def min_production_facility_rule(instance, location, process, *scale_list):
        if location_process_dict is not None:
            if process in location_process_dict[location]:
                return instance.Cap_P[location, process, scale_list[:network_scale_level + 1]] >= cap_min[location][process][list(cap_min[location][process].keys())[:1][0]] * instance.X_P[location, process, scale_list[:network_scale_level + 1]]
            else:
                return instance.Cap_P[location, process, scale_list[:network_scale_level + 1]] == 0
        else:
            return Constraint.Skip

    instance.constraint_min_production_facility = Constraint(
        instance.locations, instance.processes, *
        scales, rule=min_production_facility_rule,
        doc='production facility sizing and location')
    return instance.constraint_min_production_facility


def constraint_min_capacity_facility(instance: ConcreteModel, location_process_dict: dict = None, network_scale_level: int = 0, capacity_bounds: CapacityBounds = None) -> Constraint:
    """Minimum capacity recieved from CapacityBounds object

    Args:
        instance (ConcreteModel): pyomo instance
        location_process_dict (dict, optional): capacity facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: min_capacity_facility
    """

    if location_process_dict is None:
        location_process_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def min_capacity_facility_rule(instance, location, process, *scale_list):
        if location_process_dict is not None:
            if process in location_process_dict[location]:
                return instance.Cap_P[location, process, scale_list[:network_scale_level + 1]] >= capacity_bounds.Cap_P_min[location, process, scale_list[:network_scale_level + 1][0]]
            else:
                return instance.Cap_P[location, process, scale_list[:network_scale_level + 1]] == 0
        else:
            return Constraint.Skip

    instance.constraint_min_capacity_facility = Constraint(
        instance.locations, instance.processes, *
        scales, rule=min_capacity_facility_rule,
        doc='capacity facility sizing initialization')
    return instance.constraint_min_capacity_facility


def constraint_preserve_capacity_facility(instance: ConcreteModel, location_process_dict: dict = None, network_scale_level: int = 0) -> Constraint:
    """Ensures that capacity over network scale is not reduced
    Essentially, the capacity of a facility is preserved

    Args:
        instance (ConcreteModel): pyomo instance
        location_process_dict (dict, optional): capacity facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: preserve_capacity_facility
    """

    if location_process_dict is None:
        location_process_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)

    def preserve_capacity_facility_rule(instance, location, process, *scale_list):
        if location_process_dict is not None:
            if process in location_process_dict[location]:
                if scale_list[:network_scale_level + 1] != scale_iter[0]:
                    return instance.Cap_P[location, process, scale_list[:network_scale_level + 1]] >= instance.Cap_P[location, process, scale_iter[scale_iter.index(
                        scale_list[:network_scale_level + 1]) - 1]]
                else:
                    return Constraint.Skip
            else:
                return instance.Cap_P[location, process, scale_list[:network_scale_level + 1]] == 0
        else:
            return Constraint.Skip

    instance.constraint_preserve_capacity_facility = Constraint(
        instance.locations, instance.processes, *
        scales, rule=preserve_capacity_facility_rule,
        doc='preserves the capacity over network scale')
    return instance.constraint_preserve_capacity_facility
