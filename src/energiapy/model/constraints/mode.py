"""production mode constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Constraint
from ...components.process import ProcessMode

from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list, scale_tuple


def constraint_production_mode(instance: ConcreteModel, mode_dict: dict, scheduling_scale_level: int = 0, location_process_dict: dict = None) -> Constraint:
    """The sum of production through all modes equals production at scheduling scale

    Args:
        instance (ConcreteModel): pyomo model instance
        mode_dict (dict): dictionary with modes available for process
        scheduling_scale_level (int, optional): scale for scheduling decisions. Defaults to 0.

    Returns:
        Constraint: production_mode
    """

    if location_process_dict is None:
        location_process_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level + 1)

    def production_mode_rule(instance, location, process, *scale_list):
        if process in location_process_dict[location]:
            return instance.P[location, process, scale_list[:scheduling_scale_level + 1]] == sum(
                instance.P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] for mode in
                mode_dict[process])
        else:
            return Constraint.Skip

    instance.constraint_production_mode = Constraint(
        instance.locations, instance.processes, *scales, rule=production_mode_rule,
        doc='production mode sum constraint')
    constraint_latex_render(production_mode_rule)
    return instance.constraint_production_mode


def constraint_production_mode_facility(instance: ConcreteModel, prod_max: dict, location_process_dict: dict = None,
                                        scheduling_scale_level: int = 0) -> Constraint:
    """Constraints production to maximum in mode

    Args:
        instance (ConcreteModel): pyomo instance
        prod_max (dict): maximum production of process at location
        location_process_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: production_facility_mode
    """

    if location_process_dict is None:
        location_process_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level + 1)

    def production_mode_facility_rule(instance, location, process, mode, *scale_list):
        if process in location_process_dict[location]:
            if mode <= list(prod_max[location][process].keys())[-1:][0]:
                return instance.Cap_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] <= prod_max[location][process][mode] * instance.X_P_m[location, process, mode,
                                                                                                                                                            scale_list[:scheduling_scale_level + 1]]
            else:
                return Constraint.Skip
        else:
            # return instance.Cap_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] == 0
            return Constraint.Skip

    instance.constraint_production_mode_facility = Constraint(
        instance.locations, instance.processes, instance.modes, *
        scales, rule=production_mode_facility_rule,
        doc='production facility sizing and location')
    constraint_latex_render(production_mode_facility_rule)
    return instance.constraint_production_mode_facility


def constraint_min_production_mode_facility(instance: ConcreteModel, prod_min: dict, location_process_dict: dict = None,
                                            scheduling_scale_level: int = 0) -> Constraint:
    """Constraints production to minimum in mode

    Args:
        instance (ConcreteModel): pyomo instance
        prod_min (dict): minimum production of process at location
        location_process_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: production_facility_mode
    """

    if location_process_dict is None:
        location_process_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level + 1)

    def min_production_mode_facility_rule(instance, location, process, mode, *scale_list):
        if process in location_process_dict[location]:
            if mode <= list(prod_min[location][process].keys())[-1:][0]:
                return instance.Cap_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] >= prod_min[location][process][mode] * instance.X_P_m[location, process, mode,
                                                                                                                                                                scale_list[:scheduling_scale_level + 1]]
            else:
                return Constraint.Skip
        else:
            # return instance.Cap_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] == 0
            return Constraint.Skip

    instance.constraint_min_production_mode_facility = Constraint(
        instance.locations, instance.processes, instance.modes, *
        scales, rule=min_production_mode_facility_rule,
        doc='production facility sizing and location')
    constraint_latex_render(min_production_mode_facility_rule)
    return instance.constraint_min_production_mode_facility


def constraint_production_mode_binary(instance: ConcreteModel, mode_dict: dict, scheduling_scale_level: int = 0,
                                      network_scale_level: int = 0) -> Constraint:
    """Production facility can function only in one mode

    Args:
        instance (ConcreteModel): pyomo model instance
        mode_dict (dict): dictionary with modes available for process
        scheduling_scale_level (int, optional): scale for scheduling decisions. Defaults to 0.
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: production_mode_binary
    """

    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level + 1)

    def production_mode_binary_rule(instance, location, process, *scale_list):
        return instance.X_P[location, process, scale_list[:network_scale_level + 1]] >= sum(
            instance.X_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] for mode in
            mode_dict[process])

    instance.constraint_production_mode_binary = Constraint(
        instance.locations, instance.processes, *
        scales, rule=production_mode_binary_rule,
        doc='production mode binary sum constraint')
    constraint_latex_render(production_mode_binary_rule)
    return instance.constraint_production_mode_binary

def constraint_production_mode_wo_binary(instance: ConcreteModel, mode_dict: dict, scheduling_scale_level: int = 0
                                         ) -> Constraint:
    """Production facility can function only in one mode without network binary variables

    Args:
        instance (ConcreteModel): pyomo model instance
        mode_dict (dict): dictionary with modes available for process
        scheduling_scale_level (int, optional): scale for scheduling decisions. Defaults to 0.

    Returns:
        Constraint: production_mode_wo_binary
    """

    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level + 1)

    def production_mode_wo_binary_rule(instance, location, process, *scale_list):
        return 1 == sum(
            instance.X_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] for mode in
            mode_dict[process])

    instance.constraint_production_mode_wo_binary = Constraint(
        instance.locations, instance.processes, *
        scales, rule=production_mode_wo_binary_rule,
        doc='production mode without binary sum constraint')
    constraint_latex_render(production_mode_wo_binary_rule)
    return instance.constraint_production_mode_wo_binary


def constraint_fixed_nameplate_min_production_mode(instance: ConcreteModel, prod_min: dict, location_process_dict: dict = None,
                                                   scheduling_scale_level: int = 0, mode_dict: dict = None) -> Constraint:
    """
    Determines minimum production capacity utilization of facility modes at location in network and capacity of facilities

    Args:
        instance (ConcreteModel): pyomo model instance
        prod_min (dict): dictionary with minimum production rates for modes
        location_process_dict (dict): production facilities avaiable at location. Defaults to {}.
        scheduling_scale_level (int, optional): scale for scheduling decisions. Defaults to 0.

    Returns:
        Constraint: fixed_nameplate_min_production_mode
    """

    if location_process_dict is None:
        location_process_dict = dict()

    if mode_dict is None:
        mode_dict = dict()

    scales = scale_list(instance=instance, scale_levels=scheduling_scale_level+1)

    def fixed_nameplate_min_production_mode_rule(instance, location, process, mode, *scale_list):
        if process not in location_process_dict[location]:
            return Constraint.Skip

        if len(mode_dict[process])<=1:
            return Constraint.Skip

        if mode <= list(prod_min[location][process].keys())[-1:][0]:
            rhs = (prod_min[location][process][mode]*instance.X_P_m[location, process, mode, scale_list[:scheduling_scale_level+1]])
            lhs = instance.P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]]

            # if process not in instance.processes_varying_capacity:
            #     return lhs >= rhs

            # cap_factor = capacity_factor[location][process][scale_list[:capacity_scale_level + 1]] if capacity_factor[
            #     location] else 1
            return lhs >= rhs

        return Constraint.Skip

    instance.constraint_fixed_nameplate_min_production_mode = Constraint(instance.locations, instance.processes, instance.modes,
                                                               *scales, rule=fixed_nameplate_min_production_mode_rule,
                                                               doc='mode nameplate min production capacity constraint')
    constraint_latex_render(fixed_nameplate_min_production_mode_rule)
    return instance.constraint_fixed_nameplate_min_production_mode

def constraint_fixed_nameplate_max_production_mode(instance: ConcreteModel, prod_max: dict, location_process_dict: dict = None,
                                         scheduling_scale_level: int = 0, mode_dict: dict = None) -> Constraint:
    """
    Determines maximum production capacity utilization of facility modes at location in network and capacity of facilities

    Args:
        instance (ConcreteModel): pyomo model instance
        mode_dict (dict): dictionary with modes available for process
        scheduling_scale_level (int, optional): scale for scheduling decisions. Defaults to 0.

    Returns:
        Constraint: fixed_nameplate_max_production_mode
    """

    if mode_dict is None:
        mode_dict = dict()

    if location_process_dict is None:
        location_process_dict = dict()

    scales = scale_list(instance=instance, scale_levels=scheduling_scale_level+1)

    def fixed_nameplate_max_production_mode_rule(instance, location, process, mode, *scale_list):
        if process not in location_process_dict[location]:
            return Constraint.Skip

        if len(mode_dict[process]) <= 1:
            return Constraint.Skip

        if mode <= list(prod_max[location][process].keys())[-1:][0]:
            rhs = (prod_max[location][process][mode]*instance.X_P_m[location, process, mode, scale_list[:scheduling_scale_level+1]])
            lhs = instance.P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]]

            return lhs <= rhs

        return Constraint.Skip

    instance.constraint_fixed_nameplate_max_production_mode = Constraint(instance.locations, instance.processes, instance.modes,
                                                               *scales, rule=fixed_nameplate_max_production_mode_rule,
                                                               doc='mode nameplate max production capacity constraint')
    constraint_latex_render(fixed_nameplate_max_production_mode_rule)
    return instance.constraint_fixed_nameplate_max_production_mode

# def constraint_production_rate1(instance: ConcreteModel, rate_max_dict: dict, scheduling_scale_level: int = 0) -> Constraint:
#     """Manages the production rate in mode along with constraint_production_rate2
#
#     Args:
#         instance (ConcreteModel): pyomo model instance
#         rate_max_dict (dict): dictionary with max rates within modes available for process
#         scheduling_scale_level (int, optional): scale for scheduling decisions. Defaults to 0.
#
#     Returns:
#         Constraint: production_mode_rate1
#     """
#
#     scales = scale_list(instance=instance,
#                         scale_levels=scheduling_scale_level + 1)
#     scale_iter = scale_tuple(
#         instance=instance, scale_levels=scheduling_scale_level + 1)
#
#     def production_rate_rule1(instance, location, process, mode, *scale_list):
#         if rate_max_dict[process] is not None:
#             # if all(e==0 for e in scale_list):
#             #     # lhs = instance.P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]]
#             #     # rhs = - rate_max_dict[process][mode] - max(rate_max_dict[process].values())*(2 - instance.X_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]])
#             #     return Constraint.Skip
#             #
#             # else:
#             lhs = instance.P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] - instance.P_m[location,
#                                                                                                             process, mode, scale_iter[scale_iter.index(scale_list[:scheduling_scale_level + 1]) - 1]]
#             rhs = - rate_max_dict[process][mode] - max(rate_max_dict[process].values())*(2 - instance.X_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] -
#                                                                                      instance.X_P_m[location, process, mode, scale_iter[scale_iter.index(scale_list[:scheduling_scale_level + 1]) - 1]])
#             # rhs = - (rate_max_dict[process][mode] - 10000 * (2 - instance.X_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] -
#             #                instance.X_P_m[location, process, mode, scale_iter[scale_iter.index(scale_list[:scheduling_scale_level + 1]) - 1]]))
#             return lhs >= rhs
#
#         else:
#             return Constraint.Skip
#
#     instance.constraint_production_rate1 = Constraint(
#         instance.locations, instance.processes, instance.modes, *
#         scales, rule=production_rate_rule1,
#         doc='production mode rate 1')
#     constraint_latex_render(production_rate_rule1)
#     return instance.constraint_production_rate1
#
#
# def constraint_production_rate2(instance: ConcreteModel, rate_max_dict: dict, scheduling_scale_level: int = 0) -> Constraint:
#     """Manages the production rate in mode along with constraint_production_rate1
#
#     Args:
#         instance (ConcreteModel): pyomo model instance
#         rate_max_dict (dict): dictionary with max rates within modes available for process
#         scheduling_scale_level (int, optional): scale for scheduling decisions. Defaults to 0.
#
#     Returns:
#         Constraint: production_mode_rate2
#     """
#
#     scales = scale_list(instance=instance,
#                         scale_levels=scheduling_scale_level + 1)
#     scale_iter = scale_tuple(
#         instance=instance, scale_levels=scheduling_scale_level + 1)
#
#     def production_rate_rule2(instance, location, process, mode, *scale_list):
#         if rate_max_dict[process] is not None:
#             # if all(e==0 for e in scale_list):
#             #     return Constraint.Skip
#             # else:
#             lhs = instance.P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] - instance.P_m[location,
#                                                                                                                 process, mode, scale_iter[scale_iter.index(scale_list[:scheduling_scale_level + 1]) - 1]]
#             rhs = rate_max_dict[process][mode] + max(rate_max_dict[process].values())*(2 - instance.X_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]
#                                                                                                       ] - instance.X_P_m[location, process, mode, scale_iter[scale_iter.index(scale_list[:scheduling_scale_level + 1]) - 1]])
#             # rhs = (rate_max_dict[process][mode] + 10000 * (2 - instance.X_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] -
#             #                instance.X_P_m[location, process, mode, scale_iter[scale_iter.index(scale_list[:scheduling_scale_level + 1]) - 1]]))
#             return lhs <= rhs
#         else:
#             return Constraint.Skip
#
#     instance.constraint_production_rate2 = Constraint(
#         instance.locations, instance.processes, instance.modes, *
#         scales, rule=production_rate_rule2,
#         doc='production mode rate 1')
#     constraint_latex_render(production_rate_rule2)
#     return instance.constraint_production_rate2


def constraint_production_rate1(instance: ConcreteModel, rate_max_dict: dict, scheduling_scale_level: int = 0) -> Constraint:
    """Manages the production rate in mode along with constraint_production_rate1

    Args:
        instance (ConcreteModel): pyomo model instance
        rate_max_dict (dict): dictionary with max rates within modes available for process
        scheduling_scale_level (int, optional): scale for scheduling decisions. Defaults to 0.

    Returns:
        Constraint: production_mode_rate1
    """

    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level + 1)
    scale_iter = scale_tuple(instance=instance,
                              scale_levels=scheduling_scale_level + 1)

    # loc_list = [loc.name for loc in scenario.location_set if loc.capacity_factor is not None]

    def production_rate_rule1(instance, location, process, mode, *scale_list):
        if rate_max_dict[process] is not None:
            if all(e==0 for e in scale_list):
                return Constraint.Skip
            if scale_list[2]==0:
                return Constraint.Skip
            else:
                lhs = instance.P[location, process, scale_list[:scheduling_scale_level + 1]] - instance.P[location, process,  scale_iter[scale_iter.index(scale_list[:scheduling_scale_level + 1]) - 1]]
                rhs = sum(rate_max_dict[process][mode]*instance.X_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] for mode in instance.modes)
            return lhs <= rhs
        else:
            return Constraint.Skip

    instance.constraint_production_rate1 = Constraint(
        instance.locations, instance.processes, instance.modes, *
        scales, rule=production_rate_rule1,
        doc='production mode rate 1')
    constraint_latex_render(production_rate_rule1)
    return instance.constraint_production_rate1


def constraint_production_rate2(instance: ConcreteModel, rate_max_dict: dict, scheduling_scale_level: int = 0) -> Constraint:
    """Manages the production rate in mode along with constraint_production_rate1

    Args:
        instance (ConcreteModel): pyomo model instance
        rate_max_dict (dict): dictionary with max rates within modes available for process
        scheduling_scale_level (int, optional): scale for scheduling decisions. Defaults to 0.

    Returns:
        Constraint: production_mode_rate2
    """

    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level + 1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level + 1)

    def production_rate_rule2(instance, location, process, mode, *scale_list):
        if rate_max_dict[process] is not None:
            if all(e==0 for e in scale_list):
                return Constraint.Skip
            if scale_list[2]==0:
                return Constraint.Skip
            else:
                lhs = instance.P[location, process, scale_list[:scheduling_scale_level + 1]] - instance.P[location, process, scale_iter[scale_iter.index(scale_list[:scheduling_scale_level + 1]) - 1]]
                rhs = -sum(rate_max_dict[process][mode]*instance.X_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] for mode in instance.modes)
            return lhs >= rhs
        else:
            return Constraint.Skip

    instance.constraint_production_rate2 = Constraint(
        instance.locations, instance.processes, instance.modes, *
        scales, rule=production_rate_rule2,
        doc='production mode rate 2')
    constraint_latex_render(production_rate_rule2)
    return instance.constraint_production_rate2


def constraint_production_mode_switch(instance: ConcreteModel, mode_dict: dict, scheduling_scale_level: int = 0) -> Constraint:
    """The sum of production through all modes equals production at scheduling scale

    Args:
        instance (ConcreteModel): pyomo model instance
        scheduling_scale_level (int, optional): scale for scheduling decisions. Defaults to 0.

    Returns:
        Constraint: production_mode_switch
    """

    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level + 1)
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level + 1)

    def production_mode_switch_rule(instance, location, process, mode, *scale_list):
        if len(mode_dict[process]) > 1:
            lhs = sum(instance.X_P_mm[location, process, mode_, mode, scale_list[:scheduling_scale_level+1]] for mode_ in instance.modes) - sum(
                instance.X_P_mm[location, process, mode, mode_, scale_list[:scheduling_scale_level+1]] for mode_ in instance.modes)

            rhs = instance.X_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] - \
                instance.X_P_m[location, process, mode, scale_iter[scale_iter.index(
                    scale_list[:scheduling_scale_level + 1]) - 1]]

            return lhs == rhs
        else:
            return Constraint.Skip

    instance.production_mode_switch = Constraint(
        instance.locations, instance.processes, instance.modes, *
        scales, rule=production_mode_switch_rule,
        doc='production mode switch')
    constraint_latex_render(production_mode_switch_rule)
    return instance.production_mode_switch
