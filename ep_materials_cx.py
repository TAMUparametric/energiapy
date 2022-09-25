
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

__author__ = "Yilun Lin, Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "1.0.3"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"


# *-------------------------Import modules------------------------------------
# from turtle import distance
import pandas
# import numpy 
# from pyomo.opt import SolverStatus, TerminationCondition
from pyomo.environ import SolverFactory #, Var, NonNegativeReals, Set
from energiapy.components.temporal_scale import Temporal_scale
from energiapy.components.resource import Resource
from energiapy.components.process import Process
from energiapy.components.material import Material
from energiapy.components.location import Location
from energiapy.components.network import Network
from energiapy.components.scenario import Scenario
from energiapy.components.transport import Transport
from energiapy.model.formulate_milp import formulate_milp
from energiapy.utils.data_utils import get_data,make_henry_price_df
from energiapy.graph import graph
from energiapy.model.pyomo_solve import solve


# *-------------------------Import data------------------------------------

# import stored files 
ho_solar_df = pandas.read_csv('data/ho_solar.csv', index_col=0)
ho_wind_df = pandas.read_csv('data/ho_wind.csv', index_col=0)

# varying natural gas prices
hp_price_daily_df = make_henry_price_df(
    file_name='data/Henry_Hub_Natural_Gas_Spot_Price_Daily.csv', year=2019, stretch=True)
 
# *-------------------------Temporal scales------------------------------------

scales = Temporal_scale(discretization_list = [1, 365, 24])
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
smallM = 0.01

# *-------------------------Resources------------------------------------

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
                       20, varying_cost_df= hp_price_daily_df, price=1, basis='kg', label='Natural gas', block = 'materialfeedstock')
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
Geothermal_energy= Resource(name='Geotehrmal', store_max=10**10, sell=True, basis='MW',  label='Geothermal Storage', block='resourcestorage')

# *-------------------------Materials------------------------------------
LiR = Material(name='LiR', gwp=1.484, H2O=2273, basis= 'kg', label='Rock-based Lithium', citation= 'Nelson Bunyui Manjong (2021), https://www.tcc.fl.edu/media/divisions/academic-affairs/academic-enrichment/urc/poster-abstracts/Xanders_Madison_Poster_URS.pdf') #gwp=(0.216,0.314)
LiB = Material(name='LiB', gwp=0.031, basis= 'kg', label='Brine-based Lithium', citation= 'Nelson Bunyui Manjong (2021)') #gwp=(0.289,0.499)
Mn = Material(name='Mn', gwp=4.51, basis= 'kg', label='Manganese', citation= 'Nelson Bunyui Manjong (2021)') #inventory data #9.6, 2.6,7.9
Ni = Material(name='Ni', gwp=7.64, H2O=80, basis= 'kg', label='Nickel', citation= 'Mark Mistry (2016), Sustainable water use in minerals and metal production')
Co = Material(name='Co', gwp=11.73, basis= 'kg', label='Cobalt', citation= 'Farjana et al. 2019a, b')
Steel = Material(name='Steel', gwp=(0.8,1.4), H2O=3.94, basis= 'kg', label='Steel', citation= 'Kim R.Bawden (2016), Anlong Li (2020)')
CuP = Material(name='Cu', gwp=2.5, H2O=30, basis= 'kg', label='Copper Pyro', citation= 'T.E. Norgate (2007), Sustainable water use in minerals and metal production')
CuH = Material(name='Cu', gwp=6, H2O=40, basis= 'kg', label='Copper Hyro', citation= 'T.E. Norgate (2007), Sustainable water use in minerals and metal production')
PbB = Material(name='PbB', gwp=1.5, H2O=15, basis= 'kg', label='Lead BF', citation= 'T.E. Norgate (2007), Sustainable water use in minerals and metal production')
PbI = Material(name='PbI', gwp=2.5, H2O=25, basis= 'kg', label='Lead ISF', citation= 'T.E. Norgate (2007), Sustainable water use in minerals and metal production')
ZnE = Material(name='ZnE', gwp=5, H2O=30, basis= 'kg', label='Zn Elec', citation= 'T.E. Norgate (2007), Sustainable water use in minerals and metal production')
ZnI = Material(name='ZnI', gwp=3.5, H2O=25, basis= 'kg', label='Zn ISF', citation= 'T.E. Norgate (2007), Sustainable water use in minerals and metal production')
Pd = Material(name='Pd', gwp=3880, H2O=210713, basis= 'kg', label='Palladium', citation= 'Philip Nuss (2014), Simon Meißner (2021)')
Rd = Material(name='Rd', gwp=35100, basis= 'kg', label='Rhodium', citation= 'Philip Nuss (2014)')
Pt = Material(name='Pd', gwp=12500, H2O=31349, basis= 'kg', label='Platinum', citation= 'Philip Nuss (2014), Simon Meißner (2021)')
Y = Material(name='Y', gwp=15.1, basis= 'kg', label='Yttrium', citation= 'Philip Nuss (2014)')
Al = Material(name='Al', gwp=8.2, H2O=147, basis= 'kg', label='Aluminium', citation= 'Philip Nuss (2014), Water requirements of the aluminum industry Water Supply Paper 1330-C')
Mg = Material(name='Mg', gwp=9.6, basis= 'kg', label='Magnesium', citation= 'Philip Nuss (2014)')
#H20: L/kg

#polymer
PP = Material(name='PP', gwp=1.586, basis= 'kg', label='Polypropylene', citation= 'Greenhouse gas emissions and natural capital implications of plastics (including biobased plastics)')
HDPE = Material(name='HDPE', gwp=1.98, basis= 'kg', label='HD polyethylene', citation= 'Greenhouse gas emissions and natural capital implications of plastics (including biobased plastics)')
LDPE = Material(name='LDPE', gwp=1.93, basis= 'kg', label='LD polyethylene', citation= 'Greenhouse gas emissions and natural capital implications of plastics (including biobased plastics)')
PVC = Material(name='PVC', gwp=2.51, basis= 'kg', label='Polyvinylchloride', citation= 'Greenhouse gas emissions and natural capital implications of plastics (including biobased plastics)')
Rubber = Material(name='Rubber', gwp=6.4, basis= 'kg', label='Rubber', citation= 'GREENING OF INDUSTRY NETWORK (GIN) 2010: CLIMATE CHANGE AND GREEN GROWTH: INNOVATING FOR SUSTAINABILITY ')
PTFE = Material(name='PTFE', gwp=9.6, basis= 'kg', label='Poly tetra fluoroethylene', citation='https://shamrocktechnologies.com/co2-emissions/')


# *-------------------------Processes ------------------------------------

cost_dict = get_data(file_name='cost_dict')
# Unit for gwp is kgCO2/Kwh

LiI_c = Process(name='LiI_c', conversion={Charge: 1, Power: -1}, cost = cost_dict['HO']['moderate']['LiI_c']['0'],\
    prod_max=bigM, trl='nrel', block='power_storage', label='Lithium-ion battery', citation='Zakeri 2015')
LiI_d = Process(name='LiI_d', conversion={Charge: -1.1765, Power: 1}, cost =  {'CAPEX': smallM, 'Fixed O&M': 0, 'Variable O&M': smallM, \
    'units': '$/kg','source': 'dummy'}, \
    prod_max=bigM, trl='discharge', block='power_storage', label='Lithium-ion battery discharge', citation='Zakeri 2015')
CAES_c = Process(name='CAES_c', conversion={Air_C: 1, Power: -1}, cost = cost_dict['HO']['moderate']['CAES_c']['0'], \
    intro_scale=0, prod_max=bigM, trl='pilot', block='power_storage', label='Compressed air energy storage (CAES)', citation='Zakeri 2015')
CAES_d = Process(name='CAES_d', conversion={Air_C: -1.4286, Power: 1}, cost =  {'CAPEX': smallM, 'Fixed O&M': 0, 'Variable O&M': smallM, \
    'units': '$/kg','source': 'dummy'},\
    intro_scale=0, prod_max=bigM, trl='discharge', block='power_storage', label='Compressed air energy storage (CAES) discharge', citation='Zakeri 2015')
PSH_c = Process(name='PSH_c', conversion={H2O_E: 1, Power: -1}, cost = cost_dict['HO']['moderate']['PSH_c']['0'], \
    intro_scale=0, prod_max=bigM, trl='nrel', block='power_storage', label='Pumped storage hydropower (PSH)', citation='Zakeri 2015')
PSH_d = Process(name='PSH_d', conversion={H2O_E: -1.4286, Power: 1}, cost =  {'CAPEX': smallM, 'Fixed O&M': 0, 'Variable O&M': smallM, \
    'units': '$/kg','source': 'dummy'}, \
    prod_max=bigM, trl='discharge', block='power_storage', label='Pumped storage hydropower (PSH) discharge', citation='Zakeri 2015')
PV = Process(name='PV', intro_scale=pv_start, conversion={Solar: -1, Power: 1, H2O: -20}, cost = cost_dict['HO']['moderate']['PV']['0'], \
    varying_capacity_df = ho_solar_df, prod_max=bigM, gwp=0.005, land=13320/1800, trl='nrel', block='power_generation', lifetime=(25,30), label='Solar photovoltaics (PV) array', citation='Use pvlib conversion, Lu 2021, Marco Raugei 2020')
WF = Process(name='WF', conversion={Wind: -1, Power: 1, H2O: -1}, cost = cost_dict['HO']['moderate']['WF']['0'], \
    varying_capacity_df = ho_wind_df, prod_max=bigM, gwp=0.003, land=10800/1800, trl='nrel', block='power_generation', lifetime=(20,25),\
        label='Wind mill array', citation='Use windtoolkit conversion, Ziegler 2018, Marco Raugei 2020')
AKE = Process(name='AKE', intro_scale=ake_start, conversion={Power: -1, H2_G: 19.474, O2: 763.2, H2O: -175.266}, \
    cost = cost_dict['HO']['moderate']['AKE']['0'], prod_max=bigM, gwp=(0.7,6.6), trl='utility', block='material_production', lifetime=(7,10),\
        label='Alkaline water electrolysis (AWE)', citation='Demirhan et al. 2018 AIChE paper, Luo 2021, Kanz 2021')  # 20.833 MW required to produce 1000t/day.H2, unit for gwp is per kgH2
SMRH = Process(name='SMRH', intro_scale=smrh_start, conversion={Power: -1.11*10**(-3), CH4: -3.76, H2O: -23.7, H2_B: 1, CO2_Vent: 1.03, CO2: 9.332}, \
    cost = cost_dict['HO']['moderate']['SMRH']['0'], prod_max=bigM, gwp=(11.888*(1-0.55), 11.888*(1-0.9)), trl='enterprise', block='material_production', lifetime=20,\
        label='Steam methane reforming + CCUS', citation='Mosca 2020, 90pc capture, Schreiber 2020, https://www.nrel.gov/docs/fy01osti/27637.pdf')  #capture efficiency-55%-90%, Antonini 2020, unit for gwp is per kgH2
# SMR = Process(name='SMR', intro_scale=smr_start, cost = cost_dict['HO']['moderate']['SMR']['0'], conversion={Power: -1.11*10**(-3), CH4: -3.76, H2O: -23.7, H2_B: 1, CO2_Vent: 9.4979}, prod_max=bigM, gwp=0, trl='enterprise',
#                       block='material_production', label='Steam methane reforming', citation='Mosca 2020')
ASMR = Process(name='ASMR', conversion={Uranium: -4.17*10**(-5), H2O: -3364.1, Power: 1}, cost = cost_dict['HO']['moderate']['ASMR']['0'], \
    intro_scale=asmr_start, gwp=9100, prod_max=bigM, land=1100/1800, trl='pilot', block='power_generation', lifetime=30, label='Small modular reactors (SMRs)', \
        citation='https://www.iaea.org/newscenter/news/what-are-small-modular-reactors-smrs#:~:text=SMRs%20have%20reduced%20fuel%20requirements,to%2030%20years%20without%20refuelling.')
H2_C_c = Process(name='H2_C_c', conversion={Power: -1.10*10**(-3), H2_C: 1, H2: -1}, cost = cost_dict['HO']['moderate']['H2_C_c']['0'], \
    prod_max=12000, gwp=0, trl='pilot', block='material_storage', label='Hydrogen local storage (Compressed)', \
        citation='Bossel and Eliasson - Energy and the Hydrogen Economy, ')
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
    intro_scale=4, prod_max=bigM, gwp=0, trl='pilot', block='CCUS', lifetime=(12,20), label='Direct air capture', citation='D. Belloti et al (2017), Beuttler (2019)')
# DOWC = Process(name='DOWC', intro_scale=20, prod_max=bigM, gwp=0,
#                        trl='repurposed', block='CCUS', label='Depleted oil wells')
EOR = Process(name='EOR', intro_scale=0, conversion={Power: -0.00255, CO2: -1, CO2_EOR: 1, CO2_Vent: 0.67}, \
    cost = cost_dict['HO']['moderate']['EOR']['0'], prod_max=bigM, gwp=438, carbon_credit=True, \
        trl='enterprise', block='CCUS', label='CO2-Enhanced oil recovery', citation='Nicholas A.Azzolina (2016)') #unit for gwp is per bbl
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
Na_S = Process(name='Na-S', gwp=0.028, lifetime=(10,15), label='Sodium-Sulfur', citation= 'Florin, N. and Dominish, E. (2017), Zakeri 2015')
Lead = Process(name='Lead', gwp=0.075, lifetime=(5,15), label='Lead-acid', citation= 'Florin, N. and Dominish, E. (2017), Zakeri 2015')
VRB = Process(name='VRB', gwp=0.02, lifetime=(5,10), label='VRB', citation= 'Florin, N. and Dominish, E. (2017), Zakeri 2015')
Ni_Cd = Process(name='Na-S', gwp=0.08, lifetime=(10,20), label='Ni-Cd', citation= 'Florin, N. and Dominish, E. (2017), Zakeri 2015')



demand = {(0, i): 100.0 for i in range(scales.discretization_list[1])}


# *-------------------------Geographic scales/location------------------------------------
HO = Location(name='HO', processes= {H2_L_c, H2_L_d, PV, LiI_c, LiI_d, WF, AKE, SMRH}, demand = demand, scales = scales, label='Houston')
# LA = Location(name='LA', processes= {H2_L_c, H2_L_d, PV, LiI_c, LiI_d, WF, SMRH}, demand = demand, scales = scales, label='Los Angeles')

# # *-------------------------Input data graphs------------------------------------
graph.capacity_factor(location= HO, process= PV, color= 'orange')
graph.capacity_factor(location= HO, process= WF, color= 'steelblue')

graph.cost_factor (location= HO, resource= CH4, color = 'indianred') 


# *-------------------------Transport modes------------------------------------
Train_H2 = Transport(name= 'Train_H2', resources= {H2_L, H2_C}, label= 'Railway for hydrogen transportation', trans_max= 10**8, trans_loss= 0.001, trans_cost= 1.667*10**(-3))
Pipe = Transport(name= 'Pipe', resources= {H2_L}, trans_max= 10**8, trans_loss= 0.001, trans_cost= 0.5*10**(-3), label= 'Railroad transport')


# *-------------------------Network------------------------------------
distance_matrix = [
    [0, 678],
    [678, 0]
                   ]

transport_matrix = [
    [[], [Train_H2, Pipe]],
    [[Train_H2, Pipe], []] 
                   ]

# network = Network(name= 'Network', network = HO, distance_matrix= distance_matrix, transport_matrix= transport_matrix) 

# *-------------------------Scenario------------------------------------

case = Scenario(name= '', network= HO, scales= scales,  expenditure_scale_level= 2, scheduling_scale_level= 2, network_scale_level= 0, demand_scale_level= 1, label= 'shell milp case study')

# *-------------------------Model formulation------------------------------------
milp = formulate_milp(scenario= case)


results = solve(scenario = case, instance=milp, solver= 'gurobi', name='cs_material', print_solversteps= True)



# %%
