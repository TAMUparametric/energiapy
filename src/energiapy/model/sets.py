"""pyomo sets
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from itertools import product

from pyomo.environ import ConcreteModel, Set

from ..components.scenario import Scenario


def generate_sets(instance: ConcreteModel, scenario: Scenario):
    """Generates pyomo sets based on declared lists.

    Creates the following sets:

    processes: Set of all processes

    processes_full: 'Set of all processes including dummy discharge'

    resources: Set of all resources

    resources_nosell: Set of non-dischargeable resources

    resources_sell: Set of dischargeable resources

    resources_store: Set of storeable resources

    resources_purch: Set of purchased resources

    resources_varying: Set of resources with varying purchase price

    resources_demand: Set of resources with exact demand

    resources_transport: Set of resource which can be transported

    processes_varying: Set of processes with varying capacity

    processes_failure: Set of processes which can fail

    processes_materials: Set of processes with material requirements

    processes_storage: Set of storage process

    processes_multim: Set of processes with multiple modes

    processes_singlem: Set of processes with multiple modes

    locations: Set of locations

    sources: Set of locations which act as sources

    sinks: Set of locations which act as sinks

    materials: Set of materials

    transports: Set of transportation options



    scales: Set of scales


    Args:
        instance (ConcreteModel): pyomo instance
        scenario (Scenario): scenario

    """

    instance.scales = Set(scenario.scales.list, initialize=scenario.scales.scale, doc='set of scales')

    sets = scenario.set_dict

    instance.processes = Set(initialize=sets['processes'], doc='Set of processes')
    instance.processes_full = Set(initialize=sets['processes_full'],
                                  doc='Set of all processes including dummy discharge')
    instance.resources = Set(initialize=sets['resources'], doc='Set of resources')
    instance.resources_nosell = Set(initialize=sets['resources_nosell'], doc='Set of non-dischargeable resources')
    instance.resources_sell = Set(initialize=sets['resources_sell'], doc='Set of dischargeable resources')
    instance.resources_store = Set(initialize=sets['resources_store'], doc='Set of storeable resources')
    instance.resources_purch = Set(initialize=sets['resources_purch'], doc='Set of purchased resources')
    instance.resources_varying_price = Set(initialize=sets['resources_varying_price'],
                                           doc='Set of resources with varying purchase price')
    instance.resources_varying_demand = Set(initialize=sets['resources_varying_demand'],
                                            doc='Set of resources with varying purchase price')
    instance.resources_demand = Set(initialize=sets['resources_demand'], doc='Set of resources with exact demand')
    instance.processes_varying = Set(initialize=sets['processes_varying'], doc='Set of processes with varying capacity')
    instance.processes_failure = Set(initialize=sets['processes_failure'], doc='Set of processes which can fail')
    instance.processes_materials = Set(initialize=sets['processes_materials'],
                                       doc='Set of processes with material requirements')
    instance.processes_storage = Set(initialize=sets['processes_storage'], doc='Set of storage process')
    instance.processes_multim = Set(initialize=sets['processes_multim'], doc='Set of processes with multiple modes')
    instance.processes_singlem = Set(initialize=sets['processes_singlem'], doc='Set of processes with multiple modes')
    instance.locations = Set(initialize=sets['locations'], doc='Set of locations')

    instance.resources_uncertain_price = Set(initialize=sets['resources_uncertain_price'],
                                             doc='Set of resources with uncertain purchase price')
    instance.resources_uncertain_demand = Set(initialize=sets['resources_uncertain_demand'],
                                              doc='Set of resources with uncertain demand')
    instance.processes_uncertain_capacity = Set(initialize=sets['processes_uncertain_capacity'],
                                                doc='Set of processes with uncertain capacity')

    mode_lens = []
    for i, j in product(scenario.process_set, scenario.location_set):
        mode_lens.append(len(scenario.prod_max[j.name][i.name].keys()))

    instance.modes = Set(initialize=list(range(max(mode_lens))), doc='Set of process modes')

    if scenario.source_locations is not None:
        instance.sources = Set(initialize=sets['sources'], doc='Set of sources')

    if scenario.sink_locations is not None:
        instance.sinks = Set(initialize=sets['sinks'], doc='Set of sinks')

    if len(scenario.material_set) > 0:
        instance.materials = Set(initialize=sets['materials'], doc='Set of materials')

    if scenario.transport_set is not None:
        instance.transports = Set(initialize=sets['transports'], doc='Set of transports')
        instance.resources_trans = Set(initialize=sets['resources_trans'], doc='Set of transportable resources')
    return
