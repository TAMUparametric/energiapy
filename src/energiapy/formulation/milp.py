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

from ..components.scenario import Scenario
from ..model.sets import generate_sets
from ..model.variables.schedule import *
from ..model.variables.network import *
from ..model.variables.binary import *
from ..model.variables.cost import *
from ..model.variables.transport import *
from src.energiapy.model.constraints.resource_balance import *
from src.energiapy.model.constraints.production import *
from src.energiapy.model.constraints.inventory import *
from src.energiapy.model.constraints.cost import *
from src.energiapy.model.constraints.land import *
from src.energiapy.model.constraints.emission import *
from src.energiapy.model.constraints.transport import *
from ..model.objectives import cost_objective
from pyomo.environ import ConcreteModel


class IncludeVars(Enum):
    network = auto()
    schedule = auto()
    binary = auto()
    cost = auto()
    transport = auto()
    
    
    
    
class IncludeCons(Enum):
    network = auto()
    schedule = auto()
    binary = auto()
    

def formulate_milp(scenario: Scenario) -> ConcreteModel:
    """formulates a multi-scale mixed integer linear programming formulation of the scenario

    Args:
        scenario (Scenario): scenario under consideration

    Returns:
        ConcreteModel: pyomo model instance with sets, variables, constraints, objectives generated
    """

    instance = ConcreteModel()

    generate_sets(instance=instance, location_set=scenario.location_set, transport_set=scenario.transport_set, scales=scenario.scales,
                  process_set=scenario.process_set, resource_set=scenario.resource_set, material_set=scenario.material_set,
                  source_set=scenario.source_locations, sink_set=scenario.sink_locations)

    generate_scheduling_vars(
        instance=instance, scale_level=scenario.scheduling_scale_level)
    generate_network_vars(
        instance=instance, scale_level=scenario.network_scale_level)
    generate_network_binary_vars(
        instance=instance, scale_level=scenario.network_scale_level)

    if len(instance.locations) > 1:
        generate_transport_vars(
            instance=instance, scale_level=scenario.scheduling_scale_level)

    inventory_balance_constraint(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                 conversion=scenario.conversion)
    nameplate_production_constraint(instance=instance, capacity_factor=scenario.capacity_factor,
                                    network_scale_level=scenario.network_scale_level, scheduling_scale_level=scenario.scheduling_scale_level)
    nameplate_inventory_constraint(instance=instance, loc_res_dict=scenario.loc_res_dict, network_scale_level=scenario.network_scale_level,
                                   scheduling_scale_level=scenario.scheduling_scale_level)
    resource_consumption_constraint(instance=instance, loc_res_dict=scenario.loc_res_dict,
                                    cons_max=scenario.cons_max, scheduling_scale_level=scenario.scheduling_scale_level)
    resource_purchase_constraint(instance=instance, cost_factor=scenario.cost_factor, price=scenario.price,
                                 loc_res_dict=scenario.loc_res_dict, scheduling_scale_level=scenario.scheduling_scale_level,
                                 expenditure_scale_level=scenario.expenditure_scale_level)
    # resource_discharge_constraint(instance= instance, scheduling_scale_level= scenario.scheduling_scale_level)

    production_facility_constraint(instance=instance, prod_max=scenario.prod_max,
                                   loc_pro_dict=scenario.loc_pro_dict, network_scale_level=scenario.network_scale_level)
    storage_facility_constraint(instance=instance, store_max=scenario.store_max,
                                loc_res_dict=scenario.loc_res_dict, network_scale_level=scenario.network_scale_level)

    min_production_facility_constraint(instance=instance, prod_min=scenario.prod_min,
                                       loc_pro_dict=scenario.loc_pro_dict, network_scale_level=scenario.network_scale_level)
    min_storage_facility_constraint(instance=instance, store_min=scenario.store_min,
                                    loc_res_dict=scenario.loc_res_dict, network_scale_level=scenario.network_scale_level)

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

    process_capex_constraint(instance=instance, capex_dict=scenario.capex_dict,
                             network_scale_level=scenario.network_scale_level)
    process_fopex_constraint(instance=instance, fopex_dict=scenario.fopex_dict,
                             network_scale_level=scenario.network_scale_level)
    process_vopex_constraint(instance=instance, vopex_dict=scenario.vopex_dict,
                             network_scale_level=scenario.network_scale_level)

    process_land_constraint(instance=instance, land_dict=scenario.land_dict,
                            network_scale_level=scenario.network_scale_level)
    location_land_constraint(
        instance=instance, network_scale_level=scenario.network_scale_level)
    network_land_constraint(
        instance=instance, network_scale_level=scenario.network_scale_level)

    location_capex_constraint(
        instance=instance, network_scale_level=scenario.network_scale_level)
    location_fopex_constraint(
        instance=instance, network_scale_level=scenario.network_scale_level)
    location_vopex_constraint(
        instance=instance, network_scale_level=scenario.network_scale_level)

    network_capex_constraint(
        instance=instance, network_scale_level=scenario.network_scale_level)
    network_fopex_constraint(
        instance=instance, network_scale_level=scenario.network_scale_level)
    network_vopex_constraint(
        instance=instance, network_scale_level=scenario.network_scale_level)

    demand_constraint(instance=instance, demand_scale_level=scenario.demand_scale_level,
                      scheduling_scale_level=scenario.scheduling_scale_level, demand=scenario.demand)

    carbon_emission_location_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    carbon_emission_network_constraint(instance= instance, network_scale_level= scenario.network_scale_level)


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

    

    cost_objective(instance=instance,
                   network_scale_level=scenario.network_scale_level)

    return instance
