"""Formulates a multiscale mixed integer linear programming (MILP) model from Scenario  
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

import resource
from ..components.scenario import Scenario
from ..model.pyomo_sets import generate_sets
from ..model.pyomo_vars import generate_milp_vars
from ..model.pyomo_cons import *
from pyomo.environ import ConcreteModel

    
def formulate_milp(scenario: Scenario) -> ConcreteModel:
    """formulates a multi-scale mixed integer linear programming formulation of the scenario
    
    Args:
        scenario (Scenario): scenario under consideration

    Returns:
        ConcreteModel: pyomo model instance with sets, variables, constraints, objectives generated
    """
    
    instance = ConcreteModel()
    generate_sets(instance= instance, location_set= scenario.location_set, transport_set= scenario.transport_set, scales= scenario.scales, \
        process_set= scenario.process_set, resource_set= scenario.resource_set, material_set= scenario.material_set, \
            source_set= scenario.source_locations, sink_set= scenario.sink_locations)
    generate_milp_vars(instance= instance, expenditure_scale_level= scenario.expenditure_scale_level, \
        scheduling_scale_level = scenario.scheduling_scale_level, network_scale_level= scenario.network_scale_level)
    # test_cycle(instance= instance, location_set= scenario.location_set, scheduling_scale_level= scenario.scheduling_scale_level)
    inventory_balance_constraint(instance= instance, location_set= scenario.location_set, scheduling_scale_level= scenario.scheduling_scale_level)
    nameplate_production_constraint(instance= instance, location_set= scenario.location_set, network_scale_level= \
        scenario.network_scale_level, scheduling_scale_level= scenario.scheduling_scale_level)
    nameplate_inventory_constraint(instance= instance, location_set= scenario.location_set, network_scale_level= scenario.network_scale_level,\
        scheduling_scale_level= scenario.scheduling_scale_level)
    resource_consumption_constraint(instance= instance, location_set= scenario.location_set, scheduling_scale_level= scenario.scheduling_scale_level)
    resource_expenditure_constraint(instance= instance, location_set= scenario.location_set, scheduling_scale_level= scenario.scheduling_scale_level,\
        expenditure_scale_level= scenario.expenditure_scale_level)
    resource_discharge_constraint(instance= instance, location_set= scenario.location_set, scheduling_scale_level= scenario.scheduling_scale_level)
    
    return instance
