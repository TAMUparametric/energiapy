
#%%

"""
Flexibility analysis case study 
"""
# flexibility test: given a fixed range for the uncertain parameter Fh,  where is the critical point?

# case study source: https://doi.org/10.1016/0098-1354(87)87011-4 (Grossmann and Floudas 1987)

__author__ = "Natasha Jane Chrisandina, Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Natasha Jane Chrisandina", "Rahul Kakodkar", "Efstratios N. Pistikopoulos", "Mahmoud M. El-Halwagi"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Natasha Jane Chrisandina"
__email__ = "nchrisandina@tamu.edu"
__status__ = "Production"

# *-------------------------Import modules------------------------------------
import pandas
# import numpy 
# from pyomo.opt import SolverStatus, TerminationCondition
from src.energiapy.components.temporal_scale import Temporal_scale
from src.energiapy.components.resource import Resource
from src.energiapy.components.process import Process
from src.energiapy.components.location import Location
from src.energiapy.components.network import Network
from src.energiapy.components.scenario import Scenario
from src.energiapy.components.transport import Transport
from src.energiapy.graph import graph
from src.energiapy.model.formulate_mpmilp import formulate_mpmilp
from src.energiapy.model.pyomo_solve import solve

# *-------------------------Temporal scales------------------------------------
#Defined as a single temporal scale with 42 discretization, base scale becomes 0
scales = Temporal_scale(discretization_list= [1, 42])

# *-------------------------Constants defined here for ease------------------------------------
bigM = 10**10 #very large number
water_price = 31.70  # $/5000gallons
power_price = 8  # cents/kWh
ur_price = 42.70  # 250 Pfund U308 (Uranium)
A_f = 0.05  # annualization factor

# *-------------------------Resources------------------------------------
Charge = Resource(name='Charge', sell=False,
                          store_max=bigM, basis='MW', label='Battery energy')
Solar = Resource(name='Solar', cons_max=10**20, basis='MW', label='Solar Power')
Wind = Resource(name='Wind', cons_max=10**20, basis='MW', label='Wind Power')
H2_L = Resource(name='H2_L', sell=True, store_max=10**10, demand=True, basis='kg', label='Hydrogen - Geological')
H2 = Resource(name='H2', basis='kg', label='Hydrogen')
H2O = Resource(name='H2O', cons_max=10**20, price=water_price/(5000*3.7854), basis='kg', label='Water')
O2 = Resource(name='O2', sell=True, loss=0.07, basis='kg', label='Oxygen')
CH4 = Resource(name='CH4', cons_max=10**20, varying = True, price=1, basis='kg', label='Natural gas')
CO2 = Resource(name='CO2', basis='kg', label='Carbon dioxide')
Power = Resource(name='Power', basis='MW', label='Renewable power generated')



# *-------------------------Processes ------------------------------------
LiI_c = Process(name='LiI_c', conversion={Charge: 1, Power: -1}, prod_max=bigM, \
    label='Lithium-ion battery', citation='Zakeri 2015', basis = 'MW')
LiI_d = Process(name='LiI_d', conversion={Charge: -1.1765, Power: 1}, prod_max=bigM, \
    label='Lithium-ion battery discharge', citation='Zakeri 2015', basis = 'MW')
PV = Process(name='PV',  conversion={Solar: -1, Power: 1, H2O: -20}, varying= True, prod_max=bigM, label='Solar photovoltaics (PV) array', citation='Use pvlib conversion', basis = 'MW')
WF = Process(name='WF', conversion={Wind: -1, Power: 1, H2O: -1}, varying= True, prod_max=bigM, \
    label='Wind mill array', citation='Use windtoolkit conversion', basis = 'MW')
AKE = Process(name='AKE', conversion={Power: -1, H2: 19.474, O2: 763.2, H2O: -175.266}, \
    prod_max=bigM, label='Alkaline water electrolysis (AWE)', citation='Demirhan et al. 2018 AIChE paper', basis = 'MW')  # 20.833 MW required to produce 1000t/day.H2
H2_L_c = Process(name='H2_L_c', conversion={Power: -4.17*10**(-4), H2_L: 1, H2: -1}, prod_max=bigM, \
    label='Hydrogen geological storage', citation='Bossel and Eliasson - Energy and the Hydrogen Economy', basis = 'kg')
H2_L_d = Process(name='H2_L_d', conversion={H2_L: -1, H2: 1}, prod_max=bigM, \
    label='Hydrogen geological storage discharge', citation='Bossel and Eliasson - Energy and the Hydrogen Economy', basis = 'kg')


# *-------------------------Geographic scales/location------------------------------------

#candidate cities (sources)
#can only produce and transport green hydrogen that passes through liquefaction/storage is optional
CityA = Location(name= 'A', processes= {PV, LiI_c, LiI_d, WF, AKE, H2_L_c, H2_L_d}, scales = scales, label= 'city A')
CityB = Location(name= 'B', processes= {PV, LiI_c, LiI_d, WF, AKE, H2_L_c, H2_L_d}, scales = scales, label= 'city B')
CityC = Location(name= 'C', processes= {PV, LiI_c, LiI_d, WF, AKE, H2_L_c, H2_L_d}, scales = scales, label= 'city C')

#candidate cities (sinks)
#can only consume green hydrogen that is liquefied or dispensed through storage. 
Site1 = Location(name= '1', processes = {H2_L_c, H2_L_d}, demand = {H2_L: 2}, scales = scales, label= 'site close to A')
Site2 = Location(name= '2', processes = {H2_L_c, H2_L_d}, demand = {H2_L: 2}, scales = scales, label= 'site close to B')
Site3 = Location(name= '3', processes = {H2_L_c, H2_L_d}, demand = {H2_L: 2}, scales = scales, label= 'site close to C')
Site4 = Location(name= '4', processes = {H2_L_c, H2_L_d}, demand = {H2_L: 2}, scales = scales, label= 'site between A and B')
Site5 = Location(name= '5', processes = {H2_L_c, H2_L_d}, demand = {H2_L: 2}, scales = scales, label= 'site between B and C')
Site6 = Location(name= '6', processes = {H2_L_c, H2_L_d}, demand = {H2_L: 2}, scales = scales, label= 'site between C and A')
Site7 = Location(name= '7', processes = {H2_L_c, H2_L_d}, demand = {H2_L: 2}, scales = scales, label= 'site between A, B and C')

city_list = [CityA, CityB, CityC] #sources
site_list = [Site1, Site2, Site3, Site4, Site5, Site6, Site7] #sinks


# *-------------------------Transport modes------------------------------------
Train = Transport(name= 'Train', resources= {H2_L}, trans_max= 100, trans_loss= 0.002, trans_cost= 1.667*10**(-3), label= 'Railroad transport')
Pipe = Transport(name= 'Pipe', resources= {H2_L}, trans_max= 100, trans_loss= 0.001, trans_cost= 0.5*10**(-3), label= 'Railroad transport')



# *-------------------------Network------------------------------------
#distance between sources and sinks. y - sinks (seven), x - sources (three) 
distance_matrix = [
    [  0.  ,  40.  , 120.4 ,  27.  ,  52.2 ,  68.7 ,  40.5 ],
    [ 40.  ,   0.  , 125.4 ,  12.  ,  47.  ,  77.7 ,  39.8 ],
    [120.4 , 125.4 ,   0.  , 122.19,  78.4 ,  51.7 ,  86.8 ]
    ]

#transportation modes available between sources and sinks. y - sinks (seven), x - sources (three) 
transport_matrix = [
    [  []  ,  [Train, Pipe]  , [Train] ,  [Pipe]  ,  [Pipe] ,  [Pipe] ,  [Train] ],
    [ [Train]  ,   []  , [Train, Pipe] ,  [Train]  ,  [Train]  ,  [Pipe] ,  [Train, Pipe] ],
    [[Pipe] , [Train, Pipe] ,   []  , [Train, Pipe],  [Pipe] ,  [Train] ,  [Train] ]
    ]

#define the network
Arcs = Network(name= 'Arcs', source_locations= city_list, sink_locations= site_list, \
    distance_matrix= distance_matrix, transport_matrix= transport_matrix, label= 'connections between cities and sites')

# *-------------------------Scenario------------------------------------
#given that this is a single temporal scale model, all scales could be allowed to default to 0. Scales stated here due to clarity
case = Scenario(name= '', network= Arcs, scales= scales, \
    expenditure_scale_level= 1, scheduling_scale_level= 1, network_scale_level= 0,  demand_scale_level=1,  label= 'mpmilp case study')

# *-------------------------Model formulation------------------------------------
#this creates a pyomo instance, prior to this step the model is only defined in energiapy
mpmilp = formulate_mpmilp(scenario= case, penalty= 1)

results = solve(scenario = case, instance=mpmilp, solver= 'gurobi', name='trial', tee = True)
# results = solve(scenario = case, instance=mpmilp, solver= 'gurobi', name='trial', saveformat= '.pkl', tee = True)


#%% plots results at requested scales, usetex giving a very unique error only for this plot!! 
#TODO - add the type of graph generated in the title
location = 'B'
for i in case.process_set:
    graph.schedule(results = results, y_axis = 'P', component= i.name, location= location, usetex = False)
#%%
for i in case.resource_set:
    graph.schedule(results = results, y_axis = 'S', component= i.name, location= location, usetex = False)
#%%
for i in case.resource_set:
    graph.schedule(results = results, y_axis = 'C', component= i.name, location= location, usetex = False)
for i in case.resource_set:
    graph.schedule(results = results, y_axis = 'B', component= i.name, location= location, usetex = False)    
for i in case.resource_set:
    graph.schedule(results = results, y_axis = 'Inv', component= i.name, location= location, usetex = False)    

for i in case.process_set:
    if i.varying == True:
        graph.schedule(results = results, y_axis = 'Delta_Cap_P', component= i.name, location= location, usetex = False)    
#%%
graph.schedule(results = results, y_axis = 'P', component= 'WF', location= 'C', usetex = False)

# %%


# %%
# %%
