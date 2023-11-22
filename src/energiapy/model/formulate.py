"""Formulates models from Scenario
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from enum import Enum, auto
from typing import Set, Dict, Tuple
from pyomo.environ import ConcreteModel, Suffix

from ..components.scenario import Scenario
from ..components.resource import Resource
from ..components.location import Location
from ..components.process import Process
from .constraints.constraints import Constraints, make_constraint, Cons

from .constraints.cost import (
    constraint_location_capex,
    constraint_location_fopex,
    constraint_location_incidental,
    constraint_land_location_cost,
    constraint_location_vopex,
    constraint_network_capex,
    constraint_network_fopex,
    constraint_network_incidental,
    constraint_land_network_cost,
    constraint_network_vopex,
    constraint_process_capex,
    constraint_process_fopex,
    constraint_process_incidental,
    constraint_land_process_cost,
    constraint_process_vopex,
    constraint_transport_cost,
    constraint_transport_cost_network,
    constraint_transport_imp_cost,
    constraint_network_cost,
    constraint_resource_purchase,
    constraint_resource_revenue,
    constraint_location_purchase,
    constraint_location_revenue,
    constraint_network_revenue,
    constraint_network_purchase,
    constraint_storage_cost,
    constraint_storage_cost_location,
    constraint_storage_cost_network,
)
from .constraints.emission import (
    constraint_global_warming_potential_location,
    constraint_global_warming_potential_material,
    constraint_global_warming_potential_material_mode,
    constraint_global_warming_potential_network,
    constraint_global_warming_potential_network_reduction,
    constraint_global_warming_potential_process,
    constraint_global_warming_potential_resource,
)
from .constraints.failure import constraint_nameplate_production_failure
from .constraints.inventory import (
    constraint_nameplate_inventory,
    constraint_storage_max,
    constraint_storage_min,
)
from .constraints.land import (
    constraint_land_location,
    constraint_land_location_restriction,
    constraint_land_network,
    constraint_land_process,
)
from .constraints.mode import (
    constraint_production_mode,
    constraint_production_mode_binary,
    constraint_production_mode_facility,
    constraint_min_production_mode_facility,
    constraint_production_rate1,
    constraint_production_rate2,
    constraint_production_mode_switch

)
from .constraints.production import (
    constraint_nameplate_production,
    constraint_production_max,
    constraint_production_min,
    constraint_nameplate_production_material_mode
)
from .constraints.resource_balance import (
    constraint_inventory_balance,
    constraint_location_consumption,
    constraint_location_discharge,
    constraint_location_production,
    constraint_network_consumption,
    constraint_network_discharge,
    constraint_network_production,
    constraint_resource_consumption,
    constraint_inventory_network,
    constraint_location_production_material_mode,
    constraint_location_production_material_mode_sum
)

from .constraints.demand import (
    constraint_demand,
    constraint_demand_penalty
)
from .constraints.transport import (
    # constraint_transport_balance,
    # constraint_transport_exp_UB,
    # constraint_transport_export,
    # constraint_transport_imp_UB,
    # constraint_transport_import,
    constraint_transport_export,
    constraint_resource_export,
    constraint_export,
    constraint_transport_capacity_LB,
    constraint_transport_capacity_UB,
    constraint_transport_capex,
    constraint_transport_network_capex,
    constraint_transport_export_network,
    constraint_transport_vopex,
    constraint_transport_network_vopex,
    constraint_transport_fopex,
    constraint_transport_network_fopex
)
from .constraints.uncertain import (
    constraint_uncertain_process_capacity,
    constraint_uncertain_resource_demand,
)
from .constraints.network import (
    constraint_storage_facility,
    constraint_production_facility,
    constraint_min_storage_facility,
    constraint_min_production_facility,
    constraint_min_capacity_facility,
    constraint_preserve_capacity_facility
)
from .constraints.credit import (
    constraint_credit_process,
    constraint_credit_location,
    constraint_credit_network
)
from .constraints.material import (
    constraint_material_process,
    constraint_material_location,
    constraint_material_network,
    constraint_production_facility_material_mode_binary,
    constraint_production_facility_material_mode,
    constraint_production_facility_material,
    constraint_min_production_facility_material,
    constraint_material_mode_process
)
from .objectives import (
    objective_cost,
    objective_discharge_max,
    objective_discharge_min,
    objective_profit,
    objective_gwp_min,
    objective_cost_w_demand_penalty,
    objective_profit_w_demand_penalty
)

from .sets import generate_sets
from .variables.binary import generate_network_binary_vars
from .variables.cost import generate_costing_vars
from .variables.mode import generate_mode_vars
from .variables.network import generate_network_vars
from .variables.schedule import generate_scheduling_vars
from .variables.transport import generate_transport_vars
from .variables.uncertain import generate_uncertainty_vars
from .variables.credit import generate_credit_vars
from .variables.land import generate_land_vars
from .variables.emission import generate_emission_vars
from .variables.material import generate_material_vars
from .variables.demand import generate_demand_vars


class ModelClass(Enum):
    """Class of model
    """
    MIP = auto()
    """
    Mixed integer programming
    """
    MPLP = auto()
    """
    multi-parametric linear programming
    """


class Objective(Enum):
    """
    Objective type
    """
    COST = auto()
    """
    Minimize cost
    """
    PROFIT = auto()
    """
    Maximize profit
    """
    MIN_DISCHARGE = auto()
    """
    Minimize discharge of particular resource
    """
    MAX_DISCHARGE = auto()
    """
    Minimize discharge of particular resource
    """
    MIN_GWP = auto()
    """
    Minimize global warming potential across network (includes resource, material, process emissions)
    """
    COST_W_DEMAND_PENALTY = auto()
    """
    Minimize cost with penalty for unmet resource demand
    """
    PROFIT_W_DEMAND_PENALTY = auto()
    """
    Maximized profit with penalty for unmet resource demand
    """


def formulate(scenario: Scenario, constraints: Set[Constraints] = None, objective: Objective = None,
              write_lpfile: bool = False, gwp: float = None, land_restriction: float = None,
              gwp_reduction_pct: float = None, model_class: ModelClass = ModelClass.MIP, objective_resource: Resource = None,
              inventory_zero: Dict[Location,
                                   Dict[Tuple[Process, Resource], float]] = None,
              demand_sign: str = 'geq') -> ConcreteModel:
    """formulates a model. Constraints need to be declared in order

    Args:
        scenario (Scenario): scenario to formulate model over
        constraints (Set[Constraints], optional): constraints to include. Defaults to None
        objective (Objective, optional): objective. Defaults to None
        write_lpfile (bool, False): write out a .LP file. Uses scenario.name as name.
        gwp (float, optional): _description_. Defaults to None.
        land_restriction (float, optional): restrict land usage. Defaults to 10**9.
        gwp_reduction_pct (float, optional): percentage reduction in gwp required. Defaults to None.
        model_class (ModelClass, optional): class of model [MIP, mpLP]. Defaults to ModelClass.MIP
        objective_resource (Resource, None): resource to feature in objective for maximization and such
        inventory_zero (Dict[Location, Dict[Tuple[Process, Resource], float]], optional): inventory at the start of the scheduling horizon. Defaults to None.
        demand_sign (str, optional): Should the supply be greater('geq')/lesser('leq')/equal('eq') to the demand. Defaults to 'geq'

    Constraints include:
            Constraints.COST
            Constraints.EMISSION
            Constraints.FAILURE
            Constraints.INVENTORY
            Constraints.LAND
            Constraints.PRODUCTION
            Constraints.RESOURCE_BALANCE
            Constraints.TRANSPORT
            Constraints.UNCERTAIN
            Constraints.NETWORK
            Constraints.MODE
            Constraints.CREDIT
            Constraints.MATERIAL
            Constraints.PRESERVE_NETWORK
            Constraints.DEMAND

    Objectives include:
            Objectives.COST
            Objectives.PROFIT
            Objectives.MIN_DISCHARGE
            Objectives.MAX_DISCHARGE

    Returns:
        ConcreteModel: pyomo instance
    """

    demand = scenario.demand
    # if isinstance(demand, dict):
    #     demand = {i.name: {j.name: demand[i][j]
    #                        for j in demand[i].keys()} for i in demand.keys()}
    if isinstance(demand, dict):
        if isinstance(list(demand.keys())[0], Location):
            try:
                demand = {i.name: {
                    j.name: demand[i][j] for j in demand[i].keys()} for i in demand.keys()}
            except:
                pass
    if model_class is ModelClass.MIP:

        instance = ConcreteModel()
        generate_sets(instance=instance, scenario=scenario)

        generate_scheduling_vars(
            instance=instance, scale_level=scenario.scheduling_scale_level, mode_dict=scenario.mode_dict)
        generate_network_vars(
            instance=instance, scale_level=scenario.network_scale_level)
        generate_costing_vars(instance=instance)

        generate_material_vars(
            instance=instance, scale_level=scenario.network_scale_level)

        if Constraints.UNCERTAIN in constraints:
            generate_uncertainty_vars(
                instance=instance, scale_level=scenario.scheduling_scale_level)

            constraint_uncertain_process_capacity(
                instance=instance, capacity=scenario.prod_max, network_scale_level=scenario.network_scale_level)
            constraint_uncertain_resource_demand(
                instance=instance, demand=demand, scheduling_scale_level=scenario.scheduling_scale_level)

        if len(scenario.location_set) > 1:
            generate_transport_vars(instance=instance)

        if Constraints.COST in constraints:
            constraint_process_capex(instance=instance, capex_dict=scenario.capex_dict,
                                     network_scale_level=scenario.expenditure_scale_level, capex_factor=scenario.capex_factor, annualization_factor=scenario.annualization_factor)
            constraint_process_fopex(instance=instance, fopex_dict=scenario.fopex_dict,
                                     network_scale_level=scenario.expenditure_scale_level, fopex_factor=scenario.fopex_factor)
            constraint_process_vopex(instance=instance, vopex_dict=scenario.vopex_dict,
                                     network_scale_level=scenario.expenditure_scale_level, vopex_factor=scenario.vopex_factor)
            constraint_process_incidental(instance=instance, incidental_dict=scenario.incidental_dict,
                                          network_scale_level=scenario.network_scale_level)

            # constraint_location_capex(
            #     instance=instance, network_scale_level=scenario.network_scale_level)
            # constraint_location_fopex(
            #     instance=instance, network_scale_level=scenario.network_scale_level)
            # constraint_location_vopex(
            #     instance=instance, network_scale_level=scenario.network_scale_level)
            # constraint_location_incidental(
            #     instance=instance, network_scale_level=scenario.network_scale_level)

            # *----------------sum capex, fopex, vopex, incidental costs over location ---------------------------------------------

            instance.constraint_location_capex = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMLOCCOST_Y, variable_x='Capex_location', variable_y='Capex_process', location_set=instance.locations, component_set=instance.processes,
                loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up capex from process over a location')

            instance.constraint_location_fopex = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMLOCCOST_Y, variable_x='Fopex_location', variable_y='Fopex_process', location_set=instance.locations, component_set=instance.processes,
                loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up fopex from process over a locations')

            instance.constraint_location_vopex = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMLOCCOST_Y, variable_x='Vopex_location', variable_y='Vopex_process', location_set=instance.locations, component_set=instance.processes,
                loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up vopex from process over a locations')

            instance.constraint_location_incidental = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMLOCCOST_Y, variable_x='Incidental_location', variable_y='Incidental_process', location_set=instance.locations, component_set=instance.processes,
                loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up incidental expenditure from process over a location')

            # constraint_network_capex(
            #     instance=instance, network_scale_level=scenario.network_scale_level)
            # constraint_network_fopex(
            #     instance=instance, network_scale_level=scenario.network_scale_level)
            # constraint_network_vopex(
            #     instance=instance, network_scale_level=scenario.network_scale_level)
            # constraint_network_incidental(
            #     instance=instance, network_scale_level=scenario.network_scale_level)

            # *----------------sum capex, fopex, vopex, incidental costs over network ---------------------------------------------

            instance.constraint_network_capex = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMCOST_Y, variable_x='Capex_network', variable_y='Capex_location', location_set=instance.locations, component_set=instance.processes,
                loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up capex from process over all locations in network')

            instance.constraint_network_fopex = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMCOST_Y, variable_x='Fopex_network', variable_y='Fopex_location', location_set=instance.locations, component_set=instance.processes,
                loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up fopex from process over all locations in network')

            instance.constraint_network_vopex = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMCOST_Y, variable_x='Vopex_network', variable_y='Vopex_location', location_set=instance.locations, component_set=instance.processes,
                loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up vopex from process over all locations in network')

            instance.constraint_network_incidental = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMCOST_Y, variable_x='Incidental_network', variable_y='Incidental_location', location_set=instance.locations, component_set=instance.processes,
                loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up incidental expenditure from process over all locations in network')

            instance.constraint_storage_cost = constraint_storage_cost(
                instance=instance, location_resource_dict=scenario.location_resource_dict, storage_cost_dict=scenario.storage_cost_dict, network_scale_level=scenario.network_scale_level)

            instance.constraint_storage_cost_location = constraint_storage_cost_location(
                instance=instance, network_scale_level=scenario.network_scale_level)

            instance.constraint_storage_cost_network = constraint_storage_cost_network(
                instance=instance, network_scale_level=scenario.network_scale_level)

        if Constraints.EMISSION in constraints:
            generate_emission_vars(
                instance=instance, scale_level=scenario.network_scale_level)

            constraint_global_warming_potential_process(
                instance=instance, process_gwp_dict=scenario.process_gwp_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_global_warming_potential_resource(
                instance=instance, resource_gwp_dict=scenario.resource_gwp_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_global_warming_potential_location(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_global_warming_potential_network(
                instance=instance, network_scale_level=scenario.network_scale_level)

            if Constraints.MATERIAL in constraints:

                constraint_global_warming_potential_material(
                    instance=instance, network_scale_level=scenario.network_scale_level)

                constraint_global_warming_potential_material_mode(instance=instance, material_gwp_dict=scenario.material_gwp_dict,
                                                                  process_material_mode_material_dict=scenario.process_material_mode_material_dict,
                                                                  network_scale_level=scenario.network_scale_level)

        if Constraints.FAILURE in constraints:
            constraint_nameplate_production_failure(instance=instance, fail_factor=scenario.fail_factor,
                                                    network_scale_level=scenario.network_scale_level,
                                                    scheduling_scale_level=scenario.scheduling_scale_level)

        if Constraints.INVENTORY in constraints:
            instance.constraint_nameplate_inventory = make_constraint(instance=instance, type_cons=Cons.X_LEQ_Y, variable_x='Inv',
                                                                      location_set=instance.locations, component_set=instance.resources_store,  loc_comp_dict=scenario.location_resource_dict,
                                                                      x_scale_level=scenario.scheduling_scale_level, y_scale_level=scenario.network_scale_level, variable_y='Cap_S', label='restricts inventory to certain nameplate capacity')

            # *----------------inventory bounds ---------------------------------------------

            instance.constraint_storage_max = make_constraint(instance=instance, type_cons=Cons.X_LEQ_B, variable_x='Cap_S', b_max=scenario.store_max, location_set=instance.locations, component_set=instance.resources_store,
                                                              loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, label='restricts nameplate inventory to some UB')

            instance.constraint_storage_min = make_constraint(instance=instance, type_cons=Cons.X_GEQ_B, variable_x='Cap_S', b_max=scenario.store_min, location_set=instance.locations, component_set=instance.resources_store,
                                                              loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, label='restricts nameplate inventory to some LB')

        if Constraints.PRODUCTION in constraints:

            constraint_production_mode(instance=instance, mode_dict=scenario.mode_dict,
                                       scheduling_scale_level=scenario.scheduling_scale_level)

            # *----------------nameplate production capacity---------------------------------------------

            instance.constraint_nameplate_production_certain_capacity = make_constraint(instance=instance, type_cons=Cons.X_LEQ_Y, variable_x='P',
                                                                                        location_set=instance.locations, component_set=instance.processes_certain_capacity,  loc_comp_dict=scenario.location_process_dict,
                                                                                        x_scale_level=scenario.scheduling_scale_level, y_scale_level=scenario.network_scale_level, variable_y='Cap_P', label='restricts production to certain nameplate capacity')

            instance.constraint_nameplate_production_varying_capacity = make_constraint(instance=instance, type_cons=Cons.X_LEQ_BY, variable_x='P',
                                                                                        location_set=instance.locations, component_set=instance.processes_varying_capacity,  loc_comp_dict=scenario.location_process_dict,
                                                                                        b_factor=scenario.capacity_factor, x_scale_level=scenario.scheduling_scale_level, b_scale_level=scenario.capacity_scale_level,
                                                                                        y_scale_level=scenario.network_scale_level, variable_y='Cap_P', label='restricts production to varying nameplate capacity')

            # *----------------production capacity bounds---------------------------------------------

            # instance.constraint_production_max = make_constraint(instance=instance, type_cons=Cons.X_LEQ_BY, variable_x='Cap_P', variable_y='X_P', b_max=scenario.prod_max, location_set=instance.locations, component_set=instance.processes,
            #                                                      loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level, label='restricts nameplate capacity to some UB')

            # instance.constraint_production_min = make_constraint(instance=instance, type_cons=Cons.X_GEQ_BY, variable_x='Cap_P', variable_y='X_P', b_max=scenario.prod_min, location_set=instance.locations, component_set=instance.processes,
            #                                                      loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level, label='restricts nameplate capacity to some LB')

            instance.constraint_production_max = make_constraint(instance=instance, type_cons=Cons.X_LEQ_B, variable_x='Cap_P', b_max=scenario.prod_max, location_set=instance.locations, component_set=instance.processes,
                                                                 loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, label='restricts nameplate capacity to some UB')

            instance.constraint_production_min = make_constraint(instance=instance, type_cons=Cons.X_GEQ_B, variable_x='Cap_P', b_max=scenario.prod_min, location_set=instance.locations, component_set=instance.processes,
                                                                 loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, label='restricts nameplate capacity to some LB')

        if Constraints.LAND in constraints:
            generate_land_vars(
                instance=instance, scale_level=scenario.network_scale_level)

            constraint_land_process(instance=instance, land_dict=scenario.land_dict,
                                    network_scale_level=scenario.network_scale_level)
            constraint_land_location(
                instance=instance, network_scale_level=scenario.network_scale_level)
            constraint_land_network(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_land_process_cost(instance=instance, land_dict=scenario.land_dict,
                                         land_cost_dict=scenario.land_cost_dict,
                                         network_scale_level=scenario.network_scale_level)
            constraint_land_location_cost(
                instance=instance, network_scale_level=scenario.network_scale_level)
            constraint_land_network_cost(
                instance=instance, network_scale_level=scenario.network_scale_level)

            if land_restriction is not None:
                constraint_land_location_restriction(
                    instance=instance, network_scale_level=scenario.network_scale_level,
                    land_restriction=land_restriction)

        if Constraints.CREDIT in constraints:
            generate_credit_vars(
                instance=instance, scale_level=scenario.network_scale_level)

            constraint_credit_process(instance=instance, credit_dict=scenario.credit_dict,
                                      network_scale_level=scenario.network_scale_level)
            constraint_credit_location(
                instance=instance, network_scale_level=scenario.network_scale_level)
            constraint_credit_network(
                instance=instance, network_scale_level=scenario.network_scale_level)

        if Constraints.RESOURCE_BALANCE in constraints:
            constraint_inventory_balance(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                         multiconversion=scenario.multiconversion, mode_dict=scenario.mode_dict, inventory_zero=inventory_zero,
                                         location_resource_dict=scenario.location_resource_dict)

            # constraint_network_production(
            #     instance=instance, network_scale_level=scenario.network_scale_level)
            # constraint_network_discharge(
            #     instance=instance, network_scale_level=scenario.network_scale_level)
            # constraint_network_consumption(
            #     instance=instance, network_scale_level=scenario.network_scale_level)
            # constraint_network_purchase(
            #     instance=instance, network_scale_level=scenario.network_scale_level)

            # *----------------resource consumption---------------------------------------------

            instance.constraint_resource_consumption_certain = make_constraint(
                instance=instance, type_cons=Cons.X_LEQ_B, variable_x='C', location_set=instance.locations, component_set=instance.resources_certain_availability, b_max=scenario.cons_max,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.scheduling_scale_level, label='restricts resource consumption to certain availablity')

            instance.constraint_resource_consumption_varying = make_constraint(
                instance=instance, type_cons=Cons.X_LEQ_B, variable_x='C', location_set=instance.locations, component_set=instance.resources_varying_availability, b_max=scenario.cons_max,
                loc_comp_dict=scenario.location_resource_dict, b_factor=scenario.availability_factor, x_scale_level=scenario.scheduling_scale_level, b_scale_level=scenario.availability_scale_level, label='restricts resource consumption to varying availablity')

            # # *----------------resource purchase---------------------------------------------

            instance.constraint_resource_purchase_certain = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_BY, variable_x='B', variable_y='C', location_set=instance.locations, component_set=instance.resources_certain_price, b_max=scenario.price_dict,
                loc_comp_dict=scenario.location_resource_dict,  x_scale_level=scenario.scheduling_scale_level, y_scale_level=scenario.scheduling_scale_level, label='calculates certain amount spent on resource consumption')

            instance.constraint_resource_purchase_varying = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_BY, variable_x='B', variable_y='C', location_set=instance.locations, component_set=instance.resources_varying_price, b_max=scenario.price_dict,
                loc_comp_dict=scenario.location_resource_dict, b_factor=scenario.price_factor, x_scale_level=scenario.scheduling_scale_level, y_scale_level=scenario.scheduling_scale_level, b_scale_level=scenario.purchase_scale_level, label='calculates varying amount spent on resource consumption')

            # # *----------------sum P,S,C,B over location---------------------------------------------

            instance.constraint_location_production = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMSCALE_Y, variable_x='P_location', variable_y='P', location_set=instance.locations, component_set=instance.processes,
                loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.scheduling_scale_level, cluster_wt=scenario.cluster_wt,
                label='sums up production from process over the temporal scale at location')

            instance.constraint_location_discharge = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMSCALE_Y, variable_x='S_location', variable_y='S', location_set=instance.locations, component_set=instance.resources_sell,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.scheduling_scale_level, cluster_wt=scenario.cluster_wt,
                label='sums up discharge of resource over the temporal scale at location')

            instance.constraint_location_consumption = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMSCALE_Y, variable_x='C_location', variable_y='C', location_set=instance.locations, component_set=instance.resources_purch,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.scheduling_scale_level, cluster_wt=scenario.cluster_wt,
                label='sums up consumption of resource over the temporal scale at location')

            instance.constraint_location_purchase = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMSCALE_Y, variable_x='B_location', variable_y='B', location_set=instance.locations, component_set=instance.resources_purch,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.scheduling_scale_level, cluster_wt=scenario.cluster_wt,
                label='sums up purchase expenditure of resource over the temporal scale at location')

            # # *----------------sum P,S,C,B over network ---------------------------------------------

            instance.constraint_network_production = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMLOC_Y, variable_x='P_network', variable_y='P_location', location_set=instance.locations, component_set=instance.processes,
                loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up production from process over all locations in network')

            instance.constraint_network_discharge = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMLOC_Y, variable_x='S_network', variable_y='S_location', location_set=instance.locations, component_set=instance.resources_sell,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up discharge of resource over all locations in network')

            instance.constraint_network_consumption = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMLOC_Y, variable_x='C_network', variable_y='C_location', location_set=instance.locations, component_set=instance.resources_purch,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up consumption of resource over all locations in network')

            instance.constraint_network_purchase = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMLOC_Y, variable_x='B_network', variable_y='B_location', location_set=instance.locations, component_set=instance.resources_purch,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up purchase expenditure of resource over all locations in network')

            instance.constraint_inventory_network = constraint_inventory_network(
                instance=instance, network_scale_level=scenario.network_scale_level, scheduling_scale_level=scenario.scheduling_scale_level)
        if Constraints.TRANSPORT in constraints:

            if len(scenario.location_set) > 1:
                constraint_resource_export(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                           transport_avail_dict=scenario.transport_avail_dict, resource_transport_dict=scenario.resource_transport_dict,
                                           source_sink_resource_dict=scenario.source_sink_resource_dict)
                constraint_transport_export(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                            transport_avail_dict=scenario.transport_avail_dict, transport_resource_dict=scenario.transport_resource_dict)
                constraint_export(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                  network_scale_level=scenario.network_scale_level, location_transport_resource_dict=scenario.location_transport_resource_dict,
                                  transport_capacity_factor=scenario.transport_capacity_factor, transport_capacity_scale_level=scenario.transport_capacity_scale_level)
                constraint_transport_capacity_UB(instance=instance, network_scale_level=scenario.network_scale_level,
                                                 transport_avail_dict=scenario.transport_avail_dict, trans_max=scenario.trans_max)
                constraint_transport_capacity_LB(instance=instance, network_scale_level=scenario.network_scale_level,
                                                 transport_avail_dict=scenario.transport_avail_dict, trans_min=scenario.trans_min)

                constraint_transport_capex(instance=instance, trans_capex=scenario.trans_capex, distance_dict=scenario.distance_dict,
                                           transport_avail_dict=scenario.transport_avail_dict, network_scale_level=scenario.network_scale_level)

                constraint_transport_network_capex(
                    instance=instance, network_scale_level=scenario.network_scale_level)
                constraint_transport_export_network(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level, network_scale_level=scenario.network_scale_level,
                                                    transport_avail_dict=scenario.transport_avail_dict)
                constraint_transport_vopex(instance=instance, trans_vopex=scenario.trans_vopex, distance_dict=scenario.distance_dict,
                                           transport_avail_dict=scenario.transport_avail_dict, network_scale_level=scenario.network_scale_level)

                constraint_transport_network_vopex(
                    instance=instance, network_scale_level=scenario.network_scale_level)

                constraint_transport_fopex(instance=instance, trans_fopex=scenario.trans_fopex, distance_dict=scenario.distance_dict,
                                           transport_avail_dict=scenario.transport_avail_dict, network_scale_level=scenario.network_scale_level)
                constraint_transport_network_fopex(
                    instance=instance, network_scale_level=scenario.network_scale_level)
                # constraint_transport_import(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                #                             transport_avail_dict=scenario.transport_avail_dict)
                # constraint_transport_exp_UB(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                #                             network_scale_level=scenario.network_scale_level,
                #                             trans_max=scenario.trans_max,
                #                             transport_avail_dict=scenario.transport_avail_dict)
                # constraint_transport_imp_UB(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                #                             network_scale_level=scenario.network_scale_level,
                #                             trans_max=scenario.trans_max,
                #                             transport_avail_dict=scenario.transport_avail_dict)
                # constraint_transport_balance(
                #     instance=instance, scheduling_scale_level=scenario.scheduling_scale_level)

                # constraint_transport_imp_cost(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                #                               trans_cost=scenario.trans_cost, distance_dict=scenario.distance_dict)
                # constraint_transport_cost(
                #     instance=instance, scheduling_scale_level=scenario.scheduling_scale_level)
                # constraint_transport_cost_network(
                #     instance=instance, network_scale_level=scenario.network_scale_level)

        if Constraints.NETWORK in constraints:
            generate_network_binary_vars(
                instance=instance, scale_level=scenario.network_scale_level)

            constraint_storage_facility(instance=instance, store_max=scenario.store_max,
                                        location_resource_dict=scenario.location_resource_dict,
                                        network_scale_level=scenario.network_scale_level)

            constraint_production_facility(instance=instance, prod_max=scenario.prod_max,
                                           location_process_dict=scenario.location_process_dict,
                                           network_scale_level=scenario.network_scale_level)

            constraint_min_production_facility(instance=instance, prod_min=scenario.prod_min,
                                               location_process_dict=scenario.location_process_dict,
                                               network_scale_level=scenario.network_scale_level)

            constraint_min_storage_facility(instance=instance, store_min=scenario.store_min,
                                            location_resource_dict=scenario.location_resource_dict,
                                            network_scale_level=scenario.network_scale_level)

            instance.del_component(instance.constraint_storage_min)
            instance.del_component(instance.constraint_production_min)

        if Constraints.PRESERVE_NETWORK in constraints:

            constraint_preserve_capacity_facility(
                instance=instance, location_process_dict=scenario.location_process_dict, network_scale_level=scenario.network_scale_level)

        if Constraints.MODE in constraints:
            generate_mode_vars(
                instance=instance, scale_level=scenario.scheduling_scale_level, mode_dict=scenario.mode_dict)

            constraint_production_mode_facility(instance=instance, prod_max=scenario.prod_max,
                                                location_process_dict=scenario.location_process_dict,
                                                scheduling_scale_level=scenario.scheduling_scale_level)
            constraint_min_production_mode_facility(instance=instance, prod_min=scenario.prod_min,
                                                    location_process_dict=scenario.location_process_dict,
                                                    scheduling_scale_level=scenario.scheduling_scale_level)
            constraint_production_mode_binary(instance=instance, mode_dict=scenario.mode_dict,
                                              scheduling_scale_level=scenario.scheduling_scale_level,
                                              network_scale_level=scenario.network_scale_level)
            constraint_production_rate1(instance=instance, rate_max_dict=scenario.rate_max_dict,
                                        scheduling_scale_level=scenario.scheduling_scale_level)
            constraint_production_rate2(instance=instance, rate_max_dict=scenario.rate_max_dict,
                                        scheduling_scale_level=scenario.scheduling_scale_level)
            constraint_production_mode_switch(
                instance=instance, mode_dict=scenario.mode_dict, scheduling_scale_level=scenario.scheduling_scale_level)

        if Constraints.MATERIAL in constraints:

            constraint_material_process(
                instance=instance, process_material_dict=scenario.process_material_dict, network_scale_level=scenario.network_scale_level)
            constraint_material_location(
                instance=instance, network_scale_level=scenario.network_scale_level)
            constraint_material_network(
                instance=instance, network_scale_level=scenario.network_scale_level)
            constraint_production_facility_material_mode(
                instance=instance, network_scale_level=scenario.network_scale_level, location_process_dict=scenario.location_process_dict)
            constraint_production_facility_material_mode_binary(
                instance=instance, network_scale_level=scenario.network_scale_level, location_process_dict=scenario.location_process_dict)

            constraint_production_facility_material(instance=instance, prod_max=scenario.prod_max, location_process_dict=scenario.location_process_dict,
                                                    network_scale_level=scenario.network_scale_level, process_material_modes_dict=scenario.process_material_modes_dict)
            constraint_min_production_facility_material(instance=instance, prod_min=scenario.prod_min, location_process_dict=scenario.location_process_dict,
                                                        network_scale_level=scenario.network_scale_level, process_material_modes_dict=scenario.process_material_modes_dict)
            constraint_material_mode_process(
                instance=instance, process_material_mode_material_dict=scenario.process_material_mode_material_dict, network_scale_level=scenario.network_scale_level)

            constraint_nameplate_production_material_mode(instance=instance, capacity_factor=scenario.capacity_factor, location_process_dict=scenario.location_process_dict,
                                                          network_scale_level=scenario.network_scale_level, scheduling_scale_level=scenario.scheduling_scale_level)

            constraint_location_production_material_mode(instance=instance, cluster_wt=scenario.cluster_wt,
                                                         network_scale_level=scenario.network_scale_level, scheduling_scale_level=scenario.scheduling_scale_level)

            constraint_location_production_material_mode_sum(
                instance=instance, network_scale_level=scenario.network_scale_level,  process_material_mode_material_dict=scenario.process_material_mode_material_dict)

        if gwp is not None:
            constraint_global_warming_potential_network_reduction(
                instance=instance, network_scale_level=scenario.network_scale_level,
                gwp_reduction_pct=gwp_reduction_pct, gwp=gwp)

        if objective == Objective.COST_W_DEMAND_PENALTY:
            generate_demand_vars(
                instance=instance, scale_level=scenario.demand_scale_level)
            constraint_demand_penalty(instance=instance, demand_scale_level=scenario.demand_scale_level,
                                      scheduling_scale_level=scenario.scheduling_scale_level, demand=demand,
                                      demand_factor=scenario.demand_factor, location_resource_dict=scenario.location_resource_dict, sign=demand_sign)

            objective_cost_w_demand_penalty(instance=instance, demand_penalty=scenario.demand_penalty,
                                            constraints=constraints, network_scale_level=scenario.network_scale_level, demand_scale_level=scenario.demand_scale_level)

        elif objective == Objective.PROFIT_W_DEMAND_PENALTY:
            generate_demand_vars(
                instance=instance, scale_level=scenario.demand_scale_level)
            constraint_demand_penalty(instance=instance, demand_scale_level=scenario.demand_scale_level,
                                      scheduling_scale_level=scenario.scheduling_scale_level, demand=demand,
                                      demand_factor=scenario.demand_factor, location_resource_dict=scenario.location_resource_dict, sign=demand_sign)
            constraint_network_cost(
                instance=instance, network_scale_level=scenario.network_scale_level, constraints=constraints)
            constraint_resource_revenue(instance=instance, location_resource_dict=scenario.location_resource_dict, revenue=scenario.revenue_dict,
                                        scheduling_scale_level=scenario.scheduling_scale_level, revenue_factor=scenario.revenue_factor)
            constraint_location_revenue(
                instance=instance, network_scale_level=scenario.network_scale_level, cluster_wt=scenario.cluster_wt, scheduling_scale_level=scenario.scheduling_scale_level)
            constraint_network_revenue(
                instance=instance, network_scale_level=scenario.network_scale_level)
            objective_profit_w_demand_penalty(instance=instance, demand_penalty=scenario.demand_penalty,
                                              constraints=constraints, network_scale_level=scenario.network_scale_level, demand_scale_level=scenario.demand_scale_level)

        else:
            if Constraints.DEMAND in constraints:
                constraint_demand(instance=instance, demand_scale_level=scenario.demand_scale_level,
                                  scheduling_scale_level=scenario.scheduling_scale_level, demand=demand,
                                  demand_factor=scenario.demand_factor, location_resource_dict=scenario.location_resource_dict, sign=demand_sign)

        if objective == Objective.COST:

            objective_cost(
                instance=instance, network_scale_level=scenario.network_scale_level, constraints=constraints)

        if objective == Objective.PROFIT:

            constraint_network_cost(
                instance=instance, network_scale_level=scenario.network_scale_level, constraints=constraints)
            constraint_resource_revenue(instance=instance, location_resource_dict=scenario.location_resource_dict, revenue=scenario.revenue_dict,
                                        scheduling_scale_level=scenario.scheduling_scale_level, revenue_factor=scenario.revenue_factor)
            constraint_location_revenue(
                instance=instance, network_scale_level=scenario.network_scale_level, cluster_wt=scenario.cluster_wt, scheduling_scale_level=scenario.scheduling_scale_level)
            constraint_network_revenue(
                instance=instance, network_scale_level=scenario.network_scale_level)
            objective_profit(
                instance=instance, network_scale_level=scenario.network_scale_level, constraints=constraints)

        if objective == Objective.MIN_DISCHARGE:

            constraint_network_cost(
                instance=instance, network_scale_level=scenario.network_scale_level, constraints=constraints)

            objective_discharge_min(instance=instance, resource=objective_resource,
                                    network_scale_level=scenario.network_scale_level)

        if objective == Objective.MAX_DISCHARGE:

            constraint_network_cost(
                instance=instance, network_scale_level=scenario.network_scale_level, constraints=constraints)

            objective_discharge_max(instance=instance, resource=objective_resource,
                                    network_scale_level=scenario.network_scale_level)

        if objective == Objective.MIN_GWP:

            constraint_network_cost(
                instance=instance, network_scale_level=scenario.network_scale_level, constraints=constraints)

            objective_gwp_min(
                instance=instance, network_scale_level=scenario.network_scale_level)

        if scenario.capacity_bounds is not None:
            constraint_min_capacity_facility(instance=instance, location_process_dict=scenario.location_process_dict,
                                             network_scale_level=scenario.network_scale_level, capacity_bounds=scenario.capacity_bounds)

        if write_lpfile is True:
            instance.write(f'{scenario.name}.lp')

        instance.dual = Suffix(direction=Suffix.IMPORT_EXPORT)

        return instance

    if model_class is ModelClass.MPLP:
        A, b, c, H, CRa, CRb, F, no_eq_cons = scenario.matrix_form()

        matrix_dict = {'A': A, 'b': b, 'c': c,
                       'H': H, 'CRa': CRa, 'CRb': CRb, 'F': F, 'no_eq_cons': no_eq_cons}

        return matrix_dict
