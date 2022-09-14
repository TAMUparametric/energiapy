# %%
import pandas
from numpy import poly1d, polyfit
from src.energiapy.components.temporal_scale import Temporal_scale
from src.energiapy.components.resource import Resource
from src.energiapy.components.process import Process
from src.energiapy.components.material import Material
from src.energiapy.components.location import Location
from src.energiapy.components.network import Network
from src.energiapy.components.scenario import Scenario
from src.energiapy.components.transport import Transport
from src.energiapy.components.result import Result
from src.energiapy.model.formulate_milp import formulate_milp
from src.energiapy.utils.data_utils import get_data, make_henry_price_df
from src.energiapy.utils.nsrdb_utils import fetch_nsrdb_data
from src.energiapy.plot import plot
from src.energiapy.model.pyomo_solve import solve
from src.energiapy.utils.cluster_utils import reduce_scenario, agg_hierarchial_elbow, Clustermethod
from src.energiapy.utils.data_utils import load_results
from src.energiapy.model.pyomo_sets import generate_sets
from src.energiapy.model.pyomo_vars import *
from src.energiapy.model.pyomo_cons import *
from src.energiapy.model.pyomo_objs import cost_objective, uncertainty_cost_objective
import matplotlib.pyplot as plt
from pyomo.environ import ConcreteModel, Suffix
import random

ho_solar_df = pandas.read_csv('data/ho_solar.csv', index_col=0) #Houston solar dni
ho_wind_df = pandas.read_csv('data/ho_wind.csv', index_col=0) #Houston wind speeds


hp_price_daily_df = make_henry_price_df(
    file_name='data/Henry_Hub_Natural_Gas_Spot_Price_Daily.csv', year=2019, stretch=True)

cost_dict = get_data(file_name='data/cost_dict')
# for i in cost_dict['HO']['moderate'].keys():
#     print(i + ':', cost_dict['HO']['moderate'][i]['0'])

scales = Temporal_scale(discretization_list=[1, 365, 24])

bigM = 10**3  # very large number
smallM = 0.1
water_price = 31.70  # $/5000gallons
power_price = 8  # cents/kWh
ur_price = 42.70  # 250 Pfund U308 (Uranium)
A_f = 0.05  # annualization factor
# CO2_res = 0.2
pv_start = 0
ake_start = 0
smrh_start = 0
smr_start = 0
asmr_start = 0


Charge = Resource(name='Charge', sell=False,
                  store_max=bigM, basis='MW', label='Battery energy', block='energystorage')
Solar = Resource(
    name='Solar', cons_max=bigM, basis='MW', label='Solar Power', block='energyfeedstock')
Wind = Resource(name='Wind', cons_max= bigM, basis='MW', label='Wind Power', block='energyfeedstock')
H2_L = Resource(name='H2_L', store_max=10**4, revenue=2,
                mile=1/(0.1180535*1.60934), basis='kg', label='Hydrogen - Geological', block='resourcestorage')
H2 = Resource(name='H2', basis='kg', sell = True, demand = True, label='Hydrogen', block='Resource')
H2O = Resource(name='H2O', cons_max=10**6,
               price= 0.001, basis='kg', label='Water', block='Resource')
            #    price=water_price/(5000*3.7854), basis='kg', label='Water', block='Resource')
O2 = Resource(name='O2', sell=True, loss=0.07,
              basis='kg', label='Oxygen', block='Resource')
CH4 = Resource(name='CH4', cons_max=10 **
               6, price=1, basis='kg', label='Natural gas', block='materialfeedstock', varying_cost_df=hp_price_daily_df)
CO2 = Resource(name='CO2', basis='kg',
               label='Carbon dioxide', block='Resource')
CO2_Vent = Resource(
    name='CO2_Vent', sell=True, basis='kg', label='Carbon dioxide - Vented', block='resourcedischarge')
# Power= Resource(name= 'Power', sell= True, store_max=0,   \
#    mile= (10**3)/(0.2167432**1.60934), label= 'Renewable power generated')
Power = Resource(name='Power', basis='MW',
                 label='Renewable power generated', block='Resource')


LiI_c = Process(name='LiI_c', conversion={Charge: 1, Power: -1}, cost = cost_dict['HO']['moderate']['LiI_c']['0'],\
    prod_max=5, trl='nrel', block='power_storage', label='Lithium-ion battery', citation='Zakeri 2015')
LiI_d = Process(name='LiI_d', conversion={Charge: -1.1765, Power: 1}, cost =  {'CAPEX': smallM, 'Fixed O&M': 0, 'Variable O&M': smallM, \
    'units': '$/kg','source': 'dummy'}, \
    prod_max=5, trl='discharge', block='power_storage', label='Lithium-ion battery discharge', citation='Zakeri 2015')
WF = Process(name='WF', conversion={Wind: -1, Power: 1, H2O: -1}, cost=cost_dict['HO']['moderate']['WF']['0'],
             prod_max=100, gwp=52700, land=10800/1800, trl='nrel', block='power_generation',
             label='Wind mill array', citation='Use windtoolkit conversion', varying_capacity_df=ho_wind_df, p_fail= 0.05)
PV = Process(name='PV', intro_scale=pv_start, conversion={Solar: -1, Power: 1, H2O: -20}, cost=cost_dict['HO']['moderate']['PV']['0'],
             prod_max=bigM, gwp=53000, land=13320/1800, trl='nrel', block='power_generation', \
                 label='Solar photovoltaics (PV) array', citation='Use pvlib conversion', varying_capacity_df=ho_solar_df, p_fail = 0.05)
AKE = Process(name='AKE', intro_scale=ake_start, conversion={Power: -1, H2: 19.474, O2: 763.2, H2O: -175.266},
              cost=cost_dict['HO']['moderate']['AKE']['0'], prod_max=bigM, trl='utility', block='material_production',
              label='Alkaline water electrolysis (AWE)', citation='Demirhan et al. 2018 AIChE paper', p_fail= 0.05)  # 20.833 MW required to produce 1000t/day.H2
SMR = Process(name='SMR', intro_scale=smr_start, cost= {'CAPEX': 2400, 'Fixed O&M': 800, 'Variable O&M': 0.05, 'units': '$/kg', 'source': 'dummy'}, \
    conversion={Power: -1.11*10**(-3), CH4: -3.76, H2O: -23.7, H2: 1, CO2_Vent: 9.4979}, prod_max=bigM, gwp=0, trl='enterprise',
                      block='material_production', label='Steam methane reforming', citation='Mosca 2020', p_fail= 0.05)
H2_L_c = Process(name='H2_L_c', conversion={Power: -4.17*10**(-4), H2_L: 1, H2: -1}, cost={'CAPEX': 1000, 'Fixed O&M': 600, 'Variable O&M': 0.05,
                                                                                           'units': '$/kg', 'source': 'dummy'},
                 prod_max=bigM, gwp=0, trl='repurposed', block='material_storage', label='Hydrogen geological storage',
                 citation='Bossel and Eliasson - Energy and the Hydrogen Economy', p_fail= 0.05)
H2_L_d = Process(name='H2_L_d', conversion={H2_L: -1, H2: 1}, prod_max=bigM, gwp=0, trl='nocost', cost={'CAPEX': smallM, 'Fixed O&M': 0, 'Variable O&M': 1,                                                                                                        'units': '$/kg', 'source': 'dummy'},
                 block='material_storage', label='Hydrogen geological storage discharge', citation='Bossel and Eliasson - Energy and the Hydrogen Economy', p_fail= 0.01)

# ho_demand_dict = {(0, i, j): 100.0 for i,j in product(range(scales.discretization_list[1]), range(scales.discretization_list[2]))}
ho_demand_dict = {(0, i): 1000.0 for i in range(scales.discretization_list[1])}

HO = Location(name='HO', processes={LiI_c, LiI_d, PV, WF, AKE, SMR, H2_L_c, H2_L_d}, demand= ho_demand_dict, scales=scales, label='Houston')

# for i in HO.processes:
#     print(f"{i.label}: {i.cost}: {i.citation}")

# plot.capacity_factor(location= HO, process= PV, color= 'orange')
# plot.capacity_factor(location= HO, process= WF, color= 'blue')
# plot.cost_factor (location= HO, resource= CH4, color= 'red')


case_sl = Scenario(name= 'shell', network= HO, scales= scales,  expenditure_scale_level= 2, scheduling_scale_level= 2, \
    network_scale_level= 0, demand_scale_level= 1, label= 'shell milp case study (HO)')

reduced_case_sl = reduce_scenario(
    scenario=case_sl, location=HO, periods=20, scale_level=1, method=Clustermethod.agg_hierarchial)


#%%
def formulate_houston_milp(scenario: Scenario, carbon_bound:float= None, carbon_reduction_percentage:float= 0) -> ConcreteModel:
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
    
    if carbon_bound is not None:
        carbon_emission_constraint(instance= instance, network_scale_level= scenario.network_scale_level, \
            carbon_reduction_percentage = carbon_reduction_percentage, carbon_bound = carbon_bound)

    # carbon_emission_location_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    # carbon_emission_network_constraint(instance= instance, network_scale_level= scenario.network_scale_level)
    

    cost_objective(instance=instance,
                   network_scale_level=scenario.network_scale_level)

    return instance



reduced_milp_sl = formulate_houston_milp(scenario= reduced_case_sl)
results = solve(scenario = reduced_case_sl, instance= reduced_milp_sl, solver= 'gurobi', name=f"Houston_MILP",\
    saveformat= '.pkl', print_solversteps = True)


# def carbon_reduction_cases(scenario: Scenario, carbon_bound:float, discretization_points:float = 10):
#     iter_list = [100.0/discretization_points*(i + 1) for i in range(discretization_points-1)]

#     for iter_ in iter_list:
#         milp_ = formulate_houston_milp(scenario= scenario, carbon_bound= carbon_bound \
#             , carbon_reduction_percentage= iter_)
#         results_ = solve(scenario = scenario, instance= milp_, solver= 'gurobi', name=f"Houston_MILP_C{int(iter_)}",\
#             saveformat= '.pkl')
#     return milp_


# carbon_reduction_cases(scenario = reduced_case_sl, carbon_bound = results_reduced_sl.output['S_location'][('HO', 'CO2_Vent', 0)], discretization_points = 10)

# results = {i: load_results(f"Houston_MILP_C{i+1}0.pkl") for i in range(9)}

# carbon = [results[i].output['S_location'][('HO', 'CO2_Vent', 0)] for i in range(9)]
# electrolysis = [results[i].output['P_location'][('HO', 'AKE', 0)] for i in range(9)]
# carbon_f = [results_flex[i].output['S_location'][('HO', 'CO2_Vent', 0)] for i in range(9)]
# smrh = [results[i].output['P_location'][('HO', 'SMRH', 0)] for i in range(9)]
# smr = [results[i].output['P_location'][('HO', 'SMR', 0)] for i in range(9)]
# cap_smr = [results[i].output['Cap_P'][('HO', 'SMR', 0)] for i in range(9)]
# cap_smrh = [results[i].output['Cap_P'][('HO', 'SMRH', 0)] for i in range(9)]
# cap_ake = [results[i].output['Cap_P'][('HO', 'AKE', 0)] for i in range(9)]
# LCOE = [results[i].output['objective'] /(results[i].output['S_location'][('HO', 'H2_L', 0)] + results[i].output['S_location'][('HO', 'H2_C', 0)]) for i in range(9)]

# objective = [results[i].output['objective'] for i in range(9)]
# objective_f = [results_flex[i].output['objective'] for i in range(9)]

# plt.plot(carbon, objective)
# plt.plot(carbon_f, objective_f)


# plt.plot(LCOE)


# # plt.plot(smrh)
# # plt.plot(smr)
# plt.plot(cap_ake)

#%%
def flexibility_reformulation(scenario: Scenario, affix_results: Result, carbon_bound:float= None, carbon_reduction_percentage:float= 0):
    instance = ConcreteModel()

    generate_sets(instance=instance, location_set=scenario.location_set, transport_set=scenario.transport_set, scales=scenario.scales,
                  process_set=scenario.process_set, resource_set=scenario.resource_set, material_set=scenario.material_set,
                  source_set=scenario.source_locations, sink_set=scenario.sink_locations)

    generate_scheduling_vars(
        instance=instance, scale_level=scenario.scheduling_scale_level)
    generate_network_vars(
        instance=instance, scale_level=scenario.network_scale_level)
    generate_uncertainty_vars(
        instance=instance, scale_level=scenario.network_scale_level)
    
    if len(instance.locations) > 1:
        generate_transport_vars(
            instance=instance, scale_level=scenario.scheduling_scale_level)

    inventory_balance_constraint(instance=instance, scheduling_scale_level=scenario.scheduling_scale_level,
                                 conversion=scenario.conversion)
    nameplate_production_constraint(instance=instance, capacity_factor=scenario.capacity_factor,
                                    network_scale_level=scenario.network_scale_level, scheduling_scale_level=scenario.scheduling_scale_level)
    
    # nameplate_production_failure_constraint(instance=instance, fail_factor=scenario.fail_factor,
    #                                 network_scale_level=scenario.network_scale_level, scheduling_scale_level=scenario.scheduling_scale_level)
    
    nameplate_inventory_constraint(instance=instance, loc_res_dict=scenario.loc_res_dict, network_scale_level=scenario.network_scale_level,
                                   scheduling_scale_level=scenario.scheduling_scale_level)
    resource_consumption_constraint(instance=instance, loc_res_dict=scenario.loc_res_dict,
                                    cons_max=scenario.cons_max, scheduling_scale_level=scenario.scheduling_scale_level)
    resource_purchase_constraint(instance=instance, cost_factor=scenario.cost_factor, price=scenario.price,
                                 loc_res_dict=scenario.loc_res_dict, scheduling_scale_level=scenario.scheduling_scale_level,
                                 expenditure_scale_level=scenario.expenditure_scale_level)

    production_facility_affix_constraint(instance=instance, affix_production_cap = affix_results.output['Cap_P'],
                                   loc_pro_dict=scenario.loc_pro_dict, network_scale_level=scenario.network_scale_level)
    
    storage_facility_affix_constraint(instance=instance, affix_storage_cap = affix_results.output['Cap_S'],
                                loc_res_dict=scenario.loc_res_dict, network_scale_level=scenario.network_scale_level)

    # production_facility_constraint(instance=instance, prod_max=scenario.prod_max,
    #                                loc_pro_dict=scenario.loc_pro_dict, network_scale_level=scenario.network_scale_level)
    # storage_facility_constraint(instance=instance, store_max=scenario.store_max,
    #                             loc_res_dict=scenario.loc_res_dict, network_scale_level=scenario.network_scale_level)
    
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
    
    if carbon_bound is not None:
        carbon_emission_constraint(instance= instance, network_scale_level= scenario.network_scale_level, \
            carbon_reduction_percentage = carbon_reduction_percentage, carbon_bound = carbon_bound)
    
    instance.dual = Suffix(direction=Suffix.IMPORT)


    cost_objective(instance=instance,
                   network_scale_level=scenario.network_scale_level)
    

    return instance



flex_LP = flexibility_reformulation(scenario= reduced_case_sl, affix_results= results)

results_flex = solve(scenario = reduced_case_sl, instance= flex_LP, solver= 'gurobi', name=f"Houston_LP_Flex",\
        saveformat= '.pkl', print_solversteps = True)
#%%
def flexibility_MIP_reformulation(scenario: Scenario, affix_results: Result, carbon_bound:float= None, carbon_reduction_percentage:float= 0.0, penalty:float = 0.0):
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

    generate_uncertainty_vars(
        instance=instance, scale_level=scenario.demand_scale_level)

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
    
    nameplate_production_failure_constraint(instance=instance, fail_factor=scenario.fail_factor,
                                    network_scale_level=scenario.network_scale_level, scheduling_scale_level=scenario.scheduling_scale_level)
    
    # production_facility_affix_constraint(instance=instance, affix_production_cap = affix_results.output['Cap_P'],
    #                                loc_pro_dict=scenario.loc_pro_dict, network_scale_level=scenario.network_scale_level)
    
    # storage_facility_affix_constraint(instance=instance, affix_storage_cap = affix_results.output['Cap_S'],
    #                             loc_res_dict=scenario.loc_res_dict, network_scale_level=scenario.network_scale_level)

    production_facility_constraint(instance=instance, prod_max=scenario.prod_max,
                                   loc_pro_dict=scenario.loc_pro_dict, network_scale_level=scenario.network_scale_level)
    storage_facility_constraint(instance=instance, store_max=scenario.store_max,
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

    demand_constraint_flex(instance=instance, demand_scale_level=scenario.demand_scale_level,
                      scheduling_scale_level=scenario.scheduling_scale_level, demand=scenario.demand)
    
    if carbon_bound is not None:
        carbon_emission_constraint(instance= instance, network_scale_level= scenario.network_scale_level, \
            carbon_reduction_percentage = carbon_reduction_percentage, carbon_bound = carbon_bound)
    
    instance.dual = Suffix(direction=Suffix.IMPORT)


    uncertainty_cost_objective(instance=instance,
                   network_scale_level=scenario.network_scale_level, uncertainty_scale_level = scenario.demand_scale_level, penalty = penalty)
    

    return instance



#%%
flex_MILP = flexibility_MIP_reformulation(scenario= reduced_case_sl, affix_results= results, penalty = 300000)

results_MIP_flex = solve(scenario = reduced_case_sl, instance= flex_MILP, solver= 'gurobi', name=f"Houston_MIP_Flex",\
        saveformat= '.pkl', print_solversteps = True)
#%%


# results = load_results(filename = "Houston_MILP.pkl")
# results_flex = {i: load_results(filename = f"Houston_MILP_Flex{i}.pkl") for i in range(8)}
# results_flex = load_results(filename = f"Houston_MILP_Flex.pkl") 

#%%
plot.schedule(results=results, y_axis='Inv',
               component='H2_L', location='HO')
plot.schedule(results= results_flex, y_axis='Inv',
               component='H2_L', location='HO')
plot.schedule(results= results_MIP_flex, y_axis='Inv',
               component='H2_L', location='HO')
#%%
plot.schedule(results=results, y_axis='P',
               component='SMR', location='HO')

plot.schedule(results=results_flex, y_axis='P',
               component='SMR', location='HO')

plot.schedule(results=results_MIP_flex, y_axis='P',
               component='SMR', location='HO')

#%%
plot.contribution(results = results, y_axis = 'P_location', location = 'HO')
plot.contribution(results = results_flex, y_axis = 'P_location', location = 'HO')
plot.contribution(results = results_MIP_flex, y_axis = 'P_location', location = 'HO')


# for i in range(8):
#     plot.contribution(results = results_flex[i], y_axis = 'P_location', location = 'HO')
    

#%%
plot.capacity_utilization(results, 'HO')
plot.capacity_utilization(results_flex, 'HO')
plot.capacity_utilization(results_MIP_flex, 'HO')

#%%


#%%


# def flex_carbon_reduction_cases(scenario: Scenario, results: Result, carbon_bound:float, discretization_points:float = 10):
#     iter_list = [100.0/discretization_points*(i + 1) for i in range(discretization_points-1)]
#     iterr_ = 0
#     for iter_ in iter_list:
#         milp_ = flexibility_reformulation(scenario= scenario, affix_results= results[iterr_], carbon_bound= carbon_bound \
#             , carbon_reduction_percentage= iter_)
#         results_ = solve(scenario = scenario, instance= milp_, solver= 'gurobi', name=f"Houston_MILP_F{int(iter_)}",\
#             saveformat= '.pkl')
#         iterr_ += 1
#     return milp_

# flex_carbon_reduction_cases(scenario = reduced_case_sl,  results = results, carbon_bound = results_reduced_sl.output['S_location'][('HO', 'CO2_Vent', 0)], discretization_points = 10)

# results_flex = {i: load_results(f"Houston_MILP_F{i+1}0.pkl") for i in range(9)}

# for i in range(8):
#     flex_LP = flexibility_reformulation(scenario= reduced_case_sl, affix_results= results_reduced_sl, carbon_bound= results_reduced_sl.output['S_location'][('HO', 'CO2_Vent', 0)], carbon_reduction_percentage= 10*i)

#     results_flex = solve(scenario = reduced_case_sl, instance= flex_LP, solver= 'gurobi', name=f"Houston_MILP_Flex{i}",\
#         saveformat= '.pkl', print_solversteps = True)
    


#%%
for i in range(8):
    print(results_flex[i].duals['nameplate_production_constraint']['HO', 'WF', 0, 0 ,0])


# # %%
#  if heuristic == True:
#         # if last iteration was infeasible... diversify [toll is lower as well]
#         if objective[iter_ - 1] == 10**10:
#             toll = 0.5  # tolerance to be used
#             for prod in prod_list:  # problem is combinatorally divided for each product
#                 # print(prod)
#                 # ordered sources based on production potential
#                 prod_pot_ord = [source for source in list(
#                     prod_pot_ord_dict[prod].keys())]
#                 # fix sources [source_x = 1] for top two quartiles
#                 prod_pot_fix = prod_pot_ord[:int(round(len(prod_pot_ord)/2))]

#                 # print('prod_pot_ord')
#                 # print(prod_pot_ord)
#                 # print('prod_pot_fix')
#                 # print(prod_pot_fix)

#                 for source in range(n_sources):
#                     # print('source ' + str(source))
#                     if source in prod_pot_fix:  # source in 2nd quartile essentially
#                         # print('fix 1')
#                         # print(source)
#                         # generate a random number
#                         random_n = random.uniform(0, 1)
#                         # if number less than tolerance affix source [lower tolerance helps diversify]
#                         if random_n < toll:
#                             m.source_x[prod, source].fix(1.0)
#                         else:
#                             m.source_x[prod, source].fix(0.0)

#                         # now affix sinks with the 2nd quartile of distances
#                         sinks_distance_ord = [sink for sink in list(
#                             distances_ord_dict[source].keys())]
#                         sinks_distance_fix = sinks_distance_ord[:int(
#                             round(len(sinks_distance_ord)/2))]
#                         fix = 1.0  # affix transportation linkages to 1 only if source exists, and within 2nd distance quartile

#                     else:
#                         # print('fix 0')
#                         # print(source)
#                         random_n = random.uniform(0, 1)
#                         if random_n < toll:  # for the rest randomly affix some.
#                             m.source_x[prod, source].fix(0.0)
#                         else:
#                             m.source_x[prod, source].fix(1.0)

#                         sinks_distance_ord = [sink for sink in list(
#                             distances_ord_dict[source].keys())]
#                         sinks_distance_fix = sinks_distance_ord
#                         fix = 0.0  # affix transportation linkages to 0 if source does not exist
#                     # print('sinks_distance_ord')
#                     # print(sinks_distance_ord)
#                     # print('sinks_distance_fix')
#                     # print(sinks_distance_fix)
#                     for sink in range(n_sinks):
#                         if sink in sinks_distance_fix:
#                             # print('fix ' + str(fix))
#                             # print(sink)
#                             m.linkage_x[prod, sink, source].fix(fix)
#                         # else:
#                             # print('fix 0')
#                             # print(sink)
#                             # m.linkage_x[prod, sink, source].fix(0.0)

#         # if last iteration was not infeasible... intensify [toll is higher as well]
#         else:
#             toll = 0.8  # higher tolerance, accept more solutions
#             # first iter is set to MIP solution [can be changed, need to generalize].
#             if iter_ == 1:
#                 # so this is the first heuristic iteration
#                 for prod in prod_list:
#                     # print(prod)

#                     prod_pot_ord = [source for source in list(
#                         prod_pot_ord_dict[prod].keys())]  # order sources by prod pot
#                     # affix within 2nd quartile
#                     prod_pot_fix = prod_pot_ord[:int(
#                         round(len(prod_pot_ord)/2))]

#                     # print('prod_pot_ord')
#                     # print(prod_pot_ord)
#                     # print('prod_pot_fix')
#                     # print(prod_pot_fix)
#                     for source in range(n_sources):
#                         # print('source ' + str(source))
#                         if source in prod_pot_fix:
#                             # print('fix 1')
#                             # print(source)

#                             # located facilities greedily
#                             m.source_x[prod, source].fix(1.0)
#                             sinks_distance_ord = [sink for sink in list(
#                                 distances_ord_dict[source].keys())]
#                             sinks_distance_fix = sinks_distance_ord[:int(
#                                 round(len(sinks_distance_ord)/2))]
#                             fix = 1.0

#                         else:
#                             # print('fix 0')
#                             # print(source)

#                             # do not locate facilities here
#                             m.source_x[prod, source].fix(0.0)
#                             sinks_distance_ord = [sink for sink in list(
#                                 distances_ord_dict[source].keys())]
#                             sinks_distance_fix = sinks_distance_ord
#                             fix = 0.0
#                         # print('sinks_distance_ord')
#                         # print(sinks_distance_ord)
#                         # print('sinks_distance_fix')
#                         # print(sinks_distance_fix)
#                         for sink in range(n_sinks):
#                             if sink in sinks_distance_fix:
#                                 # print('fix ' + str(fix))
#                                 # print(sink)
#                                 # set all linkages to 1 from affixed sources to sinks
#                                 m.linkage_x[prod, sink, source].fix(fix)
#                             # else:
#                                 # print('fix 0')
#                                 # print(sink)
#                                 # m.linkage_x[prod, sink, source].fix(0.0)

#             else:
#                 if (iter_ > 3):
#                     # if solution has not improved
#                     if (objective[iter_-1] < 1.005*objective[iter_ - 2]):

#                         # print(objective[iter_-1], objective[iter_-2])
#                         print('===============================================')
#                         for prod, source in product(prod_list, range(n_sources)):
#                             # if source was already affixed to 1 and needs to be reassigned
#                             if source_re_dict[source][prod] == 1:
#                                 # randomly shuffle the affixed
#                                 random_n = random.uniform(0, 1)
#                                 if random_n < toll:
#                                     m.source_x[prod, source].fix(1.0)
#                                 else:
#                                     m.source_x[prod, source].fix(0.0)

#                             else:  # if source was already affixed to 0 and needs to be reassigned
#                                 random_n = random.uniform(
#                                     0, 1)  # randomly shuffle
#                                 if random_n < toll:
#                                     m.source_x[prod, source].fix(1.0)
#                                 else:
#                                     m.source_x[prod, source].fix(0.0)

#                             for sink in range(n_sinks):
#                                 # if linkage was already affixed to 1 and needs to be reassigned
#                                 if linkage_re_dict[source][sink][prod] == 1:
#                                     random_n = random.uniform(0, 1)
#                                     if random_n < toll:
#                                         m.linkage_x[prod, sink,
#                                                     source].fix(1.0)
#                                     else:
#                                         m.linkage_x[prod, sink,
#                                                     source].fix(0.0)

#                                 else:  # if linkage was already affixed to 0 and needs to be reassigned
#                                     random_n = random.uniform(0, 1)
#                                     if random_n < toll:
#                                         m.linkage_x[prod, sink,
#                                                     source].fix(1.0)
#                                     else:
#                                         m.linkage_x[prod, sink,
#                                                     source].fix(0.0)

#                 else:  # if solution is not too bad, start stitching the solution
#                     # note that sources and linkages are cycled with the intension of being affixed
#                     # not utilized facilities and linakges are set to 0
#                     # this helps improve the solution by avoiding uncessary facilities, linkages
#                     # All binaries are still affixed!
#                     print('++++++++++++++++++++++++++++++++++++++++++++++++++++++')

#                     for prod, source in product(prod_list, range(n_sources)):
#                         # keep the affixed sources
#                         if source_re_dict[source][prod] == 1:
#                             m.source_x[prod, source].fix(1.0)
#                         else:
#                             m.source_x[prod, source].fix(0.0)

#                         for sink in range(n_sinks):  # keep the affixed linkages
#                             if linkage_re_dict[source][sink][prod] == 1:
#                                 m.linkage_x[prod, sink, source].fix(1.0)
#                             else:
#                                 m.linkage_x[prod, sink, source].fix(0.0)


