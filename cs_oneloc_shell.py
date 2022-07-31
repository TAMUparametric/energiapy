
#%%
"""
Single location case study:

Example case study implemeted on the energia python module
The presented simultaneous design and scheduling MIP framework models:
the hydrogen economy, carbon capture utilization & storage, power generation under an integrated network

Costing for available technologies are imported from NREL's annual technology baseline
The rest are fed through a variety of sources from literature
Costing is considered at three distinct levels of research and policy push: conservative, moderate, advanced
The trajectories for introduced processes are set as per their TRL levels
Tax credits for CCUS can be provided as per the 45Q IRS amendment to the tax code
Varying power inputs for solar (using PVlib) and wind (using windtoolkit) power generation are introduced as a conversion factor (f_conv)
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "1.0.0"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"


# *-------------------------Import modules------------------------------------
# from turtle import distance
from os import stat
import pandas
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
from src.energiapy.graph import graph
from src.energiapy.model.pyomo_solve import solve

# *-------------------------Import data------------------------------------

#get solar data as dni and wind data as wind speed for most populated data point in Harris county (TX) at an hourly resolution
ho_wind_df = fetch_nsrdb_data(attrs = ['wind_speed'], year = 2019, state = 'Texas', county = 'Harris', resolution= 'hourly') #(lon_lat, wind df)
ho_solar_df = fetch_nsrdb_data(attrs = ['dni'], year = 2019, state = 'Texas', county = 'Harris', resolution= 'hourly') #(lon_lat, wind df)

#varying natural gas prices
hp_price_daily_df = make_henry_price_df(
    file_name='Henry_Hub_Natural_Gas_Spot_Price_Daily.csv', year=2019, stretch=False)
 
# *-------------------------Temporal scales------------------------------------
# Temporal_scale is used to define a descritizations of the temporal scale
# E.g.: A year at annual, daily and hourly descritization cane be represented as:
# Annual (1x1 = 1) - network level trends and their inherent uncertainties can be well 
# represented at an annual scale, for example, augmentations in process
# efficiencies, reductions in technology cost. 
# Daily (1x365 = 365) - Purchase level decisions can be sufficienctly described at a daily scale.
# Hourly (1x365x24 = 8760)- Solar and wind availability can be represented to within some factor
# of accuracy at an hourly scale. 
scales = Temporal_scale(discretization_list = [1, 365, 24])
# scales = temporal_scale(discretization_list = [1, 2, 3])

# *-------------------------Constants defined here for ease------------------------------------
bigM = 10**20 #very large number
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

# *-------------------------Resources-------------------------------------
#Resources can be - 
# consumed, e.g. solar, wind 
# purchased (consumed at a cost), e.g. natural gas, water 
# sold, e.g. hydrogen, power
# produced, e.g. hydrogen, methanol
# stored, e.g. power as charge or elevated water, hydrogen as cryogenic or compressed 
# discharged (sold for 0 currency), e.g. CO2, O2 (could be assigned profit)
# basis can be declared, maximum consumption and storage can be defined
# selling and purchase costs can vary. Natural gas and power for example 
# labels and blocks can be defined
# these can be represented as cost factors (0,1) multiplied to a base resource cost 
# *------------------------------------------------------------------------

Charge = Resource(name='Charge', sell=False,
                          store_max=bigM, basis='MW', label='Battery energy', block= 'energystorage')
Air_C = Resource(name='Air_C', store_max=bigM, basis='MW',
                         label='CAES energy', block= 'energystorage')
H2O_E = Resource(name='H2O_E', store_max=bigM, basis='MW',
                         label='PSH energy', block= 'energystorage')
Solar = Resource(
    name='Solar', cons_max=10**20, basis='MW', label='Solar Power', block = 'energyfeedstock')
Wind = Resource(name='Wind', cons_max=10 **
                        20, basis='MW', label='Wind Power', block = 'energyfeedstock')
Uranium = Resource(name='Uranium', cons_max=10 **
                           20, price=ur_price/(250/2), basis='kg', label='Uranium', block = 'energyfeedstock')
H2_C = Resource(name='H2_C', sell=True, store_max=10**4, loss=0.025/24, revenue=2, mile=1/(0.1180535*1.60934),
                        demand=True, basis='kg', label='Hydrogen - Local Cryo', block= 'resourcestorage') 
H2_L = Resource(name='H2_L', sell=True, store_max=10**10, demand=True, revenue=2,
                        mile=1/(0.1180535*1.60934), basis='kg', label='Hydrogen - Geological', block= 'resourcestorage')
H2 = Resource(name='H2', basis='kg', label='Hydrogen', block= 'Resource')
H2_B = Resource(name='H2_B', basis='kg', label='Blue hydrogen', block= 'product')
H2_G = Resource(name='H2_G', basis='kg', label='Green hydrogen', block= 'product')
H2O = Resource(name='H2O', cons_max=10**20,
                       price=water_price/(5000*3.7854), basis='kg', label='Water', block= 'Resource')
O2 = Resource(name='O2', sell=True, loss=0.07,
                      basis='kg', label='Oxygen', block = 'Resource')
CH4 = Resource(name='CH4', cons_max=10 **
                       20, price=1, basis='kg', label='Natural gas', block = 'materialfeedstock', varying_cost_df= hp_price_daily_df)
CO2 = Resource(name='CO2', basis='kg', label='Carbon dioxide', block = 'Resource')
CO2_DAC = Resource(
    name='CO2_DAC', basis='kg', label='Carbon dioxide - captured', block = 'carbonsequestration')
CO2_AQoff = Resource(
    name='CO2_AQoff', store_max=10**10, basis='kg', label='Carbon dioxide - sequestered', block = 'carbonsequestration')
CO2_EOR = Resource(
    name='CO2_EOR', store_max=10**10, basis='kg', label='Carbon dioxide - EOR', block = 'carbonsequestration')
CH3OH = Resource(name='CH3OH', sell=True, revenue=0.5,
                         mile=1/(0.0195508*1.60934), basis='kg', label='Methanol', block = 'resourcedischarge')
Power_Gr = Resource(name='Power_Gr', cons_max=10 **
                            20, price=power_price*(10), basis='kg', label='Grid electricity', block = 'energyfeedstock')
CO2_Vent = Resource(
    name='CO2_Vent', sell=True, basis='kg', label='Carbon dioxide - Vented', block = 'resourcedischarge')
# Power= Resource(name= 'Power', sell= True, store_max=0,   \
#    mile= (10**3)/(0.2167432**1.60934), label= 'Renewable power generated')
Power = Resource(name='Power', basis='MW',
                         label='Renewable power generated', block = 'Resource')

# *-------------------------Materials------------------------------------
# Materials required to build processes
Li = Material(name='Li', gwp=0, basis= 'kg', label='Lithium')


# *-------------------------Processes ------------------------------------
# Processes can convert resources, for example electorlysis converts 
# water and power into hydrogen.
# processes also require materials such as Lithium for Li-ion batteries 
# production capacity could be subject to variation. e.g. Solar PVs and Wind farms 
# intermittency can be represented through capacity factors (0,1)
# production costs and their trajectories can be defined
# blocks can be defined
# TRL trajectories can be defined 
# citations and sources can be added
# *------------------------------------------------------------------------


#cost of processes
cost_dict = get_data(file_name='cost_dict')

LiI_c = Process(name='LiI_c', conversion={Charge: 1, Power: -1}, cost = cost_dict['HO']['moderate']['LiI_c']['0'],\
    material_cons = {Li: 20}, prod_max=bigM, trl='nrel', block='power_storage', label='Lithium-ion battery', citation='Zakeri 2015')
LiI_d = Process(name='LiI_d', conversion={Charge: -1.1765, Power: 1}, cost = cost_dict['HO']['moderate']['LiI_d']['0'], \
    prod_max=bigM, trl='discharge', block='power_storage', label='Lithium-ion battery discharge', citation='Zakeri 2015')
CAES_c = Process(name='CAES_c', conversion={Air_C: 1, Power: -1}, cost = cost_dict['HO']['moderate']['CAES_c']['0'], \
    intro_scale=2, prod_max=bigM, trl='pilot', block='power_storage', label='Compressed air energy storage (CAES)', citation='Zakeri 2015')
CAES_d = Process(name='CAES_d', conversion={Air_C: -1.4286, Power: 1}, cost = cost_dict['HO']['moderate']['CAES_d']['0'],\
    intro_scale=2, prod_max=bigM, trl='discharge', block='power_storage', label='Compressed air energy storage (CAES) discharge', citation='Zakeri 2015')
PSH_c = Process(name='PSH_c', conversion={H2O_E: 1, Power: -1}, cost = cost_dict['HO']['moderate']['PSH_c']['0'], \
    intro_scale=0, prod_max=bigM, trl='nrel', block='power_storage', label='Pumped storage hydropower (PSH)', citation='Zakeri 2015')
PSH_d = Process(name='PSH_d', conversion={H2O: -1, Power: -1.4286}, cost = cost_dict['HO']['moderate']['PSH_d']['0'], \
    prod_max=bigM, trl='discharge', block='power_storage', label='Pumped storage hydropower (PSH) discharge', citation='Zakeri 2015')
PV = Process(name='PV', intro_scale=pv_start, conversion={Solar: -1, Power: 1, H2O: -20}, cost = cost_dict['HO']['moderate']['PV']['0'], \
    prod_max=bigM, gwp=53000, land=13320/1800, trl='nrel', block='power_generation', label='Solar photovoltaics (PV) array', citation='Use pvlib conversion', varying_capacity_df= ho_solar_df[1])
WF = Process(name='WF', conversion={Wind: -1, Power: 1, H2O: -1}, cost = cost_dict['HO']['moderate']['WF']['0'], \
    prod_max=bigM, gwp=52700, land=10800/1800, trl='nrel', block='power_generation', \
        label='Wind mill array', citation='Use windtoolkit conversion', varying_capacity_df= ho_wind_df[1])
AKE = Process(name='AKE', intro_scale=ake_start, conversion={Power: -1, H2_G: 19.474, O2: 763.2, H2O: -175.266}, \
    cost = cost_dict['HO']['moderate']['AKE']['0'], prod_max=bigM, trl='utility', block='material_production', \
        label='Alkaline water electrolysis (AWE)', citation='Demirhan et al. 2018 AIChE paper')  # 20.833 MW required to produce 1000t/day.H2
SMRH = Process(name='SMRH', intro_scale=smrh_start, conversion={Power: -1.11*10**(-3), CH4: -3.76, H2O: -23.7, H2_B: 1, CO2_Vent: 1.03, CO2: 9.332}, \
    cost = cost_dict['HO']['moderate']['SMRH']['0'], prod_max=bigM, gwp=0, trl='enterprise', block='material_production', \
        label='Steam methane reforming + CCUS', citation='Mosca 2020, 90pc capture')
# SMR = Process(name='SMR', intro_scale=smr_start, cost = cost_dict['HO']['moderate']['SMR']['0'], conversion={Power: -1.11*10**(-3), CH4: -3.76, H2O: -23.7, H2_B: 1, CO2_Vent: 9.4979}, prod_max=bigM, gwp=0, trl='enterprise',
#                       block='material_production', label='Steam methane reforming', citation='Mosca 2020')
ASMR = Process(name='ASMR', conversion={Uranium: -4.17*10**(-5), H2O: -3364.1, Power: 1}, cost = cost_dict['HO']['moderate']['ASMR']['0'], \
    intro_scale=asmr_start, gwp=9100, prod_max=bigM, land=1100/1800, trl='pilot', block='power_generation', label='Small modular reactors (SMRs)')
H2_C_c = Process(name='H2_C_c', conversion={Power: -1.10*10**(-3), H2_C: 1, H2: -1}, cost = cost_dict['HO']['moderate']['H2_C_c']['0'], \
    prod_max=12000, gwp=0, trl='pilot', block='material_storage', label='Hydrogen local storage (Compressed)', \
        citation='Bossel and Eliasson - Energy and the Hydrogen Economy')
H2_C_d = Process(name='H2_C_d',  conversion={H2_C: -1, H2: 1}, cost = cost_dict['HO']['moderate']['H2_C_d']['0'], prod_max=bigM, gwp=0, trl='nocost',
                         block='material_storage', label='Hydrogen local storage (Compressed) discharge', citation='Bossel and Eliasson - Energy and the Hydrogen Economy')
H2_L_c = Process(name='H2_L_c', conversion={Power: -4.17*10**(-4), H2_L: 1, H2: -1}, cost = cost_dict['HO']['moderate']['H2_L_c']['0'], prod_max=bigM, gwp=0, trl='repurposed',
                         block='material_storage', label='Hydrogen geological storage', citation='Bossel and Eliasson - Energy and the Hydrogen Economy')
H2_L_d = Process(name='H2_L_d', conversion={H2_L: -1, H2: 1}, prod_max=bigM, gwp=0, trl='nocost', cost = cost_dict['HO']['moderate']['H2_L_d']['0'],
                         block='material_storage', label='Hydrogen geological storage discharge', citation='Bossel and Eliasson - Energy and the Hydrogen Economy')
# SMRM = Process(name='SMRM', intro_scale=20, prod_max=bigM, gwp=0,
#                        trl='enterprise', block='material_production', label='Methanol SMR')
# MEFC = Process(name='MEFC', conversion={Power: -4.84*10**(-1), H2_G: -0.4048, CO2_DAC: -1.2143, CH3OH: 1}, intro_scale=6, prod_max=bigM, carbon_credit=True, trl='pilot',
#                        block='material_production', label='Catalytic methanol production', citation='Keith et al (2018), Fasihi et al (2019)')  # 10,000t/y
DAC = Process(name='DAC', conversion={Power: -1.93*10**(-4), H2O: -4.048, CO2_DAC: 1}, cost = cost_dict['HO']['moderate']['DAC']['0'], \
    intro_scale=4, prod_max=bigM, gwp=0, trl='pilot', block='CCUS', label='Direct air capture', citation='D. Belloti et al (2017)')
# DOWC = Process(name='DOWC', intro_scale=20, prod_max=bigM, gwp=0,
#                        trl='repurposed', block='CCUS', label='Depleted oil wells')
EOR = Process(name='EOR', intro_scale=0, conversion={Power: -0.00255, CO2: -1, CO2_EOR: 1, CO2_Vent: 0.67}, \
    cost = cost_dict['HO']['moderate']['EOR']['0'], prod_max=bigM, carbon_credit=True, \
        trl='enterprise', block='CCUS', label='CO2-Enhanced oil recovery')
AQoff_SMR = Process(name='AQoff_SMR', conversion={Power: -0.00128, CO2_AQoff: 1, CO2: -1}, cost = cost_dict['HO']['moderate']['AQoff_SMR']['0'], \
    prod_max=bigM, carbon_credit=True, trl='repurposed', block='CCUS', label='Offshore aquifer CO2 sequestration (SMR)')
# AQoff_DAC = Process(name='AQoff_DAC', intro_scale=20, prod_max=bigM, carbon_credit=True,
# trl='repurposed', block='CCUS', label='Offshore aquifer CO2 sequestration (DAC)')
# Grid = Process(name='Grid', intro_scale=20, prod_max=bigM, gwp=0.343,
#    trl='utility', block='power_generation', label='Grid electricity')
H2_Blue = Process(name='H2_Blue', conversion={H2: 1, H2_B: -1}, prod_max=bigM, gwp=0, cost = cost_dict['HO']['moderate']['H2_Blue']['0'],
                          trl='nocost', block='dummy', label='Blue Hydrogen production')
H2_Green = Process(name='H2_Green', conversion={H2: 1, H2_G: -1}, prod_max=bigM, cost = cost_dict['HO']['moderate']['H2_Green']['0'],
                           trl='nocost', block='dummy', label='Green Hydrogen production')



# *-------------------------Geographic scales/location------------------------------------
HO = Location(name='HO', processes= {H2_L_c, H2_L_d, PV, LiI_c, LiI_d, WF, AKE, SMRH}, demand = {H2_L: 100, H2_C: 100}, scales = scales, PV_class='Class5', WF_class='Class4',
                      LiI_class='8Hr Battery Storage', PSH_class='Class 3', label='Houston')

# *-------------------------Input data graphs------------------------------------
graph.capacity_factor(location= HO, process= PV, color= 'orange')
graph.cost_factor (location= HO, resource= CH4) 

# *-------------------------Generate scenario------------------------------------

case = Scenario(name= '', network = HO, scales= scales,  expenditure_scale_level= 1, scheduling_scale_level= 2, network_scale_level= 0, demand_scale_level= 1, label= 'shell milp case study')

#%%
# *-------------------------Model formulation------------------------------------
milp = formulate_milp(scenario= case)
results = solve(scenario = case, instance=milp, solver= 'gurobi', name='onelocmilp', saveformat = '.pkl', tee = True)

#%%

def reduce_scenario(varying_process_df: pandas.DataFrame, varying_cost_df: pandas.DataFrame, red_scn_method: str, rep_days_no: int) -> dict:
    """Reduces scenario to set of representative days
    days closest to the cluster centroids are chosen
    red_scn_methods available: Agglomorative Hierarchial Clustering (AHC)
    output dictionary contains representative days and their corresponding cluster weights

    Args:
        varying_process_df (pandas.DataFrame): contains varying process paramters (e.g.: conversion factors)
        varying_resource_df (pandas.DataFrame): contains varying resource paramters (e.g.: cost)
        red_scn_method (str): specify the type of clustering to use (e.g.: 'AHC')
        rep_days_no (int): number of representative days

    Returns:
        dict: contains set of representative days and corresponding cluster weights
    """
    if rep_days_no == 365:
        rep_day_dict = {day: {i: {} for i in ['rep_day', 'cluster_wt']} for day in list(
            varying_process_df['day'].unique())}

        for day in list(varying_process_df['day'].unique()):
            rep_day_dict[day]['rep_day'] = day
            rep_day_dict[day]['cluster_wt'] = 1

    else:
        varying_process_df = varying_process_df.drop(columns=['hour', 'day'])
        varying_resource_df = varying_resource_df.drop(columns=['hour', 'day'])

        # get list of varying processes
        varying_process = [col for col in varying_process_df]
        # get list of varying resources
        varying_resource = [col for col in varying_resource_df]

        scaled_df = pandas.DataFrame()

        # standardize the values for all process and resources
        for var in varying_process:
            scaled_iter = scaler(varying_process_df, var)
            scaled_df = pandas.concat([scaled_df, scaled_iter], axis=1)

        for var in varying_resource:
            scaled_iter = scaler(varying_resource_df, var)
            scaled_df = pandas.concat([scaled_df, scaled_iter], axis=1)

        scaled_array = scaled_df.to_numpy()  # for input into clustering models

        if red_scn_method == 'AHC':

            connectivity_matrix = generate_connectivity_matrix()  # generate connectivity matric

            # ahc = AgglomerativeClustering(n_clusters=rep_days_no, affinity='euclidean', connectivity=connectivity_matrix,
            #                               linkage='ward')  # train ahc on input data
            
            
            ahc = AgglomerativeClustering(affinity='euclidean', connectivity=connectivity_matrix,
                                          linkage='ward', compute_full_tree = True) 
            
            clustered_array = ahc.fit_predict(
                scaled_array)  # cluster as per trained model

            cluster_labels = ahc.labels_  # get list of representative days

            nearest_centroid_array = NearestCentroid().fit(
                scaled_array, clustered_array).centroids_  # get the centroids of the clusters
            nearest_centroid_df = pandas.DataFrame(data=nearest_centroid_array, columns=[
                                               col for col in scaled_df])

            # add cluster numbers to the dataset
            scaled_df['cluster_no'] = cluster_labels
            # add cluster numbers to the dataset
            nearest_centroid_df['cluster_no'] = scaled_df['cluster_no'].unique()
            euclidean_distance_list = []
            # closest actual days to the cluster centroids
            closest_to_centroid_df = pandas.DataFrame(
                columns=['day', 'rep_day', 'cluster_wt'])

            for cluster_no in nearest_centroid_df['cluster_no']:
                # -1 skips cluster_no row
                cluster_array = scaled_df[scaled_df['cluster_no']
                                          == cluster_no].iloc[:, :-1].to_numpy()
                centroid_array = nearest_centroid_df[nearest_centroid_df['cluster_no']
                                                     == cluster_no].iloc[:, :-1].to_numpy()
                centroid = centroid_array.tolist()[0]
                for cluster in cluster_array:
                    cluster_point = [cluster for cluster in cluster]
                    euclidean_distance = find_euclidean_distance(
                        cluster_point, centroid)
                    euclidean_distance_list.append(euclidean_distance)

            scaled_df['ED'] = euclidean_distance_list
            closest_to_centroid_df['day'] = (
                scaled_df['cluster_no'].value_counts().index.values)
            cluster_wts = [i for i in scaled_df['cluster_no'].value_counts()]
            closest_to_centroid_df['cluster_wt'] = cluster_wts

            list_ = []
            for i in closest_to_centroid_df['day']:
                list_.append(
                    scaled_df.index.values[scaled_df['ED'] == scaled_df['ED'][scaled_df['cluster_no'] == i].min()][0])
            closest_to_centroid_df['rep_day'] = list_
            closest_to_centroid_df = closest_to_centroid_df.sort_values(
                by=['rep_day']).reset_index(drop=True)
            closest_to_centroid_df['day'] = list(
                range(len(closest_to_centroid_df['day'])))
            rep_day_dict = {int(day) + 1: {i: {} for i in ['rep_day', 'cluster_wt']}
                            for day in list(closest_to_centroid_df['day'])}
            for day in closest_to_centroid_df['day']:
                rep_day_dict[day + 1]['rep_day'] = closest_to_centroid_df['rep_day'][closest_to_centroid_df['day'] == day].values[0]
                rep_day_dict[day + 1]['cluster_wt'] = closest_to_centroid_df['cluster_wt'][closest_to_centroid_df['day'] == day].values[0]

    return rep_day_dict


def ahc_elbow(varying_process_df: pandas.DataFrame, varying_resource_df: pandas.DataFrame, red_scn_method: str, rep_days_no: int) -> dict:
    """Reduces scenario to set of representative days
    days closest to the cluster centroids are chosen
    red_scn_methods available: Agglomorative Hierarchial Clustering (AHC)
    output dictionary contains representative days and their corresponding cluster weights

    Args:
        varying_process_df (pandas.DataFrame): contains varying process paramters (e.g.: conversion factors)
        varying_resource_df (pandas.DataFrame): contains varying resource paramters (e.g.: cost)
        red_scn_method (str): specify the type of clustering to use (e.g.: 'AHC')
        rep_days_no (int): number of representative days

    Returns:
        dict: contains set of representative days and corresponding cluster weights
    """
    if rep_days_no == 365:
        rep_day_dict = {day: {i: {} for i in ['rep_day', 'cluster_wt']} for day in list(
            varying_process_df['day'].unique())}

        for day in list(varying_process_df['day'].unique()):
            rep_day_dict[day]['rep_day'] = day
            rep_day_dict[day]['cluster_wt'] = 1

    else:
        varying_process_df = varying_process_df.drop(columns=['hour', 'day'])
        varying_resource_df = varying_resource_df.drop(columns=['hour', 'day'])

        # get list of varying processes
        varying_process = [col for col in varying_process_df]
        # get list of varying resources
        varying_resource = [col for col in varying_resource_df]

        scaled_df = pandas.DataFrame()

        # standardize the values for all process and resources
        for var in varying_process:
            scaled_iter = scaler(varying_process_df, var)
            scaled_df = pandas.concat([scaled_df, scaled_iter], axis=1)

        for var in varying_resource:
            scaled_iter = scaler(varying_resource_df, var)
            scaled_df = pandas.concat([scaled_df, scaled_iter], axis=1)

        scaled_array = scaled_df.to_numpy()  # for input into clustering models

        if red_scn_method == 'AHC':

            connectivity_matrix = generate_connectivity_matrix()  # generate connectivity matric

            ahc = AgglomerativeClustering(n_clusters=rep_days_no, affinity='euclidean', connectivity=connectivity_matrix,
                                          linkage='ward')  # train ahc on input data
            
            
            # ahc = AgglomerativeClustering(n_clusters = None, distance_threshold = 30, affinity='euclidean', connectivity=connectivity_matrix,
            #                               linkage='ward', compute_full_tree = True) 
            
            clustered_array = ahc.fit_predict(
                scaled_array)  # cluster as per trained model

            cluster_labels = ahc.labels_  # get list of representative days

            nearest_centroid_array = NearestCentroid().fit(
                scaled_array, clustered_array).centroids_  # get the centroids of the clusters
            nearest_centroid_df = pandas.DataFrame(data=nearest_centroid_array, columns=[
                                               col for col in scaled_df])

            # add cluster numbers to the dataset
            scaled_df['cluster_no'] = cluster_labels
            # add cluster numbers to the dataset
            nearest_centroid_df['cluster_no'] = scaled_df['cluster_no'].unique()
            euclidean_distance_list = []
            # closest actual days to the cluster centroids
            closest_to_centroid_df = pandas.DataFrame(
                columns=['day', 'rep_day', 'cluster_wt'])

            for cluster_no in nearest_centroid_df['cluster_no']:
                # -1 skips cluster_no row
                cluster_array = scaled_df[scaled_df['cluster_no']
                                          == cluster_no].iloc[:, :-1].to_numpy()
                centroid_array = nearest_centroid_df[nearest_centroid_df['cluster_no']
                                                     == cluster_no].iloc[:, :-1].to_numpy()
                centroid = centroid_array.tolist()[0]
                for cluster in cluster_array:
                    cluster_point = [cluster for cluster in cluster]
                    euclidean_distance = find_euclidean_distance(
                        cluster_point, centroid)
                    euclidean_distance_list.append(euclidean_distance)

            scaled_df['ED'] = euclidean_distance_list
            closest_to_centroid_df['day'] = (
                scaled_df['cluster_no'].value_counts().index.values)
            cluster_wts = [i for i in scaled_df['cluster_no'].value_counts()]
            closest_to_centroid_df['cluster_wt'] = cluster_wts
            wccs_sum = sum(i for i in scaled_df['ED'])/rep_days_no
            list_ = []
            for i in closest_to_centroid_df['day']:
                list_.append(
                    scaled_df.index.values[scaled_df['ED'] == scaled_df['ED'][scaled_df['cluster_no'] == i].min()][0])
            closest_to_centroid_df['rep_day'] = list_
            closest_to_centroid_df = closest_to_centroid_df.sort_values(
                by=['rep_day']).reset_index(drop=True)
            closest_to_centroid_df['day'] = list(
                range(len(closest_to_centroid_df['day'])))
            rep_day_dict = {int(day) + 1: {i : {} for i in ['rep_day', 'cluster_wt']}
                            for day in list(closest_to_centroid_df['day'])}
            for day in closest_to_centroid_df['day']:
                rep_day_dict[day + 1]['rep_day'] = closest_to_centroid_df['rep_day'][closest_to_centroid_df['day'] == day].values[0] + 1
                rep_day_dict[day + 1]['cluster_wt'] = closest_to_centroid_df['cluster_wt'][closest_to_centroid_df['day'] == day].values[0]

    return rep_day_dict, wccs_sum



def dtw_cluster(series1:list, series2:list):
    """clusters time series data with disparate temporal resolution 
    using dynamic time warping (dtw)

    Args:
        series1 (list): time series 1
        series2 (list): time series 2

    Returns:
        matrix: cost matrix for dtw
    """       
    matrix = numpy.zeros((len(series1) + 1, len(series2) + 1))
    for i,j in product(range(1, len(series1)+1), range(1, len(series2) + 1)):
        matrix[i, j] = numpy.inf
    matrix[0,0] = 0
    for i,j in product(range(1, len(series1)+1), range(1, len(series2) + 1)):
        cost = abs(series1[i-1] - series2[j-1]) 
        prev = numpy.min([matrix[i-1, j], matrix[i, j-1], matrix[i-1, j-1]]) 
        matrix[i,j] = cost + prev
    return matrix


def find_dtw_path(matrix:numpy.ndarray)-> list:
    """finds optimal warping path from a dynamic time warping cost matrix 

    Args:
        matrix (numpy.ndarray): cost matrix from application of dtw

    Returns:
        list: optimal path with list of coordinates
    """
    path  = []
    i,j = len(matrix) -1, len(matrix[0]) -1
    path.append([i,j])
    while i > 0 and j > 0:
        index_min = numpy.argmin([matrix[i-1, j], matrix[i, j-1], matrix[i-1, j-1]])
        if index_min == 0:
            i = i - 1
        if index_min == 1:
            j = j - 1
        if index_min == 2:
            i = i - 1
            j = j - 1
        path.append([i,j])
    # path.append([0,0])
    return path

#%%




# %%
