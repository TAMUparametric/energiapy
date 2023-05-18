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
from .constraints.constraints import Constraints

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
    constraint_network_cost
)
from .constraints.emission import (
    constraint_global_warming_potential_location,
    constraint_global_warming_potential_material,
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
)
from .constraints.production import (
    constraint_nameplate_production,
    constraint_production_max,
    constraint_production_min
)
from .constraints.resource_balance import (
    constraint_demand,
    constraint_inventory_balance,
    constraint_location_consumption,
    constraint_location_revenue,
    constraint_location_discharge,
    constraint_location_production,
    constraint_location_purchase,
    constraint_network_consumption,
    constraint_network_revenue,
    constraint_network_discharge,
    constraint_network_production,
    constraint_network_purchase,
    constraint_resource_consumption,
    constraint_resource_purchase,
    constraint_resource_revenue
)
from .constraints.transport import (
    constraint_transport_balance,
    constraint_transport_exp_UB,
    constraint_transport_export,
    constraint_transport_imp_UB,
    constraint_transport_import,
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
    constraint_min_capacity_facility
)
from .constraints.credit import (
    constraint_credit_process,
    constraint_credit_location,
    constraint_credit_network
)
from .constraints.material import (
    constraint_material_process,
    constraint_material_location,
    constraint_material_network
)
from .objectives import (
    objective_cost,
    objective_discharge_max,
    objective_discharge_min,
    objective_profit,
    objective_gwp_min
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


def formulate(scenario: Scenario, constraints: Set[Constraints] = None, objective: Objective = None,
              write_lpfile: bool = False, gwp: float = None, land_restriction: float = None,
              gwp_reduction_pct: float = None, model_class: ModelClass = ModelClass.MIP, objective_resource: Resource = None, inventory_zero: Dict[Location, Dict[Tuple[Process, Resource], float]] = None) -> ConcreteModel:
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
        inventory_zero (Dict[Location, Dict[Tuple[Process, Resource], float]], optional): inventory at the start of the scheduling horizon. Defaults to None.


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

    Objectives include:
            Objectives.COST
            Objectives.PROFIT
            Objectives.MIN_DISCHARGE
            Objectives.MAX_DISCHARGE

    Returns:
        ConcreteModel: pyomo instance
    """

    demand = scenario.demand
    if isinstance(demand, dict):
        demand = {i.name: {j.name: demand[i][j]
                           for j in demand[i].keys()} for i in demand.keys()}

    if model_class is ModelClass.MIP:

        instance = ConcreteModel()
        generate_sets(instance=instance, scenario=scenario)

        generate_scheduling_vars(
            instance=instance, scale_level=scenario.scheduling_scale_level, mode_dict=scenario.mode_dict)
        generate_network_vars(
            instance=instance, scale_level=scenario.network_scale_level)
        generate_costing_vars(instance=instance)

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
                    instance=instance, material_gwp_dict=scenario.material_gwp_dict,
                    process_material_dict=scenario.process_material_dict, network_scale_level=scenario.network_scale_level)

        if Constraints.FAILURE in constraints:
            constraint_nameplate_production_failure(instance=instance, fail_factor=scenario.fail_factor,
                                                    network_scale_level=scenario.network_scale_level,
                                                    scheduling_scale_level=scenario.scheduling_scale_level)

        if Constraints.INVENTORY in constraints:
            constraint_nameplate_inventory(instance=instance, loc_res_dict=scenario.loc_res_dict,
                                           network_scale_level=scenario.network_scale_level,
                                           scheduling_scale_level=scenario.scheduling_scale_level)

            constraint_storage_max(instance=instance, store_max=scenario.store_max,
                                   loc_res_dict=scenario.loc_res_dict,
                                   network_scale_level=scenario.network_scale_level)

            constraint_storage_min(instance=instance, store_min=scenario.store_min,
                                   loc_res_dict=scenario.loc_res_dict,
                                   network_scale_level=scenario.network_scale_level)

        if Constraints.PRODUCTION in constraints:

            constraint_production_mode(instance=instance, mode_dict=scenario.mode_dict,
                                       scheduling_scale_level=scenario.scheduling_scale_level)

            constraint_nameplate_production(instance=instance, capacity_factor=scenario.capacity_factor,
                                            loc_pro_dict=scenario.loc_pro_dict,
                                            network_scale_level=scenario.network_scale_level,
                                            scheduling_scale_level=scenario.scheduling_scale_level)

            constraint_production_max(instance=instance, prod_max=scenario.prod_max,
                                      loc_pro_dict=scenario.loc_pro_dict,
                                      network_scale_level=scenario.network_scale_level)

            constraint_production_min(instance=instance, prod_min=scenario.prod_min,
                                      loc_pro_dict=scenario.loc_pro_dict,
                                      network_scale_level=scenario.network_scale_level)

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
                                         multiconversion=scenario.multiconversion, mode_dict=scenario.mode_dict, inventory_zero=inventory_zero)

            constraint_resource_consumption(instance=instance, loc_res_dict=scenario.loc_res_dict,
                                            cons_max=scenario.cons_max,
                                            scheduling_scale_level=scenario.scheduling_scale_level, availability_factor=scenario.availability_factor)

            constraint_resource_purchase(instance=instance, price_factor=scenario.price_factor, price=scenario.price,
                                         loc_res_dict=scenario.loc_res_dict,
                                         scheduling_scale_level=scenario.scheduling_scale_level,
                                         purchase_scale_level=scenario.purchase_scale_level)

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

        if Constraints.TRANSPORT in constraints:

            if len(scenario.location_set) > 1:
                constraint_transport_export(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                            transport_avail_dict=scenario.transport_avail_dict)
                constraint_transport_import(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                            transport_avail_dict=scenario.transport_avail_dict)
                constraint_transport_exp_UB(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                            network_scale_level=scenario.network_scale_level,
                                            trans_max=scenario.trans_max,
                                            transport_avail_dict=scenario.transport_avail_dict)
                constraint_transport_imp_UB(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                            network_scale_level=scenario.network_scale_level,
                                            trans_max=scenario.trans_max,
                                            transport_avail_dict=scenario.transport_avail_dict)
                constraint_transport_balance(
                    instance=instance, scheduling_scale_level=scenario.scheduling_scale_level)

                constraint_transport_imp_cost(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                              trans_cost=scenario.trans_cost, distance_dict=scenario.distance_dict)
                constraint_transport_cost(
                    instance=instance, scheduling_scale_level=scenario.scheduling_scale_level)
                constraint_transport_cost_network(
                    instance=instance, network_scale_level=scenario.network_scale_level)

        if Constraints.NETWORK in constraints:
            generate_network_binary_vars(
                instance=instance, scale_level=scenario.network_scale_level)

            constraint_storage_facility(instance=instance, store_max=scenario.store_max,
                                        loc_res_dict=scenario.loc_res_dict,
                                        network_scale_level=scenario.network_scale_level)

            constraint_production_facility(instance=instance, prod_max=scenario.prod_max,
                                           loc_pro_dict=scenario.loc_pro_dict,
                                           network_scale_level=scenario.network_scale_level)

            constraint_min_production_facility(instance=instance, prod_min=scenario.prod_min,
                                               loc_pro_dict=scenario.loc_pro_dict,
                                               network_scale_level=scenario.network_scale_level)

            constraint_min_storage_facility(instance=instance, store_min=scenario.store_min,
                                            loc_res_dict=scenario.loc_res_dict,
                                            network_scale_level=scenario.network_scale_level)

            instance.del_component(instance.constraint_storage_min)
            instance.del_component(instance.constraint_production_min)

        if Constraints.MODE in constraints:
            generate_mode_vars(
                instance=instance, scale_level=scenario.scheduling_scale_level, mode_dict=scenario.mode_dict)

            constraint_production_mode_facility(instance=instance, prod_max=scenario.prod_max,
                                                loc_pro_dict=scenario.loc_pro_dict,
                                                scheduling_scale_level=scenario.scheduling_scale_level)
            constraint_production_mode_binary(instance=instance, mode_dict=scenario.mode_dict,
                                              scheduling_scale_level=scenario.scheduling_scale_level,
                                              network_scale_level=scenario.network_scale_level)

        if Constraints.MATERIAL in constraints:
            generate_material_vars(
                instance=instance, scale_level=scenario.network_scale_level)

            constraint_material_process(
                instance=instance, process_material_dict=scenario.process_material_dict, network_scale_level=scenario.network_scale_level)
            constraint_material_location(
                instance=instance, network_scale_level=scenario.network_scale_level)
            constraint_material_network(
                instance=instance, network_scale_level=scenario.network_scale_level)

        if gwp is not None:
            constraint_global_warming_potential_network_reduction(
                instance=instance, network_scale_level=scenario.network_scale_level,
                gwp_reduction_pct=gwp_reduction_pct, gwp=gwp)

        if objective == Objective.COST:
            constraint_demand(instance=instance, demand_scale_level=scenario.demand_scale_level,
                              scheduling_scale_level=scenario.scheduling_scale_level, demand=demand,
                              demand_factor=scenario.demand_factor, loc_res_dict=scenario.loc_res_dict)

            objective_cost(
                instance=instance, network_scale_level=scenario.network_scale_level, constraints=constraints)

        if objective == Objective.PROFIT:
            constraint_demand(instance=instance, demand_scale_level=scenario.demand_scale_level,
                              scheduling_scale_level=scenario.scheduling_scale_level, demand=demand,
                              demand_factor=scenario.demand_factor, loc_res_dict=scenario.loc_res_dict)
            constraint_network_cost(
                instance=instance, network_scale_level=scenario.network_scale_level, constraints=constraints)
            constraint_resource_revenue(instance=instance, loc_res_dict=scenario.loc_res_dict, revenue=scenario.revenue,
                                        scheduling_scale_level=scenario.scheduling_scale_level, revenue_factor=scenario.revenue_factor)
            constraint_location_revenue(
                instance=instance, network_scale_level=scenario.network_scale_level, cluster_wt=scenario.cluster_wt)
            constraint_network_revenue(
                instance=instance, network_scale_level=scenario.network_scale_level)
            objective_profit(
                instance=instance, network_scale_level=scenario.network_scale_level, constraints=constraints)

        if objective == Objective.MIN_DISCHARGE:
            constraint_demand(instance=instance, demand_scale_level=scenario.demand_scale_level,
                              scheduling_scale_level=scenario.scheduling_scale_level, demand=demand,
                              demand_factor=scenario.demand_factor, loc_res_dict=scenario.loc_res_dict)

            constraint_network_cost(
                instance=instance, network_scale_level=scenario.network_scale_level, constraints=constraints)

            objective_discharge_min(instance=instance, resource=objective_resource,
                                    network_scale_level=scenario.network_scale_level)

        if objective == Objective.MAX_DISCHARGE:
            constraint_demand(instance=instance, demand_scale_level=scenario.demand_scale_level,
                              scheduling_scale_level=scenario.scheduling_scale_level, demand=demand,
                              demand_factor=scenario.demand_factor, loc_res_dict=scenario.loc_res_dict)

            constraint_network_cost(
                instance=instance, network_scale_level=scenario.network_scale_level, constraints=constraints)

            objective_discharge_max(instance=instance, resource=objective_resource,
                                    network_scale_level=scenario.network_scale_level)

        if objective == Objective.MIN_GWP:
            constraint_demand(instance=instance, demand_scale_level=scenario.demand_scale_level,
                              scheduling_scale_level=scenario.scheduling_scale_level, demand=demand,
                              demand_factor=scenario.demand_factor, loc_res_dict=scenario.loc_res_dict)

            constraint_network_cost(
                instance=instance, network_scale_level=scenario.network_scale_level, constraints=constraints)

            objective_gwp_min(
                instance=instance, network_scale_level=scenario.network_scale_level)

        if scenario.capacity_bounds is not None:
            constraint_min_capacity_facility(instance=instance, loc_pro_dict=scenario.loc_pro_dict,
                                             network_scale_level=scenario.network_scale_level, capacity_bounds=scenario.capacity_bounds)

        if write_lpfile is True:
            instance.write(f'{scenario.name}.lp')

        instance.dual = Suffix(direction=Suffix.IMPORT_EXPORT)

        return instance

    if model_class is ModelClass.MPLP:
        A, b, c, H, CRa, CRb, F = scenario.matrix_form()

        matrix_dict = {'A': A, 'b': b, 'c': c,
                       'H': H, 'CRa': CRa, 'CRb': CRb, 'F': F}

        return matrix_dict
