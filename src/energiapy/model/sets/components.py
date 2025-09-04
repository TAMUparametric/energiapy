from ...components.scenario import Scenario
from ...utils.scale_utils import scale_pyomo_set
from pyomo.environ import ConcreteModel, Set


def generate_component_sets(instance: ConcreteModel, scenario: Scenario):
    """generates sets for components
    1. resources 
    2. processes and processes_full (containing storage charge and discharge processes)
    3. materials
    4. locations
    5. transport

    Args:
        instance (ConcreteModel): pyomo model
        scenario (Scenario): energiapy scenario
    """

    sets = scenario.set_dict

    instance.resources = Set(
        initialize=sets['resources'], doc='Set of resources')

    instance.processes = Set(
        initialize=sets['processes'], doc='Set of processes')
    instance.processes_full = Set(initialize=sets['processes_full'],
                                  doc='Set of all processes including dummy discharge')

    if len(scenario.material_set) > 0:
        instance.materials = Set(
            initialize=sets['materials'], doc='Set of materials')

    instance.locations = Set(
        initialize=sets['locations'], doc='Set of locations')

    if scenario.transport_set is not None:
        instance.transports = Set(
            initialize=sets['transports'], doc='Set of transports')