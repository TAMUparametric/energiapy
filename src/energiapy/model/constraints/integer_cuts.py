from pyomo.environ import ConcreteModel, Constraint

from ...components.location import Location
from ...utils.scale_utils import scale_list


def constraint_block_integer_cut_max(instance: ConcreteModel, network_scale_level: int, location: Location, block: 'str', processes: set, number: int = 1) -> Constraint:
    """maximum number of processes from a block that can be set up at a location

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int): scale for network level decisions 
        location (Location): location at which to impose integer cut
        block (str): process block over which to apply integer cuts
        processes (set): set of all processes in scenario
        number (int, optional): maximum number of process in block allowed. Defaults to 1.

    Returns:
        Constraint: block_integer_cut_max
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def block_integer_cut_max_rule(instance, *scale_list):
        return sum(instance.X_P[location.name, i.name, scale_list] for i in processes if i.block == block) <= number
    return Constraint(*scales, rule=block_integer_cut_max_rule, doc=f'block integer cut for {block}')


def constraint_block_integer_cut_min(instance: ConcreteModel, network_scale_level: int, location: Location, block: 'str', processes: set, number: int = 1) -> Constraint:
    """minimum number of processes from a block that can be set up at a location

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int): scale for network level decisions 
        location (Location): location at which to impose integer cut
        block (str): process block over which to apply integer cuts
        processes (set): set of all processes in scenario
        number (int, optional): minimum number of process in block allowed. Defaults to 1.

    Returns:
        Constraint: block_integer_cut_min
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def block_integer_cut_min_rule(instance, *scale_list):
        return sum(instance.X_P[location.name, i.name, scale_list] for i in processes if i.block == block) >= number
    return Constraint(*scales, rule=block_integer_cut_min_rule, doc=f'block integer cut for {block}')


def constraint_block_integer_cut(instance: ConcreteModel, network_scale_level: int, location: Location, block: 'str', processes: set, number: int = 1) -> Constraint:
    """exact number of processes from a block to be set up at a location

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int): scale for network level decisions 
        location (Location): location at which to impose integer cut
        block (str): process block over which to apply integer cuts
        processes (set): set of all processes in scenario
        number (int, optional): number of process in block to be established. Defaults to 1.

    Returns:
        Constraint: block_integer_cut
    """
    scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

    def block_integer_cut_rule(instance, *scale_list):
        return sum(instance.X_P[location.name, i.name, scale_list] for i in processes if i.block == block) == number
    return Constraint(*scales, rule=block_integer_cut_rule, doc=f'block integer cut for {block}')
