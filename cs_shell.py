
#%%
"""Example case study implemeted on the energia python module
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
__version__ = "1.0.3"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"


# *-------------------------Import modules------------------------------------
from turtle import distance
import pandas
# import numpy 
# from pyomo.opt import SolverStatus, TerminationCondition
from pyomo.environ import ConcreteModel #, Var, NonNegativeReals, Set
from src.energiapy.components.temporal_scale import temporal_scale
from src.energiapy.components.resource import resource
from src.energiapy.components.process import process
from src.energiapy.components.material import material
from src.energiapy.components.location import location
from src.energiapy.components.network import network
from src.energiapy.components.scenario import scenario
from src.energiapy.components.transport import transport
from src.energiapy.utils.data_utils import get_data,make_henry_price_df
from src.energiapy.graph import graph


 
# *-------------------------Temporal scales------------------------------------

scales = temporal_scale(discretization_list = [1, 365, 24])
# scales = temporal_scale(discretization_list = [1, 2, 3])


# *-------------------------Constants defined here for ease------------------------------------
bigM = 10**10 #very large number
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

# *-------------------------Resources------------------------------------

Charge = resource(name='Charge', sell=False,
                          store_max=bigM, basis='MW', label='Battery energy', block= 'energystorage')
Air_C = resource(name='Air_C', store_max=bigM, basis='MW',
                         label='CAES energy', block= 'energystorage')
H2O_E = resource(name='H2O_E', store_max=bigM, basis='MW',
                         label='PSH energy', block= 'energystorage')
Solar = resource(
    name='Solar', consumption_max=10**20, basis='MW', label='Solar Power', block = 'energyfeedstock')
Wind = resource(name='Wind', consumption_max=10 **
                        20, basis='MW', label='Wind Power', block = 'energyfeedstock')
Uranium = resource(name='Uranium', consumption_max=10 **
                           20, price=ur_price/(250/2), basis='kg', label='Uranium', block = 'energyfeedstock')
H2_C = resource(name='H2_C', sell=True, store_max=10**4, loss=0.025/24, revenue=2, mile=1/(0.1180535*1.60934),
                        demand=True, basis='kg', label='Hydrogen - Local Cryo', block= 'resourcestorage') 
H2_L = resource(name='H2_L', sell=True, store_max=10**10, demand=True, revenue=2,
                        mile=1/(0.1180535*1.60934), basis='kg', label='Hydrogen - Geological', block= 'resourcestorage')
H2 = resource(name='H2', basis='kg', label='Hydrogen', block= 'resource')
H2_B = resource(name='H2_B', basis='kg', label='Blue hydrogen', block= 'product')
H2_G = resource(name='H2_G', basis='kg', label='Green hydrogen', block= 'product')
H2O = resource(name='H2O', consumption_max=10**20,
                       price=water_price/(5000*3.7854), basis='kg', label='Water', block= 'resource')
O2 = resource(name='O2', sell=True, loss=0.07,
                      basis='kg', label='Oxygen', block = 'resource')
CH4 = resource(name='CH4', consumption_max=10 **
                       20, varying= True, price=1, basis='kg', label='Natural gas', block = 'materialfeedstock')
CO2 = resource(name='CO2', basis='kg', label='Carbon dioxide', block = 'resource')
CO2_DAC = resource(
    name='CO2_DAC', basis='kg', label='Carbon dioxide - captured', block = 'carbonsequestration')
CO2_AQoff = resource(
    name='CO2_AQoff', store_max=10**10, basis='kg', label='Carbon dioxide - sequestered', block = 'carbonsequestration')
CO2_EOR = resource(
    name='CO2_EOR', store_max=10**10, basis='kg', label='Carbon dioxide - EOR', block = 'carbonsequestration')
CH3OH = resource(name='CH3OH', sell=True, revenue=0.5,
                         mile=1/(0.0195508*1.60934), basis='kg', label='Methanol', block = 'resourcedischarge')
Power_Gr = resource(name='Power_Gr', consumption_max=10 **
                            20, price=power_price*(10), basis='kg', label='Grid electricity', block = 'energyfeedstock')
CO2_Vent = resource(
    name='CO2_Vent', sell=True, basis='kg', label='Carbon dioxide - Vented', block = 'resourcedischarge')
# Power= resource(name= 'Power', sell= True, store_max=0,   \
#    mile= (10**3)/(0.2167432**1.60934), label= 'Renewable power generated')
Power = resource(name='Power', basis='MW',
                         label='Renewable power generated', block = 'resource')


# *-------------------------Materials------------------------------------
Li = material(name='Li', gwp=0, basis= 'kg', label='Lithium')


# *-------------------------Processes ------------------------------------

LiI_c = process(name='LiI_c', conversion={Charge: 1, Power: -1}, material_cons = {Li: 20}, prod_max=bigM, trl='nrel',
                        block='power_storage', label='Lithium-ion battery', source='Zakeri 2015')
LiI_d = process(name='LiI_d', conversion={Charge: -1.1765, Power: 1}, prod_max=bigM, trl='discharge',
                        block='power_storage', label='Lithium-ion battery discharge', source='Zakeri 2015')
CAES_c = process(name='CAES_c', conversion={Air_C: 1, Power: -1}, intro_scale=2, prod_max=bigM, trl='pilot',
                         block='power_storage', label='Compressed air energy storage (CAES)', source='Zakeri 2015')
CAES_d = process(name='CAES_d', conversion={Air_C: -1.4286, Power: 1}, intro_scale=2, prod_max=bigM, trl='discharge',
                         block='power_storage', label='Compressed air energy storage (CAES) discharge', source='Zakeri 2015')
PSH_c = process(name='PSH_c', conversion={H2O_E: 1, Power: -1}, intro_scale=0, prod_max=bigM, trl='nrel',
                        block='power_storage', label='Pumped storage hydropower (PSH)', source='Zakeri 2015')
PSH_d = process(name='PSH_d', conversion={H2O: -1, Power: -1.4286}, prod_max=bigM, trl='discharge',
                        block='power_storage', label='Pumped storage hydropower (PSH) discharge', source='Zakeri 2015')
PV = process(name='PV', intro_scale=pv_start, conversion={Solar: -1, Power: 1, H2O: -20}, varying= True, prod_max=bigM, gwp=53000, land=13320/1800,
                     trl='nrel', block='power_generation', label='Solar photovoltaics (PV) array', source='Use pvlib conversion')
WF = process(name='WF', conversion={Wind: -1, Power: 1, H2O: -1}, varying= True, prod_max=bigM, gwp=52700, land=10800 /
                     1800, trl='nrel', block='power_generation', label='Wind mill array', source='Use windtoolkit conversion')
AKE = process(name='AKE', intro_scale=ake_start, conversion={Power: -1, H2_G: 19.474, O2: 763.2, H2O: -175.266}, prod_max=bigM, trl='utility', block='material_production',
                      label='Alkaline water electrolysis (AWE)', source='Demirhan et al. 2018 AIChE paper')  # 20.833 MW required to produce 1000t/day.H2
SMRH = process(name='SMRH', intro_scale=smrh_start, conversion={Power: -1.11*10**(-3), CH4: -3.76, H2O: -23.7, H2_B: 1, CO2_Vent: 1.03, CO2: 9.332}, prod_max=bigM, gwp=0, trl='enterprise',
                       block='material_production', label='Steam methane reforming + CCUS', source='Mosca 2020, 90pc capture')
SMR = process(name='SMR', intro_scale=smr_start, conversion={Power: -1.11*10**(-3), CH4: -3.76, H2O: -23.7, H2_B: 1, CO2_Vent: 9.4979}, prod_max=bigM, gwp=0, trl='enterprise',
                      block='material_production', label='Steam methane reforming', source='Mosca 2020')
ASMR = process(name='ASMR', conversion={Uranium: -4.17*10**(-5), H2O: -3364.1, Power: 1}, intro_scale=asmr_start, gwp=9100, prod_max=bigM, land=1100/1800,
                       trl='pilot', block='power_generation', label='Small modular reactors (SMRs)')
H2_C_c = process(name='H2_C_c', conversion={Power: -1.10*10**(-3), H2_C: 1, H2: -1},  prod_max=12000, gwp=0, trl='pilot',
                         block='material_storage', label='Hydrogen local storage (Compressed)', source='Bossel and Eliasson - Energy and the Hydrogen Economy')
H2_C_d = process(name='H2_C_d',  conversion={H2_C: -1, H2: 1}, prod_max=bigM, gwp=0, trl='nocost',
                         block='material_storage', label='Hydrogen local storage (Compressed) discharge', source='Bossel and Eliasson - Energy and the Hydrogen Economy')
H2_L_c = process(name='H2_L_c', conversion={Power: -4.17*10**(-4), H2_L: 1, H2: -1}, prod_max=bigM, gwp=0, trl='repurposed',
                         block='material_storage', label='Hydrogen geological storage', source='Bossel and Eliasson - Energy and the Hydrogen Economy')
H2_L_d = process(name='H2_L_d', conversion={H2_L: -1, H2: 1}, prod_max=bigM, gwp=0, trl='nocost',
                         block='material_storage', label='Hydrogen geological storage discharge', source='Bossel and Eliasson - Energy and the Hydrogen Economy')
# SMRM = process(name='SMRM', intro_scale=20, prod_max=bigM, gwp=0,
#                        trl='enterprise', block='material_production', label='Methanol SMR')
MEFC = process(name='MEFC', conversion={Power: -4.84*10**(-1), H2_G: -0.4048, CO2_DAC: -1.2143, CH3OH: 1}, intro_scale=6, prod_max=bigM, carbon_credit=True, trl='pilot',
                       block='material_production', label='Catalytic methanol production', source='Keith et al (2018), Fasihi et al (2019)')  # 10,000t/y
DAC = process(name='DAC', conversion={Power: -1.93*10**(-4), H2O: -4.048, CO2_DAC: 1}, intro_scale=4, prod_max=bigM, gwp=0,
                      trl='pilot', block='CCUS', label='Direct air capture', source='D. Belloti et al (2017)')
# DOWC = process(name='DOWC', intro_scale=20, prod_max=bigM, gwp=0,
#                        trl='repurposed', block='CCUS', label='Depleted oil wells')
EOR = process(name='EOR', intro_scale=0, conversion={Power: -0.00255, CO2: -1, CO2_EOR: 1, CO2_Vent: 0.67}, prod_max=bigM, carbon_credit=True,
                      trl='enterprise', block='CCUS', label='CO2-Enhanced oil recovery')
AQoff_SMR = process(name='AQoff_SMR', conversion={Power: -0.00128, CO2_AQoff: 1, CO2: -1}, prod_max=bigM, carbon_credit=True,
                            trl='repurposed', block='CCUS', label='Offshore aquifer CO2 sequestration (SMR)')
# AQoff_DAC = process(name='AQoff_DAC', intro_scale=20, prod_max=bigM, carbon_credit=True,
# trl='repurposed', block='CCUS', label='Offshore aquifer CO2 sequestration (DAC)')
# Grid = process(name='Grid', intro_scale=20, prod_max=bigM, gwp=0.343,
#    trl='utility', block='power_generation', label='Grid electricity')
H2_Blue = process(name='H2_Blue', conversion={H2: 1, H2_B: -1}, prod_max=bigM, gwp=0,
                          trl='nocost', block='dummy', label='Blue Hydrogen production')
H2_Green = process(name='H2_Green', conversion={H2: 1, H2_G: -1}, prod_max=bigM,
                           trl='nocost', block='dummy', label='Green Hydrogen production')


cost_metrics_list = ['CAPEX', 'Fixed O&M', 'Variable O&M', 'units', 'source']

cost_dict = get_data(file_name='cost_dict')


# *-------------------------Generate scenario------------------------------------

la_power_output_df = pandas.read_csv('la_power_output_df.csv').drop(columns='datetime')
la_power_output_df['day'] = [i - 1 for i in la_power_output_df['day']]
la_power_output_df['scales'] = [(0,j,k) for j,k in zip(la_power_output_df['day'], la_power_output_df['hour'])]
la_power_output_df = la_power_output_df.drop(columns= ['day', 'hour'])
la_power_output_df['PV'] = la_power_output_df['PV']/max(la_power_output_df['PV'])
la_power_output_df['WF'] = la_power_output_df['WF']/max(la_power_output_df['WF'])




ho_power_output_df = pandas.read_csv('power_output_df.csv').drop(columns='datetime')
ho_power_output_df['day'] = [i - 1 for i in ho_power_output_df['day']]
ho_power_output_df['scales'] = [(0,j,k) for j,k in zip(ho_power_output_df['day'], ho_power_output_df['hour'])]
ho_power_output_df = ho_power_output_df.drop(columns= ['day', 'hour'])
ho_power_output_df['PV'] = ho_power_output_df['PV']/max(ho_power_output_df['PV'])
ho_power_output_df['WF'] = ho_power_output_df['WF']/max(ho_power_output_df['WF'])


#varying natural gas prices
daily_ng_price_df = make_henry_price_df(
    file_name='Henry_Hub_Natural_Gas_Spot_Price_Daily.csv', year=2019, stretch=False)

# *-------------------------Geographic scales/location------------------------------------
HO = location(name='HO', processes= {PV, LiI_c, LiI_d, WF, AKE}, scales = scales, varying_cost_df = daily_ng_price_df, \
    varying_process_df= ho_power_output_df, PV_class='Class5', WF_class='Class4',
                      LiI_class='8Hr Battery Storage', PSH_class='Class 3', label='Houston')
LA = location(name='LA', processes= {PV, LiI_c, LiI_d, WF, SMRH}, scales = scales, varying_cost_df = daily_ng_price_df, \
    varying_process_df= la_power_output_df, PV_class='Class3', WF_class='Class5',
                      LiI_class='8Hr Battery Storage', PSH_class='Class 3', label='LosAngeles')
location_list = [HO, LA]

# *-------------------------Data------------------------------------

cost_metrics_list = ['CAPEX', 'Fixed O&M', 'Variable O&M', 'units', 'source']

graph.capacity_factor(location= HO, process= PV)
graph.cost_factor (location= LA, resource= CH4 )



# *-------------------------Transport modes------------------------------------
Train_H2 = transport(name= 'Train_H2', resources= {H2_B, H2_G}, label= 'Railway for hydrogen transportation', trans_max= 10**8, trans_loss= 0.001, trans_cost= 1.667*10**(-3))
transport_list = [Train_H2]

# *-------------------------Linkage between locations------------------------------------

distance_matrix = [
    [0, 678],
    [678, 0]
                   ]

transport_matrix = [
    [[], [Train_H2]],
    [[Train_H2], []]
                   ]


Network = network(name= 'Network', source_locations= [HO, LA], sink_locations= [HO, LA], distance_matrix= distance_matrix, transport_matrix= transport_matrix) 

m = ConcreteModel()

case = scenario(name= '', network= Network, scales= scales, instance= m, \
    expenditure_scale_level= 1, scheduling_scale_level= 2, network_scale_level= 0, label= 'shell milp case study').formulate_milp()



# %%
