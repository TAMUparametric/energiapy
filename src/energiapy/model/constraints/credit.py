"""credit constraints
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


def constraint_credit_process(instance: ConcreteModel, credit_dict: dict, network_scale_level: int = 0) -> Constraint:
    """Credit generated for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        credit_dict (dict): credit generated at location
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: credit_process
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def credit_process_rule(instance, location, process, *scale_list):
        if credit_dict != {}:
            if process in credit_dict[location]:
                return instance.Credit_process[location, process, scale_list] == credit_dict[location][process] * instance.P_location[
                    location, process, scale_list]
            else:
                return instance.Credit_process[location, process, scale_list] == 0
        return Constraint.Skip

    instance.constraint_credit_process = Constraint(
        instance.locations, instance.processes, *scales, rule=credit_process_rule, doc='credit generated for process')
    constraint_latex_render(credit_process_rule)
    return instance.constraint_credit_process


def constraint_credit_location(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Credit generated at each location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: credit_location
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def credit_location_rule(instance, location, *scale_list):
        return instance.Credit_location[location, scale_list] == sum(
            instance.Credit_process[location, process_, scale_list] for process_ in instance.processes)

    instance.constraint_credit_location = Constraint(
        instance.locations, *scales, rule=credit_location_rule, doc='credit generated for process')
    constraint_latex_render(credit_location_rule)
    return instance.constraint_credit_location


def constraint_credit_network(instance: ConcreteModel, network_scale_level: int = 0) -> Constraint:
    """Credit generated by network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: credit_network
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def credit_network_rule(instance, *scale_list):
        return instance.Credit_network[scale_list] == sum(
            instance.Credit_location[location_, scale_list] for location_ in instance.locations)

    instance.constraint_credit_network = Constraint(
        *scales, rule=credit_network_rule, doc='credit generated for process')
    constraint_latex_render(credit_network_rule)
    return instance.constraint_credit_network
