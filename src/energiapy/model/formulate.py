import time
from enum import Enum, auto
from typing import Dict, Set, Tuple
from warnings import warn

from pyomo.environ import ConcreteModel, Constraint
from pyomo.environ import Objective as Objective_pyomo
from pyomo.environ import Suffix

from ..components.location import Location
from ..components.process import Process
from ..components.resource import Resource
from ..components.scenario import Scenario, ScenarioType
from .constraints.constraints import (Cons, Constraints, constraint_sum_total,
                                      make_constraint)
from .constraints.cost import (constraint_location_land_cost,
                               constraint_location_storage_cost,
                               constraint_network_land_cost,
                               constraint_network_storage_cost,
                               constraint_process_capex,
                               constraint_process_fopex,
                               constraint_process_incidental,
                               constraint_process_land_cost,
                               constraint_process_vopex,
                               constraint_storage_cost, constraint_total_cost,
                               constraint_total_purchase,
                               constraint_total_revenue,
                               constraint_transport_imp_cost)
from .constraints.credit import (constraint_location_credit,
                                 constraint_network_credit,
                                 constraint_process_credit)
from .constraints.demand import constraint_demand, constraint_demand_penalty
from .constraints.emission import (
    constraint_acidification_potential_location,
    constraint_acidification_potential_material,
    constraint_acidification_potential_material_mode,
    constraint_acidification_potential_network,
    constraint_acidification_potential_process,
    constraint_acidification_potential_resource,
    constraint_acidification_potential_resource_consumption,
    constraint_acidification_potential_resource_discharge,
    constraint_freshwater_eutrophication_potential_location,
    constraint_freshwater_eutrophication_potential_material,
    constraint_freshwater_eutrophication_potential_material_mode,
    constraint_freshwater_eutrophication_potential_network,
    constraint_freshwater_eutrophication_potential_process,
    constraint_freshwater_eutrophication_potential_resource,
    constraint_freshwater_eutrophication_potential_resource_consumption,
    constraint_freshwater_eutrophication_potential_resource_discharge,
    constraint_global_warming_potential_location,
    constraint_global_warming_potential_material,
    constraint_global_warming_potential_material_mode,
    constraint_global_warming_potential_network,
    constraint_global_warming_potential_network_reduction,
    constraint_global_warming_potential_process,
    constraint_global_warming_potential_resource,
    constraint_global_warming_potential_resource_consumption,
    constraint_global_warming_potential_resource_discharge,
    constraint_marine_eutrophication_potential_location,
    constraint_marine_eutrophication_potential_material,
    constraint_marine_eutrophication_potential_material_mode,
    constraint_marine_eutrophication_potential_network,
    constraint_marine_eutrophication_potential_process,
    constraint_marine_eutrophication_potential_resource,
    constraint_marine_eutrophication_potential_resource_consumption,
    constraint_marine_eutrophication_potential_resource_discharge,
    constraint_ozone_depletion_potential_location,
    constraint_ozone_depletion_potential_material,
    constraint_ozone_depletion_potential_material_mode,
    constraint_ozone_depletion_potential_network,
    constraint_ozone_depletion_potential_process,
    constraint_ozone_depletion_potential_resource,
    constraint_ozone_depletion_potential_resource_consumption,
    constraint_ozone_depletion_potential_resource_discharge,
    constraint_terrestrial_eutrophication_potential_location,
    constraint_terrestrial_eutrophication_potential_material,
    constraint_terrestrial_eutrophication_potential_material_mode,
    constraint_terrestrial_eutrophication_potential_network,
    constraint_terrestrial_eutrophication_potential_process,
    constraint_terrestrial_eutrophication_potential_resource,
    constraint_terrestrial_eutrophication_potential_resource_consumption,
    constraint_terrestrial_eutrophication_potential_resource_discharge)
from .constraints.failure import constraint_nameplate_production_failure
from .constraints.land import (constraint_location_land,
                               constraint_location_land_restriction,
                               constraint_network_land, constraint_procss_land)
from .constraints.material import (
    constraint_material_location, constraint_material_mode_process,
    constraint_material_network, constraint_material_process,
    constraint_min_production_facility_material,
    constraint_production_facility_material,
    constraint_production_facility_material_mode,
    constraint_production_facility_material_mode_binary)
from .constraints.mode import (constraint_min_production_mode_facility,
                               constraint_production_mode,
                               constraint_production_mode_binary,
                               constraint_production_mode_facility,
                               constraint_production_mode_switch,
                               constraint_production_rate1,
                               constraint_production_rate2)
from .constraints.network import (constraint_min_capacity_facility,
                                  constraint_min_production_facility,
                                  constraint_min_storage_facility,
                                  constraint_preserve_capacity_facility,
                                  constraint_production_facility,
                                  constraint_storage_facility)
from .constraints.production import \
    constraint_nameplate_production_material_mode
from .constraints.resource_balance import (
    constraint_inventory_balance, constraint_inventory_network,
    constraint_location_production_material_mode,
    constraint_location_production_material_mode_sum)
from .constraints.transport import (  # constraint_transport_balance,; constraint_transport_exp_UB,; constraint_transport_export,; constraint_transport_imp_UB,; constraint_transport_import,
    constraint_export, constraint_resource_export,
    constraint_transport_capacity_LB, constraint_transport_capacity_LB_no_bin,
    constraint_transport_capacity_UB, constraint_transport_capacity_UB_no_bin,
    constraint_transport_capex, constraint_transport_export,
    constraint_transport_export_network, constraint_transport_fopex,
    constraint_transport_network_capex, constraint_transport_network_fopex,
    constraint_transport_network_vopex, constraint_transport_vopex)
from .constraints.uncertain import (constraint_uncertain_process_capacity,
                                    constraint_uncertain_resource_demand)
from .objectives import (objective_cost, objective_cost_w_demand_penalty,
                         objective_discharge_max, objective_discharge_min,
                         objective_emission_min, objective_gwp_min,
                         objective_profit, objective_profit_w_demand_penalty)
from .sets.components import generate_component_sets
from .sets.location_subsets import generate_location_subsets
from .sets.modes import (generate_material_mode_sets,
                         generate_production_mode_sets)
from .sets.process_subsets import generate_process_subsets
from .sets.resource_subsets import generate_resource_subsets
from .sets.temporal import generate_temporal_sets
from .sets.transport_subsets import generate_transport_subsets
from .variables.binary import generate_network_binary_vars
from .variables.demand import generate_demand_vars
from .variables.economic import (generate_process_credit_vars,
                                 generate_process_expenditure_vars,
                                 generate_resource_expenditure_vars,
                                 generate_resource_revenue_vars,
                                 generate_total_cost_var,
                                 generate_transport_expenditure_vars)
from .variables.emission import generate_emission_vars
from .variables.land import generate_land_vars
from .variables.material import generate_material_vars
from .variables.mode import generate_mode_vars
from .variables.network import generate_network_vars
from .variables.schedule import generate_scheduling_vars
from .variables.transport import (generate_transport_network_binaries,
                                  generate_transport_resource_vars)
from .variables.uncertain import generate_uncertainty_vars


class ModelClass(Enum):
    """Class of model
    """
    MIP = auto()
    """
    Mixed integer program
    """
    MPLP = auto()
    """
    multi-parametric linear program
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
    EMISSION = auto()
    """
    Minimize emission using weighted sum method
    """


def formulate(scenario: Scenario, constraints: Set[Constraints] = None, objective: Objective = None,
              write_lpfile: bool = False, gwp: float = None, land_restriction: float = None,
              gwp_reduction_pct: float = None, model_class: ModelClass = ModelClass.MIP, objective_resource: Resource = None,
              inventory_zero: Dict[Location,
                                   Dict[Tuple[Process, Resource], float]] = None,
              demand_sign: str = 'geq', meet_demand_scale: int = None) -> ConcreteModel:
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
            Objective.COST
            Objective.PROFIT
            Objective.MIN_DISCHARGE
            Objective.MAX_DISCHARGE
            Objective.COST_W_DEMAND_PENALTY
            Objective.PROFIT_W_DEMAND_PENALTY
            Objective.MIN_GWP
            Objective.EMISSION
    Returns:
        ConcreteModel: pyomo instance
    """
    start = time.time()
    demand = scenario.demand
    if meet_demand_scale is None:
        meet_demand_scale = scenario.scales.scheduling_scale

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

        # *----------------Declare Model ---------------------------------------------
        instance = ConcreteModel()

        # *----------------Define Sets ---------------------------------------------

        generate_temporal_sets(instance=instance, scenario=scenario)
        generate_component_sets(instance=instance, scenario=scenario)

        generate_resource_subsets(instance=instance, scenario=scenario)
        generate_process_subsets(instance=instance, scenario=scenario)
        generate_material_mode_sets(instance=instance, scenario=scenario)
        # generate_production_mode_sets

        if scenario.scenario_type == ScenarioType.MULTI_LOCATION:
            if Constraints.TRANSPORT in constraints:
                generate_location_subsets(instance=instance, scenario=scenario)
                generate_transport_subsets(
                    instance=instance, scenario=scenario)
            else:
                warn('Define TRANSPORT constraints')

        # *----------------Generate Vars ---------------------------------------------

        generate_scheduling_vars(
            instance=instance, mode_dict=scenario.mode_dict, scenario=scenario)

        generate_network_vars(
            instance=instance)

        generate_material_vars(instance=instance)

        if Constraints.UNCERTAIN in constraints:
            generate_uncertainty_vars(
                instance=instance, scale_level=scenario.scheduling_scale_level)

            constraint_uncertain_process_capacity(
                instance=instance, capacity=scenario.cap_max, network_scale_level=scenario.network_scale_level)
            constraint_uncertain_resource_demand(
                instance=instance, demand=demand, scheduling_scale_level=scenario.scheduling_scale_level)

        if scenario.scenario_type == ScenarioType.MULTI_LOCATION:
            if Constraints.TRANSPORT in constraints:
                generate_transport_resource_vars(instance=instance)
                generate_transport_expenditure_vars(instance=instance)

                if Constraints.NETWORK in constraints:
                    generate_transport_network_binaries(instance=instance)
            else:
                warn('You might want to include TRANSPORT constraints')

        # *----------------Write Constraints ---------------------------------------------

        if Constraints.COST in constraints:

            # *----------------Technology Expenditure---------------------------------------------

            generate_process_expenditure_vars(
                instance=instance, scenario=scenario)

            if scenario.consider_capex:
                constraint_process_capex(instance=instance, capex_dict=scenario.capex_dict,
                                         network_scale_level=scenario.network_scale_level, capex_factor=scenario.capex_factor, annualization_factor=scenario.annualization_factor)

                instance.constraint_location_capex = make_constraint(
                    instance=instance, type_cons=Cons.X_EQ_SUMLOCCOST_Y, variable_x='Capex_location', variable_y='Capex_process', locations=instance.locations, component_set=instance.processes,
                    loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                    label='sums up capex from process over a location')

                instance.constraint_network_capex = make_constraint(
                    instance=instance, type_cons=Cons.X_EQ_SUMCOST_Y, variable_x='Capex_network', variable_y='Capex_location', locations=instance.locations, component_set=instance.processes,
                    loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                    label='sums up capex from process over all locations in network')

                instance.constraint_total_capex = constraint_sum_total(
                    instance=instance, var_total='Capex_total', var='Capex_network', network_scale_level=scenario.network_scale_level, label='calculates total capital expenditure on processes')

            if scenario.consider_fopex:

                constraint_process_fopex(instance=instance, fopex_dict=scenario.fopex_dict,
                                         network_scale_level=scenario.network_scale_level, fopex_factor=scenario.fopex_factor)

                instance.constraint_location_fopex = make_constraint(
                    instance=instance, type_cons=Cons.X_EQ_SUMLOCCOST_Y, variable_x='Fopex_location', variable_y='Fopex_process', locations=instance.locations, component_set=instance.processes,
                    loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                    label='sums up fopex from process over a locations')

                instance.constraint_network_fopex = make_constraint(
                    instance=instance, type_cons=Cons.X_EQ_SUMCOST_Y, variable_x='Fopex_network', variable_y='Fopex_location', locations=instance.locations, component_set=instance.processes,
                    loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                    label='sums up fopex from process over all locations in network')

                instance.constraint_total_fopex = constraint_sum_total(
                    instance=instance, var_total='Fopex_total', var='Fopex_network', network_scale_level=scenario.network_scale_level, label='calculates total fixed operational expenditure on processes')

            if scenario.consider_vopex:
                constraint_process_vopex(instance=instance, vopex_dict=scenario.vopex_dict,
                                         network_scale_level=scenario.network_scale_level, vopex_factor=scenario.vopex_factor)

                instance.constraint_location_vopex = make_constraint(
                    instance=instance, type_cons=Cons.X_EQ_SUMLOCCOST_Y, variable_x='Vopex_location', variable_y='Vopex_process', locations=instance.locations, component_set=instance.processes,
                    loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                    label='sums up vopex from process over a locations')

                instance.constraint_network_vopex = make_constraint(
                    instance=instance, type_cons=Cons.X_EQ_SUMCOST_Y, variable_x='Vopex_network', variable_y='Vopex_location', locations=instance.locations, component_set=instance.processes,
                    loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                    label='sums up vopex from process over all locations in network')

                instance.constraint_total_vopex = constraint_sum_total(
                    instance=instance, var_total='Vopex_total', var='Vopex_network', network_scale_level=scenario.network_scale_level, label='calculates total variable operational expenditure on processes')

            if scenario.consider_incidental:
                constraint_process_incidental(instance=instance, incidental_dict=scenario.incidental_dict,
                                              network_scale_level=scenario.network_scale_level, incidental_factor=scenario.incidental_factor)

                instance.constraint_location_incidental = make_constraint(
                    instance=instance, type_cons=Cons.X_EQ_SUMLOCCOST_Y, variable_x='Incidental_location', variable_y='Incidental_process', locations=instance.locations, component_set=instance.processes,
                    loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                    label='sums up incidental expenditure from process over a location')

                instance.constraint_network_incidental = make_constraint(
                    instance=instance, type_cons=Cons.X_EQ_SUMCOST_Y, variable_x='Incidental_network', variable_y='Incidental_location', locations=instance.locations, component_set=instance.processes,
                    loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                    label='sums up incidental expenditure from process over all locations in network')

                instance.constraint_total_incidental = constraint_sum_total(
                    instance=instance, var_total='Incidental_total', var='Incidental_network', network_scale_level=scenario.network_scale_level, label='calculates total incidental expenditure on processes')

            # *----------------Resource Expenditure---------------------------------------------

            generate_resource_expenditure_vars(
                instance=instance, scenario=scenario)

            instance.constraint_resource_purchase_certain = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_BY, variable_x='B', variable_y='C', locations=instance.locations, component_set=instance.resources_certain_price, b_max=scenario.price,
                loc_comp_dict=scenario.location_resource_dict,  x_scale_level=scenario.scheduling_scale_level, y_scale_level=scenario.scheduling_scale_level, label='calculates certain amount spent on resource consumption')

            instance.constraint_resource_purchase_varying = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_BY, variable_x='B', variable_y='C', locations=instance.locations, component_set=instance.resources_varying_price, b_max=scenario.price,
                loc_comp_dict=scenario.location_resource_dict, b_factor=scenario.price_factor, x_scale_level=scenario.scheduling_scale_level, y_scale_level=scenario.scheduling_scale_level, b_scale_level=scenario.price_factor_scale_level, label='calculates varying amount spent on resource consumption')

            instance.constraint_location_resource_purchase = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMSCALE_Y, variable_x='B_location', variable_y='B', locations=instance.locations, component_set=instance.resources_purch,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.scheduling_scale_level, cluster_wt=scenario.cluster_wt,
                label='sums up purchase expenditure of resource over the temporal scale at location')

            instance.constraint_network_resource_purchase = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMLOC_Y, variable_x='B_network', variable_y='B_location', locations=instance.locations, component_set=instance.resources_purch,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up purchase expenditure of resource over all locations in network')

            # defined differently because this is summed over resource and time
            instance.constraint_total_purchase = constraint_total_purchase(
                instance=instance, network_scale_level=scenario.network_scale_level)

            if scenario.consider_storage_cost is True:

                # *----------------storage costs network ---------------------------------------------

                constraint_storage_cost(instance=instance, location_resource_dict=scenario.location_resource_dict,
                                        storage_cost=scenario.storage_cost, network_scale_level=scenario.network_scale_level)

                constraint_location_storage_cost(
                    instance=instance, network_scale_level=scenario.network_scale_level)

                constraint_network_storage_cost(
                    instance=instance, network_scale_level=scenario.network_scale_level)

                instance.constraint_total_storage_cost = constraint_sum_total(
                    instance=instance, var_total='Inv_cost_total', var='Inv_cost_network', network_scale_level=scenario.network_scale_level, label='calculates total storage cost')

            if Constraints.TRANSPORT in constraints:

                if scenario.scenario_type == ScenarioType.MULTI_LOCATION:

                    constraint_transport_capex(instance=instance, trans_capex=scenario.trans_capex, distance_dict=scenario.distance_dict,
                                               transport_avail_dict=scenario.transport_avail_dict, network_scale_level=scenario.network_scale_level, annualization_factor=scenario.annualization_factor)

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

                    instance.constraint_transport_total_capex = constraint_sum_total(
                        instance=instance, var_total='Capex_transport_total', var='Capex_transport_network', network_scale_level=scenario.network_scale_level, label='calculates total capital expenditure on transports')

                    instance.constraint_transport_total_vopex = constraint_sum_total(
                        instance=instance, var_total='Vopex_transport_total', var='Vopex_transport_network', network_scale_level=scenario.network_scale_level, label='calculates total variable operational expenditure on transports')

                    instance.constraint_transport_total_fopex = constraint_sum_total(
                        instance=instance, var_total='Fopex_transport_total', var='Fopex_transport_network', network_scale_level=scenario.network_scale_level, label='calculates total fixed operational expenditure on transports')

                else:
                    warn(
                        'TRANSPORT constraints are not required for a sigle location scenario')

            # *----------------Total cost ---------------------------------------------
            generate_total_cost_var(instance=instance)

            instance.constraint_total_cost = constraint_total_cost(
                instance=instance,  constraints=constraints, scenario=scenario)

        if Constraints.EMISSION in constraints:
            generate_emission_vars(instance=instance)

            constraint_global_warming_potential_process(
                instance=instance, process_gwp_dict=scenario.process_gwp_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_global_warming_potential_resource(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_global_warming_potential_resource_consumption(
                instance=instance, resource_gwp_dict=scenario.resource_gwp_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_global_warming_potential_resource_discharge(
                instance=instance, resource_gwp_dict=scenario.resource_gwp_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_global_warming_potential_location(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_global_warming_potential_network(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_ozone_depletion_potential_process(
                instance=instance, process_odp_dict=scenario.process_odp_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_ozone_depletion_potential_resource(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_ozone_depletion_potential_resource_consumption(
                instance=instance, resource_odp_dict=scenario.resource_odp_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_ozone_depletion_potential_resource_discharge(
                instance=instance, resource_odp_dict=scenario.resource_odp_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_ozone_depletion_potential_location(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_ozone_depletion_potential_network(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_acidification_potential_process(
                instance=instance, process_acid_dict=scenario.process_acid_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_acidification_potential_resource(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_acidification_potential_resource_consumption(
                instance=instance, resource_acid_dict=scenario.resource_acid_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_acidification_potential_resource_discharge(
                instance=instance, resource_acid_dict=scenario.resource_acid_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_acidification_potential_location(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_acidification_potential_network(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_terrestrial_eutrophication_potential_process(
                instance=instance, process_eutt_dict=scenario.process_eutt_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_terrestrial_eutrophication_potential_resource(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_terrestrial_eutrophication_potential_resource_consumption(
                instance=instance, resource_eutt_dict=scenario.resource_eutt_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_terrestrial_eutrophication_potential_resource_discharge(
                instance=instance, resource_eutt_dict=scenario.resource_eutt_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_terrestrial_eutrophication_potential_location(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_terrestrial_eutrophication_potential_network(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_freshwater_eutrophication_potential_process(
                instance=instance, process_eutf_dict=scenario.process_eutf_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_freshwater_eutrophication_potential_resource(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_freshwater_eutrophication_potential_resource_consumption(
                instance=instance, resource_eutf_dict=scenario.resource_eutf_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_freshwater_eutrophication_potential_resource_discharge(
                instance=instance, resource_eutf_dict=scenario.resource_eutf_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_freshwater_eutrophication_potential_location(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_freshwater_eutrophication_potential_network(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_marine_eutrophication_potential_process(
                instance=instance, process_eutm_dict=scenario.process_eutm_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_marine_eutrophication_potential_resource(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_marine_eutrophication_potential_resource_consumption(
                instance=instance, resource_eutm_dict=scenario.resource_eutm_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_marine_eutrophication_potential_resource_discharge(
                instance=instance, resource_eutm_dict=scenario.resource_eutm_dict,
                network_scale_level=scenario.network_scale_level)

            constraint_marine_eutrophication_potential_location(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_marine_eutrophication_potential_network(
                instance=instance, network_scale_level=scenario.network_scale_level)

            if Constraints.MATERIAL in constraints:

                constraint_global_warming_potential_material(
                    instance=instance, network_scale_level=scenario.network_scale_level)

                constraint_global_warming_potential_material_mode(instance=instance, material_gwp_dict=scenario.material_gwp_dict,
                                                                  process_material_mode_material_dict=scenario.process_material_mode_material_dict,
                                                                  network_scale_level=scenario.network_scale_level)

                constraint_ozone_depletion_potential_material(
                    instance=instance, network_scale_level=scenario.network_scale_level)

                constraint_ozone_depletion_potential_material_mode(instance=instance, material_odp_dict=scenario.material_odp_dict,
                                                                   process_material_mode_material_dict=scenario.process_material_mode_material_dict,
                                                                   network_scale_level=scenario.network_scale_level)

                constraint_acidification_potential_material(
                    instance=instance, network_scale_level=scenario.network_scale_level)

                constraint_acidification_potential_material_mode(instance=instance, material_acid_dict=scenario.material_acid_dict,
                                                                 process_material_mode_material_dict=scenario.process_material_mode_material_dict,
                                                                 network_scale_level=scenario.network_scale_level)

                constraint_terrestrial_eutrophication_potential_material(
                    instance=instance, network_scale_level=scenario.network_scale_level)

                constraint_terrestrial_eutrophication_potential_material_mode(instance=instance, material_eutt_dict=scenario.material_eutt_dict,
                                                                              process_material_mode_material_dict=scenario.process_material_mode_material_dict,
                                                                              network_scale_level=scenario.network_scale_level)

                constraint_freshwater_eutrophication_potential_material(
                    instance=instance, network_scale_level=scenario.network_scale_level)

                constraint_freshwater_eutrophication_potential_material_mode(instance=instance, material_eutf_dict=scenario.material_eutf_dict,
                                                                             process_material_mode_material_dict=scenario.process_material_mode_material_dict,
                                                                             network_scale_level=scenario.network_scale_level)

                constraint_marine_eutrophication_potential_material(
                    instance=instance, network_scale_level=scenario.network_scale_level)

                constraint_marine_eutrophication_potential_material_mode(instance=instance, material_eutm_dict=scenario.material_eutm_dict,
                                                                         process_material_mode_material_dict=scenario.process_material_mode_material_dict,
                                                                         network_scale_level=scenario.network_scale_level)
        if Constraints.FAILURE in constraints:
            constraint_nameplate_production_failure(instance=instance, fail_factor=scenario.fail_factor,
                                                    network_scale_level=scenario.network_scale_level,
                                                    scheduling_scale_level=scenario.scheduling_scale_level)

        if Constraints.INVENTORY in constraints:
            instance.constraint_nameplate_inventory = make_constraint(instance=instance, type_cons=Cons.X_LEQ_Y, variable_x='Inv',
                                                                      locations=instance.locations, component_set=instance.resources_store,  loc_comp_dict=scenario.location_resource_dict,
                                                                      x_scale_level=scenario.scheduling_scale_level, y_scale_level=scenario.network_scale_level, variable_y='Cap_S', label='restricts inventory to certain nameplate capacity')

            # *----------------inventory bounds ---------------------------------------------

            instance.constraint_storage_max = make_constraint(instance=instance, type_cons=Cons.X_LEQ_B, variable_x='Cap_S', b_max=scenario.store_max, locations=instance.locations, component_set=instance.resources_store,
                                                              loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, label='restricts nameplate inventory to some UB')

            instance.constraint_storage_min = make_constraint(instance=instance, type_cons=Cons.X_GEQ_B, variable_x='Cap_S', b_max=scenario.store_min, locations=instance.locations, component_set=instance.resources_store,
                                                              loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, label='restricts nameplate inventory to some LB')

        if Constraints.PRODUCTION in constraints:

            constraint_production_mode(instance=instance, location_process_dict=scenario.location_process_dict, mode_dict=scenario.mode_dict,
                                       scheduling_scale_level=scenario.scheduling_scale_level)

            # *----------------nameplate production capacity---------------------------------------------

            instance.constraint_nameplate_production_certain_capacity = make_constraint(instance=instance, type_cons=Cons.X_LEQ_Y, variable_x='P',
                                                                                        locations=instance.locations, component_set=instance.processes_certain_capacity,  loc_comp_dict=scenario.location_process_dict,
                                                                                        x_scale_level=scenario.scheduling_scale_level, y_scale_level=scenario.network_scale_level, variable_y='Cap_P', label='restricts production to certain nameplate capacity')

            instance.constraint_nameplate_production_varying_capacity = make_constraint(instance=instance, type_cons=Cons.X_LEQ_BY, variable_x='P',
                                                                                        locations=instance.locations, component_set=instance.processes_varying_capacity,  loc_comp_dict=scenario.location_process_dict,
                                                                                        b_factor=scenario.capacity_factor, x_scale_level=scenario.scheduling_scale_level, b_scale_level=scenario.capacity_factor_scale_level,
                                                                                        y_scale_level=scenario.network_scale_level, variable_y='Cap_P', label='restricts production to varying nameplate capacity')

            # *----------------production capacity bounds---------------------------------------------

            # instance.constraint_production_max = make_constraint(instance=instance, type_cons=Cons.X_LEQ_BY, variable_x='Cap_P', variable_y='X_P', b_max=scenario.cap_max, locations=instance.locations, component_set=instance.processes,
            #                                                      loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level, label='restricts nameplate capacity to some UB')

            # instance.constraint_production_min = make_constraint(instance=instance, type_cons=Cons.X_GEQ_BY, variable_x='Cap_P', variable_y='X_P', b_max=scenario.cap_min, locations=instance.locations, component_set=instance.processes,
            #                                                      loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level, label='restricts nameplate capacity to some LB')

            instance.constraint_production_max = make_constraint(instance=instance, type_cons=Cons.X_LEQ_B, variable_x='Cap_P', b_max=scenario.cap_max, locations=instance.locations, component_set=instance.processes,
                                                                 loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, label='restricts nameplate capacity to some UB')

            instance.constraint_production_min = make_constraint(instance=instance, type_cons=Cons.X_GEQ_B, variable_x='Cap_P', b_max=scenario.cap_min, locations=instance.locations, component_set=instance.processes,
                                                                 loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, label='restricts nameplate capacity to some LB')

        if Constraints.LAND in constraints:
            generate_land_vars(instance=instance)

            constraint_procss_land(instance=instance, land_dict=scenario.land_dict,
                                   network_scale_level=scenario.network_scale_level)
            constraint_location_land(
                instance=instance, network_scale_level=scenario.network_scale_level)
            constraint_network_land(
                instance=instance, network_scale_level=scenario.network_scale_level)

            constraint_process_land_cost(instance=instance, land_dict=scenario.land_dict,
                                         land_cost_dict=scenario.land_cost_dict,
                                         network_scale_level=scenario.network_scale_level)
            constraint_location_land_cost(
                instance=instance, network_scale_level=scenario.network_scale_level)
            constraint_network_land_cost(
                instance=instance, network_scale_level=scenario.network_scale_level)

            instance.constraint_total_land_cost = constraint_sum_total(
                instance=instance, var_total='Land_cost_total', var='Land_cost_network', network_scale_level=scenario.network_scale_level, label='calculates total on land')

            if land_restriction is not None:
                constraint_location_land_restriction(
                    instance=instance, network_scale_level=scenario.network_scale_level,
                    land_restriction=land_restriction)

        if Constraints.CREDIT in constraints:

            generate_process_credit_vars(instance=instance)

            constraint_process_credit(instance=instance, credit_dict=scenario.credit_dict,
                                      network_scale_level=scenario.network_scale_level)
            constraint_location_credit(
                instance=instance, network_scale_level=scenario.network_scale_level)
            constraint_network_credit(
                instance=instance, network_scale_level=scenario.network_scale_level)

            instance.constraint_total_credit = constraint_sum_total(
                instance=instance, var_total='Credit_total', var='Credit_network', network_scale_level=scenario.network_scale_level, label='calculates total credit')

        if Constraints.RESOURCE_BALANCE in constraints:
            constraint_inventory_balance(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                         multiconversion=scenario.multiconversion, mode_dict=scenario.mode_dict, inventory_zero=inventory_zero,
                                         location_resource_dict=scenario.location_resource_dict, location_process_dict=scenario.location_process_dict,
                                         location_resource_purch_dict=scenario.location_resource_purch_dict, location_resource_sell_dict=scenario.location_resource_sell_dict,
                                         location_resource_store_dict=scenario.location_resource_store_dict)

            # *----------------resource consumption---------------------------------------------

            instance.constraint_resource_consumption_certain = make_constraint(
                instance=instance, type_cons=Cons.X_LEQ_B, variable_x='C', locations=instance.locations, component_set=instance.resources_certain_availability, b_max=scenario.cons_max,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.scheduling_scale_level, label='restricts resource consumption to certain availablity')

            instance.constraint_resource_consumption_varying = make_constraint(
                instance=instance, type_cons=Cons.X_LEQ_B, variable_x='C', locations=instance.locations, component_set=instance.resources_varying_availability, b_max=scenario.cons_max,
                loc_comp_dict=scenario.location_resource_dict, b_factor=scenario.availability_factor, x_scale_level=scenario.scheduling_scale_level, b_scale_level=scenario.availability_factor_scale_level, label='restricts resource consumption to varying availablity')

            # # *----------------sum P,S,C,B over location---------------------------------------------

            instance.constraint_location_production = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMSCALE_Y, variable_x='P_location', variable_y='P', locations=instance.locations, component_set=instance.processes,
                loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.scheduling_scale_level, cluster_wt=scenario.cluster_wt,
                label='sums up production from process over the temporal scale at location')

            instance.constraint_location_resource_discharge = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMSCALE_Y, variable_x='S_location', variable_y='S', locations=instance.locations, component_set=instance.resources_sell,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.scheduling_scale_level, cluster_wt=scenario.cluster_wt,
                label='sums up discharge of resource over the temporal scale at location')

            instance.constraint_location_resource_consumption = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMSCALE_Y, variable_x='C_location', variable_y='C', locations=instance.locations, component_set=instance.resources_purch,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.scheduling_scale_level, cluster_wt=scenario.cluster_wt,
                label='sums up consumption of resource over the temporal scale at location')

            # # *----------------sum P,S,C,B over network ---------------------------------------------

            instance.constraint_network_production = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMLOC_Y, variable_x='P_network', variable_y='P_location', locations=instance.locations, component_set=instance.processes,
                loc_comp_dict=scenario.location_process_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up production from process over all locations in network')

            instance.constraint_network_resource_discharge = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMLOC_Y, variable_x='S_network', variable_y='S_location', locations=instance.locations, component_set=instance.resources_sell,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up discharge of resource over all locations in network')

            instance.constraint_network_resource_consumption = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMLOC_Y, variable_x='C_network', variable_y='C_location', locations=instance.locations, component_set=instance.resources_purch,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up consumption of resource over all locations in network')

            #####
            instance.constraint_inventory_network = constraint_inventory_network(
                instance=instance, network_scale_level=scenario.network_scale_level, scheduling_scale_level=scenario.scheduling_scale_level)

            if Constraints.TRANSPORT in constraints:

                if scenario.scenario_type == ScenarioType.MULTI_LOCATION:
                    constraint_resource_export(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                               transport_avail_dict=scenario.transport_avail_dict, resource_transport_dict=scenario.resource_transport_dict,
                                               source_sink_resource_dict=scenario.source_sink_resource_dict)
                    constraint_transport_export(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                                transport_avail_dict=scenario.transport_avail_dict, transport_resource_dict=scenario.transport_resource_dict)
                    constraint_export(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                      network_scale_level=scenario.network_scale_level, location_transport_resource_dict=scenario.location_transport_resource_dict,
                                      transport_capacity_factor=scenario.transport_capacity_factor, transport_capacity_scale_level=scenario.transport_capacity_scale_level)

                    constraint_transport_capacity_UB_no_bin(instance=instance, network_scale_level=scenario.network_scale_level,
                                                            transport_avail_dict=scenario.transport_avail_dict, trans_max=scenario.trans_max)
                    constraint_transport_capacity_LB_no_bin(instance=instance, network_scale_level=scenario.network_scale_level,
                                                            transport_avail_dict=scenario.transport_avail_dict, trans_min=scenario.trans_min)

        if Constraints.NETWORK in constraints:
            generate_network_binary_vars(instance=instance)

            constraint_storage_facility(instance=instance, store_max=scenario.store_max,
                                        location_resource_dict=scenario.location_resource_dict,
                                        network_scale_level=scenario.network_scale_level)

            constraint_production_facility(instance=instance, cap_max=scenario.cap_max,
                                           location_process_dict=scenario.location_process_dict,
                                           network_scale_level=scenario.network_scale_level)

            constraint_min_production_facility(instance=instance, cap_min=scenario.cap_min,
                                               location_process_dict=scenario.location_process_dict,
                                               network_scale_level=scenario.network_scale_level)

            constraint_min_storage_facility(instance=instance, store_min=scenario.store_min,
                                            location_resource_dict=scenario.location_resource_dict,
                                            network_scale_level=scenario.network_scale_level)

            instance.del_component(instance.constraint_storage_min)
            instance.del_component(instance.constraint_production_min)

            if scenario.scenario_type == ScenarioType.MULTI_LOCATION:
                constraint_transport_capacity_UB(instance=instance, network_scale_level=scenario.network_scale_level,
                                                 transport_avail_dict=scenario.transport_avail_dict, trans_max=scenario.trans_max)
                constraint_transport_capacity_LB(instance=instance, network_scale_level=scenario.network_scale_level,
                                                 transport_avail_dict=scenario.transport_avail_dict, trans_min=scenario.trans_min)

                instance.del_component(
                    instance.constraint_transport_capacity_UB_no_bin)
                instance.del_component(
                    instance.constraint_transport_capacity_LB_no_bin)
        if Constraints.PRESERVE_NETWORK in constraints:

            constraint_preserve_capacity_facility(
                instance=instance, location_process_dict=scenario.location_process_dict, network_scale_level=scenario.network_scale_level)

        if Constraints.MODE in constraints:
            generate_mode_vars(
                instance=instance, mode_dict=scenario.mode_dict)

            constraint_production_mode_facility(instance=instance, cap_max=scenario.cap_max,
                                                location_process_dict=scenario.location_process_dict,
                                                scheduling_scale_level=scenario.scheduling_scale_level)
            constraint_min_production_mode_facility(instance=instance, cap_min=scenario.cap_min,
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

            constraint_production_facility_material(instance=instance, cap_max=scenario.cap_max, location_process_dict=scenario.location_process_dict,
                                                    network_scale_level=scenario.network_scale_level, process_material_modes_dict=scenario.process_material_modes_dict)
            constraint_min_production_facility_material(instance=instance, cap_min=scenario.cap_min, location_process_dict=scenario.location_process_dict,
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

        if (objective == Objective.PROFIT) or (objective == Objective.PROFIT_W_DEMAND_PENALTY):

            generate_resource_revenue_vars(
                instance=instance, scenario=scenario)

            instance.constraint_resource_revenue_certain = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_BY, variable_x='R', variable_y='S', locations=instance.locations, component_set=instance.resources_certain_revenue, b_max=scenario.resource_revenue,
                loc_comp_dict=scenario.location_resource_dict,  x_scale_level=scenario.scheduling_scale_level, y_scale_level=scenario.scheduling_scale_level, label='revenue earned from selling resource')

            instance.constraint_resource_revenue_varying = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_BY, variable_x='R', variable_y='S', locations=instance.locations, component_set=instance.resources_varying_revenue, b_max=scenario.resource_revenue,
                loc_comp_dict=scenario.location_resource_dict, b_factor=scenario.revenue_factor, x_scale_level=scenario.scheduling_scale_level, y_scale_level=scenario.scheduling_scale_level, b_scale_level=scenario.revenue_factor_scale_level, label='revenue earned from selling resource at varying price')

            instance.constraint_location_revenue = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMSCALE_Y, variable_x='R_location', variable_y='R', locations=instance.locations, component_set=instance.resources_sell,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.scheduling_scale_level, cluster_wt=scenario.cluster_wt,
                label='sums up revenue expenditure of resource over the temporal scale at location')

            instance.constraint_network_revenue = make_constraint(
                instance=instance, type_cons=Cons.X_EQ_SUMLOC_Y, variable_x='R_network', variable_y='R_location', locations=instance.locations, component_set=instance.resources_sell,
                loc_comp_dict=scenario.location_resource_dict, x_scale_level=scenario.network_scale_level, y_scale_level=scenario.network_scale_level,
                label='sums up revenue expenditure of resource over all locations in network')

            instance.constraint_total_revenue = constraint_total_revenue(
                instance=instance, network_scale_level=scenario.network_scale_level)

        if (objective == Objective.COST_W_DEMAND_PENALTY) or (objective == Objective.PROFIT_W_DEMAND_PENALTY):

            generate_demand_vars(
                instance=instance, scale_level=scenario.demand_scale_level)
            constraint_demand_penalty(instance=instance, demand_scale_level=scenario.demand_scale_level,
                                      scheduling_scale_level=scenario.scheduling_scale_level, demand=demand,
                                      demand_factor=scenario.demand_factor, location_resource_dict=scenario.location_resource_sell_dict, sign=demand_sign)

        # *---------------------------------- Objective--------------------------------------------------------------------

        if objective == Objective.COST:
            instance.min_cost = objective_cost(
                instance=instance)

        if objective == Objective.PROFIT:
            instance.max_profit = objective_profit(
                instance=instance, network_scale_level=scenario.network_scale_level)

        if objective == Objective.COST_W_DEMAND_PENALTY:
            instance.min_cost_w_demand_penalty = objective_cost_w_demand_penalty(
                instance=instance, demand_penalty=scenario.demand_penalty, demand_scale_level=scenario.demand_scale_level)

        elif objective == Objective.PROFIT_W_DEMAND_PENALTY:
            instance.min_profit_w_demand_penalty = objective_profit_w_demand_penalty(instance=instance, demand_penalty=scenario.demand_penalty,
                                                                                     network_scale_level=scenario.network_scale_level, demand_scale_level=scenario.demand_scale_level)

        else:
            if Constraints.DEMAND in constraints:
                instance.constraint_resource_demand = constraint_demand(instance=instance, demand_scale_level=scenario.demand_scale_level,
                                                                        scheduling_scale_level=scenario.scheduling_scale_level, demand=demand,
                                                                        demand_factor=scenario.demand_factor, location_resource_dict=scenario.location_resource_sell_dict, sign=demand_sign)

        if objective == Objective.MIN_DISCHARGE:

            instance.min_discharge = objective_discharge_min(instance=instance, resource=objective_resource,
                                                             network_scale_level=scenario.network_scale_level)

        if objective == Objective.MAX_DISCHARGE:

            instance.max_discharge = objective_discharge_max(instance=instance, resource=objective_resource,
                                                             network_scale_level=scenario.network_scale_level)

        if objective == Objective.MIN_GWP:

            instance.min_gwp = objective_gwp_min(
                instance=instance, network_scale_level=scenario.network_scale_level)

        if objective == Objective.EMISSION:

            instance.min_emission = objective_emission_min(instance=instance, network_scale_level=scenario.network_scale_level, gwp_w=scenario.emission_weights.gwp, odp_w=scenario.emission_weights.odp, acid_w=scenario.emission_weights.acid,
                                                           eutt_w=scenario.emission_weights.eutt, eutf_w=scenario.emission_weights.eutf, eutm_w=scenario.emission_weights.eutm)

        if scenario.capacity_bounds is not None:
            constraint_min_capacity_facility(instance=instance, location_process_dict=scenario.location_process_dict,
                                             network_scale_level=scenario.network_scale_level, capacity_bounds=scenario.capacity_bounds)

        if write_lpfile is True:
            instance.write(f'{scenario.name}.lp')

        instance.dual = Suffix(direction=Suffix.IMPORT_EXPORT)

        obj = str(list([i for i in instance.component_objects()
                        if i.ctype == Objective_pyomo])[0])

        obj = obj.replace('_', ' ')

        cons_list = list(
            map(str, [i for i in instance.component_objects() if i.ctype == Constraint]))
        cons_list = [i.replace('_', ' ') for i in cons_list]

        print(f'{obj}')
        print()
        print('s.t.')
        print()
        for i in cons_list:
            print(i)

        end = time.time()
        delta = end - start
        print()
        print(f'model formulated in {delta} seconds')
        return instance

    if model_class is ModelClass.MPLP:
        A, b, c, H, CRa, CRb, F, no_eq_cons = scenario.matrix_form()

        matrix_dict = {'A': A, 'b': b, 'c': c,
                       'H': H, 'CRa': CRa, 'CRb': CRb, 'F': F, 'no_eq_cons': no_eq_cons}

        return matrix_dict
