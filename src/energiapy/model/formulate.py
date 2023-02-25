"""Formulates models from Scenario  
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
from .sets import generate_sets
from .variables.schedule import *
from .variables.network import *
from .variables.binary import *
from .variables.cost import *
from .variables.transport import *
from .variables.uncertain import *
from .variables.mode import *
from .constraints.resource_balance import *
from .constraints.production import *
from .constraints.inventory import *
from .constraints.cost import *
from .constraints.land import *
from .constraints.emission import *
from .constraints.transport import *
from .constraints.failure import *
from .constraints.uncertain import *
from .objectives import *
from pyomo.environ import ConcreteModel
from typing import  Set


# class Variables(Enum):
#     network = auto()
#     schedule = auto()
#     binary = auto()
#     cost = auto()
#     transport = auto()
#     uncertain = auto()
    
class Constraints(Enum):
    cost = auto()
    emission = auto()
    failure = auto()
    inventory = auto()
    land = auto()
    production = auto()
    resource_balance = auto() 
    transport = auto()
    uncertain = auto()
    mode = auto()
    lifecycle = auto()

class Objective(Enum):
    cost = auto()
    demand = auto()
    
def formulate(scenario: Scenario, constraints:Set[Constraints], objective:Objective, demand:float = 0.0001,\
    land_restriction:float = 10**9, gwp:float = None, gwp_reduction_pct:float = None) -> ConcreteModel:
    """formulates a model

    Args:
        scenario (Scenario): scenario to formulate model over
        constraints (Set[Constraints]): constraints to include. 
        objective (Objective): objective 
        land_restriction (float, optional): restrict land usage. Defaults to 10**9.

    Constraints include:
            Constraints.cost 
            Constraints.emission 
            Constraints.failure 
            Constraints.inventory 
            Constraints.land 
            Constraints.production 
            Constraints.resource_balance  
            Constraints.transport 
            Constraints.uncertain 
    
    Objectives include:
            Objectives.cost
            Objectives.demand
            
    Returns:
        ConcreteModel: instance
    """

    if type(scenario.demand) is dict:
        demand = {i.name: {j.name: scenario.demand[i][j] for j in scenario.demand[i].keys()} for i in scenario.demand.keys()}
    else:
        demand = scenario.demand
        
    instance = ConcreteModel() 
    generate_sets(instance=instance, scenario= scenario)


    generate_scheduling_vars(instance=instance, scale_level=scenario.scheduling_scale_level, mode_dict= scenario.mode_dict)
    generate_network_vars(instance=instance, scale_level=scenario.network_scale_level)
    generate_network_binary_vars(instance=instance, scale_level=scenario.network_scale_level)
    generate_costing_vars(instance= instance)

    if Constraints.uncertain in constraints:
        generate_uncertainty_vars(instance = instance, scale_level = scenario.scheduling_scale_level)

        uncertain_process_capacity_constraint(instance = instance, capacity = scenario.prod_max, network_scale_level = scenario.network_scale_level)
        uncertain_resource_demand_constraint(instance = instance, demand = demand, scheduling_scale_level = scenario.scheduling_scale_level)
    
    if Constraints.mode in constraints:
        generate_mode_vars(instance=instance, scale_level=scenario.scheduling_scale_level, mode_dict= scenario.mode_dict)

    
    if len(scenario.location_set) > 1:
        generate_transport_vars(instance=instance, scale_level=scenario.scheduling_scale_level)
        
    if Constraints.cost in constraints:
        process_capex_constraint(instance=instance, capex_dict=scenario.capex_dict,
                             network_scale_level=scenario.network_scale_level)
        process_fopex_constraint(instance=instance, fopex_dict=scenario.fopex_dict,
                                network_scale_level=scenario.network_scale_level)
        process_vopex_constraint(instance=instance, vopex_dict=scenario.vopex_dict,
                                network_scale_level=scenario.network_scale_level)

        process_incidental_constraint(instance=instance, incidental_dict=scenario.incidental_dict,
                                network_scale_level=scenario.network_scale_level)

        
        location_capex_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)
        location_fopex_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)
        location_vopex_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)
        location_incidental_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)
        
        network_capex_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)
        network_fopex_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)
        network_vopex_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)
        
        network_incidental_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)
        
    if Constraints.emission in constraints:
        global_warming_potential_process_constraint(
            instance = instance, process_gwp_dict = scenario.process_gwp_dict, network_scale_level=scenario.network_scale_level)
        
        global_warming_potential_resource_constraint(
            instance = instance, resource_gwp_dict = scenario.resource_gwp_dict, network_scale_level=scenario.network_scale_level)

        global_warming_potential_material_constraint(
            instance = instance, material_gwp_dict = scenario.material_gwp_dict, process_material_dict = scenario.process_material_dict, network_scale_level=scenario.network_scale_level)

        global_warming_potential_location_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)

        global_warming_potential_network_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)

    if Constraints.failure in constraints:
        nameplate_production_failure_constraint(instance=instance, fail_factor=scenario.fail_factor,
                                network_scale_level=scenario.network_scale_level, scheduling_scale_level=scenario.scheduling_scale_level)

    if Constraints.inventory in constraints:
        nameplate_inventory_constraint(instance=instance, loc_res_dict=scenario.loc_res_dict, network_scale_level=scenario.network_scale_level,
                                scheduling_scale_level=scenario.scheduling_scale_level)

        storage_facility_constraint(instance=instance, store_max=scenario.store_max,
                            loc_res_dict=scenario.loc_res_dict, network_scale_level=scenario.network_scale_level)

        min_storage_facility_constraint(instance=instance, store_min=scenario.store_min,
                                        loc_res_dict=scenario.loc_res_dict, network_scale_level=scenario.network_scale_level)

    if Constraints.production in constraints:
        nameplate_production_constraint(instance=instance, capacity_factor=scenario.capacity_factor,
                                network_scale_level=scenario.network_scale_level, scheduling_scale_level=scenario.scheduling_scale_level)
        production_facility_constraint(instance=instance, prod_max=scenario.prod_max,
                                loc_pro_dict=scenario.loc_pro_dict, network_scale_level=scenario.network_scale_level)
        min_production_facility_constraint(instance=instance, prod_min=scenario.prod_min,
                                    loc_pro_dict=scenario.loc_pro_dict, network_scale_level=scenario.network_scale_level)

    if Constraints.land in constraints:
        process_land_constraint(instance=instance, land_dict=scenario.land_dict,
                        network_scale_level=scenario.network_scale_level)
        location_land_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)
        network_land_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)
        
        location_land_restriction_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level, land_restriction= land_restriction)

    if Constraints.resource_balance in constraints:
        
        inventory_balance_constraint(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                    conversion=scenario.conversion)

        resource_consumption_constraint(instance=instance, loc_res_dict=scenario.loc_res_dict,
                                cons_max=scenario.cons_max, scheduling_scale_level=scenario.scheduling_scale_level)
        
        resource_purchase_constraint(instance=instance, cost_factor=scenario.cost_factor, price=scenario.price,
                                    loc_res_dict=scenario.loc_res_dict, scheduling_scale_level=scenario.scheduling_scale_level,
                                    expenditure_scale_level=scenario.expenditure_scale_level)

        location_production_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level, cluster_wt=scenario.cluster_wt)
        location_discharge_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level, cluster_wt=scenario.cluster_wt)
        location_consumption_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level, cluster_wt=scenario.cluster_wt)
        location_purchase_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level, cluster_wt=scenario.cluster_wt)

        network_production_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)
        network_discharge_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)
        network_consumption_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)
        network_purchase_constraint(
            instance=instance, network_scale_level=scenario.network_scale_level)

    if Constraints.transport in constraints:
        
        if len(scenario.location_set) > 1:
            transport_export_constraint(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                        transport_avail_dict=scenario.transport_avail_dict)
            transport_import_constraint(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                        transport_avail_dict=scenario.transport_avail_dict)
            transport_exp_UB_constraint(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                        trans_max=scenario.trans_max, transport_avail_dict=scenario.transport_avail_dict)
            transport_imp_UB_constraint(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                        trans_max=scenario.trans_max, transport_avail_dict=scenario.transport_avail_dict)
            transport_balance_constraint(
                instance=instance, scheduling_scale_level=scenario.scheduling_scale_level)

            transport_exp_cost_constraint(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                        trans_cost=scenario.trans_cost, distance_dict=scenario.distance_dict)
            transport_imp_cost_constraint(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                        trans_cost=scenario.trans_cost, distance_dict=scenario.distance_dict)
            transport_cost_constraint(
                instance=instance, scheduling_scale_level=scenario.scheduling_scale_level)
            transport_cost_network_constraint(
                instance=instance, network_scale_level=scenario.network_scale_level)
    
    if gwp is not None:
        global_warming_potential_network_reduction_constraint(instance= instance, network_scale_level = scenario.network_scale_level\
            , gwp_reduction_pct = gwp_reduction_pct, gwp = gwp)

            
    if objective == Objective.cost:
        
        demand_constraint(instance=instance, demand_scale_level=scenario.demand_scale_level,
                    scheduling_scale_level=scenario.scheduling_scale_level, demand = demand, demand_factor=scenario.demand_factor)
        
        cost_objective(instance=instance,
                network_scale_level=scenario.network_scale_level)
        
        
    if objective == Objective.demand:
        demand_objective(instance=instance,
                network_scale_level=scenario.network_scale_level)
        
        
    return instance
    