
#%%

"""
Carbon cycle case study
Specifics - 
Start with a conventional system 
Introduce renewable power technologies
 
"""
# flexibility test: given a fixed range for the uncertain parameter Fh,  where is the critical point?

# case study source: https://doi.org/10.1016/0098-1354(87)87011-4 (Grossmann and Floudas 1987)

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

# *-------------------------Import modules------------------------------------
import pandas
from src.energiapy.components.temporal_scale import Temporal_scale
from src.energiapy.components.resource import Resource
from src.energiapy.components.process import Process
from src.energiapy.components.location import Location
from src.energiapy.components.network import Network
from src.energiapy.components.scenario import Scenario
from src.energiapy.components.transport import Transport
from src.energiapy.graph import graph
from src.energiapy.model.formulate_mpmilp import formulate_mpmilp
from src.energiapy.model.formulate_mplp import formulate_mplp
from src.energiapy.model.pyomo_solve import solve
from src.energiapy.utils.data_utils import get_data, load_results

results_milp = load_results(filename = 'red_onelocmilp.pkl')

# *-------------------------Temporal scales------------------------------------
#Defined as a single temporal scale with 42 discretization, base scale becomes 0
scales = Temporal_scale(discretization_list= [1, 1])

# *-------------------------Constants defined here for ease------------------------------------
bigM = 100 #very large number
water_price = 31.70  # $/5000gallons
power_price = 8  # cents/kWh
ur_price = 42.70  # 250 Pfund U308 (Uranium)
A_f = 0.05  # annualization factor
smallM = 0.1

# *-------------------------Resources------------------------------------
Charge = Resource(name='Charge', sell=False,
                          store_max=100, basis='MW', label='Battery energy', block= 'energystorage')
Air_C = Resource(name='Air_C', store_max=bigM, basis='MW',
                         label='CAES energy', block= 'energystorage')
H2O_E = Resource(name='H2O_E', store_max=bigM, basis='MW',
                         label='PSH energy', block= 'energystorage')
Solar = Resource(
    name='Solar', cons_max=10**4, basis='MW', label='Solar Power', block = 'energyfeedstock')
Wind = Resource(name='Wind', cons_max=10 **
                        4, basis='MW', label='Wind Power', block = 'energyfeedstock')
Uranium = Resource(name='Uranium', cons_max=10 **
                           4, price=ur_price/(250/2), basis='kg', label='Uranium', block = 'energyfeedstock')
H2_C = Resource(name='H2_C', sell=True, store_max=10**4, loss=0.025/24, revenue=2, mile=1/(0.1180535*1.60934),
                        demand=True, basis='kg', label='Hydrogen - Local Cryo', block= 'resourcestorage') 
H2_L = Resource(name='H2_L', sell=True, store_max=10**10, demand=True, revenue=2,
                        mile=1/(0.1180535*1.60934), basis='kg', label='Hydrogen - Geological', block= 'resourcestorage')
H2 = Resource(name='H2', basis='kg', label='Hydrogen', block= 'Resource')
H2_B = Resource(name='H2_B', basis='kg', label='Blue hydrogen', block= 'product')
H2_G = Resource(name='H2_G', basis='kg', label='Green hydrogen', block= 'product')
H2O = Resource(name='H2O', cons_max=10**4,
                       price=water_price/(5000*3.7854), basis='kg', label='Water', block= 'Resource')
O2 = Resource(name='O2', sell=True, loss=0.07,
                      basis='kg', label='Oxygen', block = 'Resource')
CH4 = Resource(name='CH4', cons_max=10 **
                       20, price=1, basis='kg', label='Natural gas', block = 'materialfeedstock', varying = False)
CO2 = Resource(name='CO2', basis='kg', label='Carbon dioxide', block = 'Resource')
CO2_DAC = Resource(
    name='CO2_DAC', basis='kg', label='Carbon dioxide - captured', block = 'carbonsequestration')
CO2_AQoff = Resource(
    name='CO2_AQoff', store_max=10**10, basis='kg', label='Carbon dioxide - sequestered', block = 'carbonsequestration')
CO2_EOR = Resource(
    name='CO2_EOR', store_max=10**10, basis='kg', label='Carbon dioxide - EOR', block = 'carbonsequestration')
CO2_Mat = Resource(
    name='CO2_Mat', store_max=10**10, basis='kg', label='Carbon dioxide - EOR', block = 'carbonsequestration')
CH3OH = Resource(name='CH3OH', sell=True, revenue=0.5,
                         mile=1/(0.0195508*1.60934), basis='kg', label='Methanol', block = 'resourcedischarge')
CO2_Vent = Resource(
    name='CO2_Vent', sell=True, basis='kg', label='Carbon dioxide - Vented', block = 'resourcedischarge')
# Power= Resource(name= 'Power', sell= True, store_max=0,   \
#    mile= (10**3)/(0.2167432**1.60934), label= 'Renewable power generated')
Power = Resource(name='Power', basis='MW',
                         label='Renewable power generated', block = 'Resource')





#cost of processes
cost_dict = get_data(file_name='cost_dict')

LiI_c = Process(name='LiI_c', conversion={Charge: 1, Power: -1}, cost = cost_dict['HO']['moderate']['LiI_c']['0'],\
    prod_max=bigM, trl='nrel', block='power_storage', label='Lithium-ion battery', citation='Zakeri 2015')
LiI_d = Process(name='LiI_d', conversion={Charge: -1.1765, Power: 1}, cost = cost_dict['HO']['moderate']['LiI_d']['0'], \
    prod_max=bigM, trl='discharge', block='power_storage', label='Lithium-ion battery discharge', citation='Zakeri 2015')
CAES_c = Process(name='CAES_c', conversion={Air_C: 1, Power: -1}, cost = cost_dict['HO']['moderate']['CAES_c']['0'], \
    intro_scale=0, prod_max=bigM, trl='pilot', block='power_storage', label='Compressed air energy storage (CAES)', citation='Zakeri 2015')
CAES_d = Process(name='CAES_d', conversion={Air_C: -1.4286, Power: 1}, cost = cost_dict['HO']['moderate']['CAES_d']['0'],\
    intro_scale=0, prod_max=bigM, trl='discharge', block='power_storage', label='Compressed air energy storage (CAES) discharge', citation='Zakeri 2015')
PSH_c = Process(name='PSH_c', conversion={H2O_E: 1, Power: -1}, cost = cost_dict['HO']['moderate']['PSH_c']['0'], \
    intro_scale=0, prod_max=bigM, trl='nrel', block='power_storage', label='Pumped storage hydropower (PSH)', citation='Zakeri 2015')
PSH_d = Process(name='PSH_d', conversion={H2O: -1, Power: -1.4286}, cost = cost_dict['HO']['moderate']['PSH_d']['0'], \
    prod_max=bigM, trl='discharge', block='power_storage', label='Pumped storage hydropower (PSH) discharge', citation='Zakeri 2015')
PV = Process(name='PV', intro_scale=0, conversion={Solar: -1, Power: 1, H2O: -20}, cost = cost_dict['HO']['moderate']['PV']['0'], \
    prod_max=bigM, gwp=53000, land=13320/1800, trl='nrel', block='power_generation', label='Solar photovoltaics (PV) array', citation='Use pvlib conversion', varying= True)
WF = Process(name='WF', conversion={Wind: -1, Power: 1, H2O: -1}, cost = cost_dict['HO']['moderate']['WF']['0'], \
    prod_max=bigM, gwp=52700, land=10800/1800, trl='nrel', block='power_generation', \
        label='Wind mill array', citation='Use windtoolkit conversion', varying = True)
AKE = Process(name='AKE', intro_scale=0, conversion={Power: -1, H2_G: 19.474, O2: 763.2, H2O: -175.266}, \
    cost = cost_dict['HO']['moderate']['AKE']['0'], prod_max=bigM, trl='utility', block='material_production', \
        label='Alkaline water electrolysis (AWE)', citation='Demirhan et al. 2018 AIChE paper')  # 20.833 MW required to produce 1000t/day.H2
SMRH = Process(name='SMRH', intro_scale=0, conversion={Power: -1.11*10**(-3), CH4: -3.76, H2O: -23.7, H2_B: 1, CO2_Vent: 1.03, CO2: 9.332}, \
    cost = cost_dict['HO']['moderate']['SMRH']['0'], prod_max=bigM, gwp=0, trl='enterprise', block='material_production', \
        label='Steam methane reforming + CCUS', citation='Mosca 2020, 90pc capture')
# SMR = Process(name='SMR', intro_scale=smr_start, cost = cost_dict['HO']['moderate']['SMR']['0'], conversion={Power: -1.11*10**(-3), CH4: -3.76, H2O: -23.7, H2_B: 1, CO2_Vent: 9.4979}, prod_max=bigM, gwp=0, trl='enterprise',
#                       block='material_production', label='Steam methane reforming', citation='Mosca 2020')
ASMR = Process(name='ASMR', conversion={Uranium: -4.17*10**(-5), H2O: -3364.1, Power: 1}, cost = cost_dict['HO']['moderate']['ASMR']['0'], \
    intro_scale=0, gwp=9100, prod_max=bigM, land=1100/1800, trl='pilot', block='power_generation', label='Small modular reactors (SMRs)')
H2_C_c = Process(name='H2_C_c', conversion={Power: -1.10*10**(-3), H2_C: 1, H2: -1}, cost = {'CAPEX': smallM, 'Fixed O&M': 0, 'Variable O&M': 0, \
    'units': '$/kg','source': 'dummy'}, \
    prod_max=12000, gwp=0, trl='pilot', block='material_storage', label='Hydrogen local storage (Compressed)', \
        citation='Bossel and Eliasson - Energy and the Hydrogen Economy')
H2_C_d = Process(name='H2_C_d',  conversion={H2_C: -1, H2: 1}, cost = {'CAPEX': smallM, 'Fixed O&M': 0, 'Variable O&M': 0, \
    'units': '$/kg','source': 'dummy'}, \
        prod_max=bigM, gwp=0, trl='nocost',
                         block='material_storage', label='Hydrogen local storage (Compressed) discharge', citation='Bossel and Eliasson - Energy and the Hydrogen Economy')
H2_L_c = Process(name='H2_L_c', conversion={Power: -4.17*10**(-4), H2_L: 1, H2: -1}, cost = {'CAPEX': smallM, 'Fixed O&M': 0, 'Variable O&M': 0, \
    'units': '$/kg','source': 'dummy'}, \
         prod_max=bigM, gwp=0, trl='repurposed', block='material_storage', label='Hydrogen geological storage', \
            citation='Bossel and Eliasson - Energy and the Hydrogen Economy')
H2_L_d = Process(name='H2_L_d', conversion={H2_L: -1, H2: 1}, prod_max=bigM, gwp=0, trl='nocost', cost = {'CAPEX': smallM, 'Fixed O&M': 0, 'Variable O&M': 0, \
    'units': '$/kg','source': 'dummy'}, \
        block='material_storage', label='Hydrogen geological storage discharge', citation='Bossel and Eliasson - Energy and the Hydrogen Economy')
# SMRM = Process(name='SMRM', intro_scale=20, prod_max=bigM, gwp=0,
#                        trl='enterprise', block='material_production', label='Methanol SMR')
# MEFC = Process(name='MEFC', conversion={Power: -4.84*10**(-1), H2_G: -0.4048, CO2_DAC: -1.2143, CH3OH: 1}, intro_scale=6, prod_max=bigM, carbon_credit=True, trl='pilot',
#                        block='material_production', label='Catalytic methanol production', citation='Keith et al (2018), Fasihi et al (2019)')  # 10,000t/y
DAC = Process(name='DAC', conversion={Power: -1.93*10**(-4), H2O: -4.048, CO2_DAC: 1}, cost = cost_dict['HO']['moderate']['DAC']['0'], \
    intro_scale=0, prod_max=bigM, gwp=0, trl='pilot', block='CCUS', label='Direct air capture', citation='D. Belloti et al (2017)')
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
H2_Blue = Process(name='H2_Blue', conversion={H2: 1, H2_B: -1}, prod_max=bigM, gwp=0, cost = {'CAPEX': smallM, 'Fixed O&M': 0, 'Variable O&M': 0, \
    'units': '$/kg','source': 'dummy'}, trl='nocost', block='dummy', label='Blue Hydrogen production')
H2_Green = Process(name='H2_Green', conversion={H2: 1, H2_G: -1}, prod_max=bigM, cost = {'CAPEX': smallM, 'Fixed O&M': 0, 'Variable O&M': 0, \
    'units': '$/kg','source': 'dummy'}, trl='nocost', block='dummy', label='Green Hydrogen production')

tx_processes = {LiI_c, LiI_d, CAES_c, CAES_d, PSH_c, PSH_d, PV, WF, AKE, SMRH, H2_C_c,
                H2_C_d, H2_L_c, H2_L_d, DAC, EOR, AQoff_SMR, H2_Blue, H2_Green}#, ASMR}
# {H2_L_c, H2_L_d, PV, LiI_c, LiI_d, WF, AKE, SMRH}

# *-------------------------Geographic scales/location------------------------------------
demand = {(i,): 100.0*(i+1) for i in range(scales.discretization_list[0])}
# demand = 1000
# demand = {H2_C:50.0, H2_L:50.0}

#candidate cities (sources)
#can only produce and transport green hydrogen that passes through liquefaction/storage is optional
TX = Location(name= 'TX', processes= tx_processes, scales = scales, demand= demand, label= 'Texas')

# *-------------------------Scenario------------------------------------
#given that this is a single temporal scale model, all scales could be allowed to default to 0. Scales stated here due to clarity
case = Scenario(name= 'carboncycle', network= TX, scales= scales, \
    expenditure_scale_level= 1, scheduling_scale_level= 1, network_scale_level= 0,  demand_scale_level=0,  label= 'carbon cycle milp')
# *-------------------------Model formulation------------------------------------
#this creates a pyomo instance, prior to this step the model is only defined in energiapy
# mpmilp = formulate_mpmilp(scenario= case, penalty= 1.5)
# results_mpmilp = solve(scenario = case, instance=mpmilp, solver= 'gurobi', name='trial', saveformat= '.pkl', print_solversteps= True)

mplp= formulate_mplp(scenario= case, penalty= 1.5)
results_mplp = solve(scenario = case, instance=mplp, solver= 'gurobi', name='txmplp', saveformat= '.pkl', print_solversteps= True)
#%%
 
graph.capacity_utilization(results = results_mplp, location = 'TX')
# graph.capacity_utilization(results = results_mplp, location = 'A', process= 'PV')
graph.capacity_utilization(results = results_mplp, location = 'TX', process= 'SMRH')



#%% plots results at requested scales, usetex giving a very unique error only for this plot!! 
#TODO - add the type of graph generated in the title
location = 'B'


for i in results.fetch_components(component_type= 'resources', condition = ('cons_max', 'g', 0)):
    graph.schedule(results = results, y_axis = 'C', component= i, location= location, usetex = False)


#%%expenditure on consumable resources
for i in results.fetch_components(component_type= 'resources', condition = ('cons_max', 'g', 0)):
    graph.schedule(results = results, y_axis = 'B', component= i, location= location, usetex = False)    


#%%inventory levels of storable processes
for i in results.fetch_components(component_type= 'resources', condition = ('store_max','g', 0)):
    graph.schedule(results = results, y_axis = 'Inv', component= i, location= location, usetex = False)    


#%%Production on per basis level for processes with varying capacities

for i in results.fetch_components(component_type= 'processes', condition = ('varying', True)):
    graph.schedule(results = results, y_axis = 'P', component= i, location= location, usetex = False)
   

#%%Delta Cap of process with varying capacities 

for i in results.fetch_components(component_type= 'processes', condition = ('varying', True)):
    graph.schedule(results = results, y_axis = 'Delta_Cap_P', component= i, location= location, usetex = False)    
