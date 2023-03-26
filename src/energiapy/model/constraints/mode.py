"""pyomo production constraints
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
from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list


def constraint_production_mode(instance: ConcreteModel, mode_dict: dict, scheduling_scale_level: int = 0) -> Constraint:
    """The sum of production through all modes equals production at scheduling scale

    Args:
        instance (ConcreteModel): pyomo model instance
        mode_dict (dict): dictionary with modes available for process
        scheduling_scale_level (int, optional): scale for scheduling decisions. Defaults to 0.

    Returns:
        Constraint: production_mode
    """

    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level + 1)

    def production_mode_rule(instance, location, process, *scale_list):
        return instance.P[location, process, scale_list[:scheduling_scale_level + 1]] == sum(
            instance.P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] for mode in
            mode_dict[process])

    instance.constraint_production_mode = Constraint(
        instance.locations, instance.processes, *scales, rule=production_mode_rule,
        doc='production mode sum constraint')
    constraint_latex_render(production_mode_rule)
    return instance.constraint_production_mode


def constraint_production_mode_facility(instance: ConcreteModel, prod_max: dict, loc_pro_dict: dict = None,
                                        scheduling_scale_level: int = 0) -> Constraint:
    """Determines where production facility of certain capacity is mode for process at location in schedule

    Args:
        instance (ConcreteModel): pyomo instance
        prod_max (dict): maximum production of process at location
        loc_pro_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: production_facility_mode
    """

    if loc_pro_dict is None:
        loc_pro_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level + 1)

    def production_mode_facility_rule(instance, location, process, mode, *scale_list):
        if process in loc_pro_dict[location]:
            if mode <= list(prod_max[location][process].keys())[-1:][0]:
                return instance.Cap_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] <= \
                    prod_max[location][process][mode] * \
                    instance.X_P_m[location, process, mode,
                    scale_list[:scheduling_scale_level + 1]]

            return Constraint.Skip

        return instance.Cap_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] == 0

    instance.constraint_production_mode_facility = Constraint(
        instance.locations, instance.processes, instance.modes, *scales, rule=production_mode_facility_rule,
        doc='production facility sizing and location')
    constraint_latex_render(production_mode_facility_rule)
    return instance.constraint_production_mode_facility


def constraint_production_mode_binary(instance: ConcreteModel, mode_dict: dict, scheduling_scale_level: int = 0,
                                      network_scale_level: int = 0) -> Constraint:
    """The sum of production through all modes equals production at scheduling scale

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
        return instance.X_P[location, process, scale_list[:network_scale_level + 1]] == sum(
            instance.X_P_m[location, process, mode, scale_list[:scheduling_scale_level + 1]] for mode in
            mode_dict[process])

    instance.constraint_production_mode_binary = Constraint(
        instance.locations, instance.processes, *scales, rule=production_mode_binary_rule,
        doc='production mode binary sum constraint')
    constraint_latex_render(production_mode_binary_rule)
    return instance.constraint_production_mode_binary
