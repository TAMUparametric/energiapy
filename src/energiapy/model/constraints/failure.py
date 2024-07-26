from pyomo.environ import ConcreteModel, Constraint

from ...utils.scale_utils import scale_list


def constraint_nameplate_production_failure(instance: ConcreteModel, fail_factor: dict = None, network_scale_level: int = 0, scheduling_scale_level: int = 0) -> Constraint:
    """Determines production capacity utilization of facilities at location in network and capacity of facilities

    Args:
        instance (ConcreteModel): pyomo instance
        fail_factor (dict, optional): uncertain capacity availability training data. Defaults to {}.
        capacity_factor (dict, optional): uncertain capacity availability training data. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: nameplate_production_failure
    """

    if fail_factor is None:
        fail_factor = dict()

    scales = scale_list(instance=instance,
                        scale_levels=len(instance.scales))

    def nameplate_production_failure_rule(instance, location, process, *scale_list):
        if process in instance.processes_failure:
            return instance.P[location, process, scale_list[:scheduling_scale_level+1]] <= fail_factor[location][process][scale_list[:scheduling_scale_level+1]] * instance.Cap_P[location, process,
                                                                                                                                                                                  scale_list[:network_scale_level+1]]
        else:
            return instance.P[location, process, scale_list[:scheduling_scale_level+1]] <= instance.Cap_P[location, process, scale_list[:network_scale_level+1]]
    instance.constraint_nameplate_production_failure = Constraint(
        instance.locations, instance.processes, *scales, rule=nameplate_production_failure_rule, doc='nameplate production capacity constraint')
    return instance.constraint_nameplate_production_failure
