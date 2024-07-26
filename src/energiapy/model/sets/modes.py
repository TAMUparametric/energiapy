from pyomo.environ import ConcreteModel, Set

from ...components.scenario import Scenario
from ...utils.scale_utils import scale_pyomo_set


def generate_production_mode_sets(instance: ConcreteModel, scenario: Scenario):
    """generates production mode sets

    Args:
        instance (ConcreteModel): pyomo model
        scenario (Scenario): energiapy scenario
    """

    sets = scenario.set_dict

    instance.processes_segments = Set(
        initialize=sets['processes_segments'], doc='Set of processes with PWL process segments')

    instance.process_modes = Set(
        scenario.set_dict['processes_full'], initialize=scenario.mode_dict, doc='Set of processes and thier modes')


def generate_material_mode_sets(instance: ConcreteModel, scenario: Scenario):
    """generates process material mode sets

    Args:
        instance (ConcreteModel): pyomo model
        scenario (Scenario): energiapy scenario
    """

    sets = scenario.set_dict

    instance.process_material_modes = Set(
        initialize=sets['process_material_modes'], doc='Set of process and material combinations')

    instance.material_modes = Set(
        initialize=sets['material_modes'], doc='Set of material modes')
