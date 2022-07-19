"""Formulates a multiparameteric mixed integer linear programming model (mpMILP) from Scenario  
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from ..components.scenario import Scenario
from ..model.pyomo_sets import generate_sets
from ..model.pyomo_vars import generate_mpmilp_vars
from ..model.pyomo_cons import *
from ..model.pyomo_objs import cost_objective
from pyomo.environ import ConcreteModel
    
      
def formulate_mpmilp(scenario: Scenario) -> ConcreteModel:
    """formulates a multi-scale multi-parametric mixed integer linear programming formulation of the scenario
    
    Args:
        scenario (Scenario): scenario under consideration

    Returns:
        ConcreteModel: pyomo model instance with sets, variables, constraints, objectives generated
    """
    instance = ConcreteModel()
    generate_sets(instance= instance, location_set= scenario.location_set, transport_set= scenario.transport_set, scales= scenario.scales, \
        process_set= scenario.process_set, resource_set= scenario.resource_set, material_set= scenario.material_set, \
            source_set= scenario.source_locations, sink_set= scenario.sink_locations)
    generate_mpmilp_vars(instance= instance, expenditure_scale_level= scenario.expenditure_scale_level, scheduling_scale_level = scenario.scheduling_scale_level \
        , network_scale_level= scenario.network_scale_level)
    
    inventory_balance_constraint(instance= instance, scheduling_scale_level= scenario.scheduling_scale_level,\
        conversion= scenario.conversion)
    
    uncertain_nameplate_production_constraint(instance= instance, network_scale_level= scenario.network_scale_level, scheduling_scale_level= scenario.scheduling_scale_level)
    nameplate_inventory_constraint(instance= instance, loc_res_dict= scenario.loc_res_dict, network_scale_level= scenario.network_scale_level,\
        scheduling_scale_level= scenario.scheduling_scale_level)
    
    resource_consumption_constraint(instance= instance, loc_res_dict= scenario.loc_res_dict, cons_max= scenario.cons_max, scheduling_scale_level= scenario.scheduling_scale_level)
    uncertain_resource_purchase_constraint(instance= instance, price= scenario.price, loc_res_dict= scenario.loc_res_dict, \
        scheduling_scale_level= scenario.scheduling_scale_level, expenditure_scale_level= scenario.expenditure_scale_level)
    resource_discharge_constraint(instance= instance, scheduling_scale_level= scenario.scheduling_scale_level)
    
    production_facility_constraint(instance= instance, prod_max= scenario.prod_max, loc_pro_dict= scenario.loc_pro_dict, network_scale_level= scenario.network_scale_level)
    storage_facility_constraint(instance= instance, store_max= scenario.store_max, loc_res_dict= scenario.loc_res_dict, network_scale_level= scenario.network_scale_level)
    
    location_production_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    location_discharge_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    location_consumption_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    location_purchase_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    

    network_production_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    network_discharge_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    network_consumption_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    network_purchase_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    
 
    process_capex_constraint(instance= instance, capex_dict= scenario.capex_dict, network_scale_level= scenario.network_scale_level)
    process_fopex_constraint(instance= instance, fopex_dict= scenario.fopex_dict, network_scale_level= scenario.network_scale_level)
    process_vopex_constraint(instance= instance, vopex_dict= scenario.vopex_dict, network_scale_level= scenario.network_scale_level)

    location_capex_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    location_fopex_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    location_vopex_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    
    network_capex_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    network_fopex_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    network_vopex_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    
    demand_constraint(instance= instance, demand_scale_level= scenario.demand_scale_level, scheduling_scale_level= scenario.scheduling_scale_level, demand_dict= scenario.demand_dict)
    
    cost_objective(instance= instance, network_scale_level= scenario.network_scale_level)
    
    
    return instance
       