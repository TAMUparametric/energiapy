from pyomo.environ import ConcreteModel, Set

from ...components.scenario import Scenario
from ...utils.scale_utils import scale_pyomo_set


def generate_process_subsets(instance: ConcreteModel, scenario: Scenario):
    """generates process subsets

    Args:
        instance (ConcreteModel): pyomo model
        scenario (Scenario): energiapy scenario
    """

    sets = scenario.set_dict

    instance.processes_varying_capacity = Set(
        initialize=sets['processes_varying_capacity'], doc='Set of processes with varying capacity')
    instance.processes_certain_capacity = Set(
        initialize=sets['processes_certain_capacity'], doc='Set of processes with certain capacity')
    instance.processes_varying_expenditure = Set(
        initialize=sets['processes_varying_expenditure'], doc='Set of processes with varying expenditure')
    instance.processes_failure = Set(
        initialize=sets['processes_failure'], doc='Set of processes which can fail')
    instance.processes_materials = Set(initialize=sets['processes_materials'],
                                       doc='Set of processes with material requirements')
    instance.processes_storage = Set(
        initialize=sets['processes_storage'], doc='Set of storage process')
    instance.processes_multim = Set(
        initialize=sets['processes_multim'], doc='Set of processes with multiple modes')
    instance.processes_singlem = Set(
        initialize=sets['processes_singlem'], doc='Set of processes with multiple modes')

    instance.processes_uncertain_capacity = Set(initialize=sets['processes_uncertain_capacity'],
                                                doc='Set of processes with uncertain capacity')