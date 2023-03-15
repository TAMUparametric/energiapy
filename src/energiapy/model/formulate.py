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
from .constraints.mode import *
from .objectives import *
from pyomo.environ import ConcreteModel
from typing import  Set


class Constraints(Enum):
    """Class of constraints

    Args:
        Enum (auto): choose set of contraints to add
    """
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
    """Class of objective

    Args:
        Enum (auto): cost, demand, etc.
    """
    cost = auto()
    demand = auto()
    
def formulate(scenario: Scenario, constraints:Set[Constraints], objective:Objective, demand:float = 0.0001, gwp:float = None,  land_restriction: float = None, gwp_reduction_pct:float = None) -> ConcreteModel:
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

    if type(demand) is dict:
        demand = {i.name: {j.name: demand[i][j] for j in demand[i].keys()} for i in demand.keys()}
        
    instance = ConcreteModel() 
    generate_sets(instance=instance, scenario= scenario)


    generate_scheduling_vars(instance=instance, scale_level=scenario.scheduling_scale_level, mode_dict= scenario.mode_dict)
    generate_network_vars(instance=instance, scale_level=scenario.network_scale_level)
    generate_network_binary_vars(instance=instance, scale_level=scenario.network_scale_level)
    generate_costing_vars(instance= instance)

    if Constraints.uncertain in constraints:
        generate_uncertainty_vars(instance = instance, scale_level = scenario.scheduling_scale_level)

        constraint_uncertain_process_capacity(instance = instance, capacity = scenario.prod_max, network_scale_level = scenario.network_scale_level)
        constraint_uncertain_resource_demand(instance = instance, demand = demand, scheduling_scale_level = scenario.scheduling_scale_level)
    
    if Constraints.mode in constraints:
        generate_mode_vars(instance= instance, scale_level=scenario.scheduling_scale_level, mode_dict= scenario.mode_dict)
        
        constraint_production_mode(instance= instance, mode_dict= scenario.mode_dict, scheduling_scale_level= scenario.scheduling_scale_level)
    
    if len(scenario.location_set) > 1:
        generate_transport_vars(instance=instance, scale_level=scenario.scheduling_scale_level)
        
    if Constraints.cost in constraints:
        constraint_process_capex(instance=instance, capex_dict=scenario.capex_dict,
                             network_scale_level=scenario.network_scale_level)
        constraint_process_fopex(instance=instance, fopex_dict=scenario.fopex_dict,
                                network_scale_level=scenario.network_scale_level)
        constraint_process_vopex(instance=instance, vopex_dict=scenario.vopex_dict,
                                network_scale_level=scenario.network_scale_level)

        constraint_process_incidental(instance=instance, incidental_dict=scenario.incidental_dict,
                                network_scale_level=scenario.network_scale_level)

        
        constraint_location_capex(
            instance=instance, network_scale_level=scenario.network_scale_level)
        constraint_location_fopex(
            instance=instance, network_scale_level=scenario.network_scale_level)
        constraint_location_vopex(
            instance=instance, network_scale_level=scenario.network_scale_level)
        constraint_location_incidental(
            instance=instance, network_scale_level=scenario.network_scale_level)
        
        constraint_network_capex(
            instance=instance, network_scale_level=scenario.network_scale_level)
        constraint_network_fopex(
            instance=instance, network_scale_level=scenario.network_scale_level)
        constraint_network_vopex(
            instance=instance, network_scale_level=scenario.network_scale_level)
        
        constraint_network_incidental(
            instance=instance, network_scale_level=scenario.network_scale_level)
        
    if Constraints.emission in constraints:
        constraint_global_warming_potential_process(
            instance = instance, process_gwp_dict = scenario.process_gwp_dict, network_scale_level=scenario.network_scale_level)
        
        constraint_global_warming_potential_resource(
            instance = instance, resource_gwp_dict = scenario.resource_gwp_dict, network_scale_level=scenario.network_scale_level)

        constraint_global_warming_potential_material(
            instance = instance, material_gwp_dict = scenario.material_gwp_dict, process_material_dict = scenario.process_material_dict, network_scale_level=scenario.network_scale_level)

        constraint_global_warming_potential_location(
            instance=instance, network_scale_level=scenario.network_scale_level)

        constraint_global_warming_potential_network(
            instance=instance, network_scale_level=scenario.network_scale_level)

    if Constraints.failure in constraints:
        constraint_nameplate_production_failure(instance=instance, fail_factor=scenario.fail_factor,
                                network_scale_level=scenario.network_scale_level, scheduling_scale_level=scenario.scheduling_scale_level)

    if Constraints.inventory in constraints:
        constraint_nameplate_inventory(instance=instance, loc_res_dict=scenario.loc_res_dict, network_scale_level=scenario.network_scale_level,
                                scheduling_scale_level=scenario.scheduling_scale_level)

        constraint_storage_facility(instance=instance, store_max=scenario.store_max,
                            loc_res_dict=scenario.loc_res_dict, network_scale_level=scenario.network_scale_level)

        constraint_min_storage_facility(instance=instance, store_min=scenario.store_min,
                                        loc_res_dict=scenario.loc_res_dict, network_scale_level=scenario.network_scale_level)

    if Constraints.production in constraints:
        constraint_nameplate_production(instance=instance, capacity_factor=scenario.capacity_factor, loc_pro_dict=scenario.loc_pro_dict,
                                network_scale_level=scenario.network_scale_level, scheduling_scale_level=scenario.scheduling_scale_level)
        constraint_production_facility(instance=instance, prod_max=scenario.prod_max,
                                loc_pro_dict=scenario.loc_pro_dict, network_scale_level=scenario.network_scale_level)
        constraint_min_production_facility(instance=instance, prod_min=scenario.prod_min,
                                    loc_pro_dict=scenario.loc_pro_dict, network_scale_level=scenario.network_scale_level)

    if Constraints.land in constraints:
        constraint_process_land(instance=instance, land_dict=scenario.land_dict,
                        network_scale_level=scenario.network_scale_level)
        constraint_location_land(
            instance=instance, network_scale_level=scenario.network_scale_level)
        constraint_network_land(
            instance=instance, network_scale_level=scenario.network_scale_level)
        
        constraint_process_land_cost(instance=instance, land_dict=scenario.land_dict, land_cost_dict = scenario.land_cost_dict,\
            network_scale_level=scenario.network_scale_level)
        constraint_location_land_cost(
            instance=instance, network_scale_level=scenario.network_scale_level)
        constraint_network_land_cost(
            instance=instance, network_scale_level=scenario.network_scale_level)
        
        if land_restriction is not None:
            constraint_location_land_restriction(instance=instance, network_scale_level=scenario.network_scale_level, land_restriction= land_restriction)

    if Constraints.resource_balance in constraints:
        
        constraint_inventory_balance(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                    multiconversion=scenario.multiconversion, mode_dict= scenario.mode_dict)

        constraint_resource_consumption(instance=instance, loc_res_dict=scenario.loc_res_dict,
                                cons_max=scenario.cons_max, scheduling_scale_level=scenario.scheduling_scale_level)
        
        constraint_resource_purchase(instance=instance, cost_factor=scenario.cost_factor, price=scenario.price,
                                    loc_res_dict=scenario.loc_res_dict, scheduling_scale_level=scenario.scheduling_scale_level,
                                    expenditure_scale_level=scenario.expenditure_scale_level)

        constraint_location_production(
            instance=instance, network_scale_level=scenario.network_scale_level, cluster_wt=scenario.cluster_wt)
        constraint_location_discharge(
            instance=instance, network_scale_level=scenario.network_scale_level, cluster_wt=scenario.cluster_wt)
        constraint_location_consumption(
            instance=instance, network_scale_level=scenario.network_scale_level, cluster_wt=scenario.cluster_wt)
        constraint_location_purchase(
            instance=instance, network_scale_level=scenario.network_scale_level, cluster_wt=scenario.cluster_wt)

        constraint_network_production(
            instance=instance, network_scale_level=scenario.network_scale_level)
        constraint_network_discharge(
            instance=instance, network_scale_level=scenario.network_scale_level)
        constraint_network_consumption(
            instance=instance, network_scale_level=scenario.network_scale_level)
        constraint_network_purchase(
            instance=instance, network_scale_level=scenario.network_scale_level)

    if Constraints.transport in constraints:
        
        if len(scenario.location_set) > 1:
            constraint_transport_export(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                        transport_avail_dict=scenario.transport_avail_dict)
            constraint_transport_import(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                        transport_avail_dict=scenario.transport_avail_dict)
            constraint_transport_exp_UB(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                        trans_max=scenario.trans_max, transport_avail_dict=scenario.transport_avail_dict)
            constraint_transport_imp_UB(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                        trans_max=scenario.trans_max, transport_avail_dict=scenario.transport_avail_dict)
            constraint_transport_balance(
                instance=instance, scheduling_scale_level=scenario.scheduling_scale_level)

            constraint_transport_imp_cost(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                        trans_cost=scenario.trans_cost, distance_dict=scenario.distance_dict)
            constraint_transport_cost(
                instance=instance, scheduling_scale_level=scenario.scheduling_scale_level)
            constraint_transport_cost_network(
                instance=instance, network_scale_level=scenario.network_scale_level)
    
    if gwp is not None:
        constraint_global_warming_potential_network_reduction(instance= instance, network_scale_level = scenario.network_scale_level\
            , gwp_reduction_pct = gwp_reduction_pct, gwp = gwp)

            
    if objective == Objective.cost:
        
        constraint_demand(instance=instance, demand_scale_level=scenario.demand_scale_level,
                    scheduling_scale_level=scenario.scheduling_scale_level, demand = demand, demand_factor=scenario.demand_factor)
        
        cost_objective(instance=instance,
                network_scale_level=scenario.network_scale_level)
        
        
    if objective == Objective.demand:
        demand_objective(instance=instance,
                network_scale_level=scenario.network_scale_level)
        
        
    return instance
    