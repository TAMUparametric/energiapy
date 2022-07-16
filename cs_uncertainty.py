
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
from pyomo.environ import SolverFactory  
from src.energiapy.components.temporal_scale import Temporal_scale
from src.energiapy.components.resource import Resource
from src.energiapy.components.process import Process
from src.energiapy.components.material import Material
from src.energiapy.components.location import Location
from src.energiapy.components.network import Network
from src.energiapy.components.scenario import Scenario
from src.energiapy.components.transport import Transport
from src.energiapy.model.pyomo_cons import *
from src.energiapy.graph import graph
from src.energiapy.model.mpmilp import formulate_mpmilp

# *-------------------------Temporal scales------------------------------------
# scales = temporal_scale(discretization_list = [4, 20, 15])
scales = Temporal_scale(discretization_list= [1])
# scales = temporal_scale(discretization_list = [1, 2, 3])

# *-------------------------Constance defined here for ease------------------------------------
bigM = 10**10 #very large number
water_price = 31.70  # $/5000gallons
power_price = 8  # cents/kWh
ur_price = 42.70  # 250 Pfund U308 (Uranium)
A_f = 0.05  # annualization factor

# *-------------------------Resources------------------------------------
Charge = Resource(name='Charge', sell=False,
                          store_max=bigM, basis='MW', label='Battery energy')
Solar = Resource(name='Solar', consumption_max=10**20, basis='MW', label='Solar Power')
Wind = Resource(name='Wind', consumption_max=10**20, basis='MW', label='Wind Power')
H2_C = Resource(name='H2_C', sell=True, store_max=10**4, loss=0.025/24, demand=True, basis='kg', label='Hydrogen - Local Cryo') 
H2_L = Resource(name='H2_L', sell=True, store_max=10**10, demand=True, basis='kg', label='Hydrogen - Geological')
H2 = Resource(name='H2', basis='kg', label='Hydrogen')
H2_B = Resource(name='H2_B', basis='kg', label='Blue hydrogen')
H2_G = Resource(name='H2_G', basis='kg', label='Green hydrogen')
H2O = Resource(name='H2O', consumption_max=10**20, price=water_price/(5000*3.7854), basis='kg', label='Water')
O2 = Resource(name='O2', sell=True, loss=0.07, basis='kg', label='Oxygen')
CH4 = Resource(name='CH4', consumption_max=10**20, varying = True, price=1, basis='kg', label='Natural gas')
CO2 = Resource(name='CO2', basis='kg', label='Carbon dioxide')
Power_Gr = Resource(name='Power_Gr', consumption_max=10 **20, price=power_price*(10), basis='kg', label='Grid electricity')
Power = Resource(name='Power', basis='MW', label='Renewable power generated')
CO2_Vent = Resource(name='CO2_Vent', sell=True, basis='kg', label='Carbon dioxide - Vented')
H2_cons = Resource(name='H2_cons', sell=True, basis='kg', label='Hydrogen consumed at site')


# *-------------------------Materials------------------------------------
Li = Material(name='Li', gwp=30, basis= 'kg', label='Lithium', citation= 'some paper')
St = Material(name='St', gwp=50, basis= 'kg', label='Steel')

# *-------------------------Processes ------------------------------------

LiI_c = Process(name='LiI_c', conversion={Charge: 1, Power: -1}, material_cons = {Li: 20, St:5}, prod_max=bigM, \
    label='Lithium-ion battery', citation='Zakeri 2015')
LiI_d = Process(name='LiI_d', conversion={Charge: -1.1765, Power: 1}, prod_max=bigM, \
    label='Lithium-ion battery discharge', citation='Zakeri 2015')
PV = Process(name='PV',  conversion={Solar: -1, Power: 1, H2O: -20}, varying= True, label='Solar photovoltaics (PV) array', citation='Use pvlib conversion')
WF = Process(name='WF', conversion={Wind: -1, Power: 1, H2O: -1}, varying= True, prod_max=bigM, \
    label='Wind mill array', citation='Use windtoolkit conversion')
AKE = Process(name='AKE', conversion={Power: -1, H2_G: 19.474, O2: 763.2, H2O: -175.266}, \
    prod_max=bigM, label='Alkaline water electrolysis (AWE)', citation='Demirhan et al. 2018 AIChE paper')  # 20.833 MW required to produce 1000t/day.H2
SMRH = Process(name='SMRH', conversion={Power: -1.11*10**(-3), CH4: -3.76, H2O: -23.7, H2_B: 1, CO2_Vent: 1.03, CO2: 9.332},\
    prod_max=bigM, label='Steam methane reforming + CCUS', citation='Mosca 2020, 90pc capture')
H2_C_c = Process(name='H2_C_c', conversion={Power: -1.10*10**(-3), H2_C: 1, H2: -1},  prod_max=12000,\
    label='Hydrogen local storage (Compressed)', citation='Bossel and Eliasson - Energy and the Hydrogen Economy')
H2_C_d = Process(name='H2_C_d',  conversion={H2_C: -1, H2: 1}, prod_max=bigM, \
    label='Hydrogen local storage (Compressed) discharge', citation='Bossel and Eliasson - Energy and the Hydrogen Economy')
H2_L_c = Process(name='H2_L_c', conversion={Power: -4.17*10**(-4), H2_L: 1, H2: -1}, prod_max=bigM, \
    label='Hydrogen geological storage', citation='Bossel and Eliasson - Energy and the Hydrogen Economy')
H2_L_d = Process(name='H2_L_d', conversion={H2_L: -1, H2: 1}, prod_max=bigM, \
    label='Hydrogen geological storage discharge', citation='Bossel and Eliasson - Energy and the Hydrogen Economy')
H2_Blue = Process(name='H2_Blue', conversion={H2: 1, H2_B: -1}, prod_max=bigM, label='Blue Hydrogen production')
H2_Green = Process(name='H2_Green', conversion={H2: 1, H2_G: -1}, prod_max=bigM, label='Green Hydrogen production')
H2_G_sink = Process(name='H2_G_sink', conversion={H2_G: -1, H2_cons: 1}, prod_max=bigM, label='Green Hydrogen consumption at site')
H2_B_sink = Process(name='H2_B_sink', conversion={H2_B: -1, H2_cons: 1}, prod_max=bigM, label='Blue Hydrogen consumption at site')


# *-------------------------Geographic scales/location------------------------------------

#candidate cities (sources)
CityA = Location(name= 'A', processes= {PV, LiI_c, LiI_d, WF, AKE}, scales = scales, label= 'city A')
CityB = Location(name= 'B', processes= {PV, LiI_c, LiI_d, WF, AKE}, scales = scales, label= 'city B')
CityC = Location(name= 'C', processes= {PV, LiI_c, LiI_d, WF, AKE}, scales = scales, label= 'city C')

#candidate cities (sinks)
Site1 = Location(name= '1', processes = {H2_G_sink}, scales = scales, label= 'site close to A')
Site2 = Location(name= '2', processes = {H2_G_sink}, scales = scales, label= 'site close to B')
Site3 = Location(name= '3', processes = {H2_G_sink}, scales = scales, label= 'site close to C')
Site4 = Location(name= '4', processes = {H2_G_sink}, scales = scales, label= 'site between A and B')
Site5 = Location(name= '5', processes = {H2_G_sink}, scales = scales, label= 'site between B and C')
Site6 = Location(name= '6', processes = {H2_G_sink}, scales = scales, label= 'site between C and A')
Site7 = Location(name= '7', processes = {H2_G_sink}, scales = scales, label= 'site between A, B and C')

# location_list = [CityA, CityB, CityC, Site1, Site2, Site3, Site4, Site5, Site6, Site7]
city_list = [CityA, CityB, CityC]
site_list = [Site1, Site2, Site3, Site4, Site5, Site6, Site7]

# city_list = [CityA]
# site_list = [Site1]

# *-------------------------Transport modes------------------------------------
Train = Transport(name= 'Train', resources= {H2_G}, trans_max= 10**8, trans_loss= 0.002, trans_cost= 1.667*10**(-3), label= 'Railroad transport')
Pipe = Transport(name= 'Pipe', resources= {H2_G}, trans_max= 10**8, trans_loss= 0.001, trans_cost= 0.5*10**(-3), label= 'Railroad transport')



# *-------------------------Network------------------------------------
distance_matrix = [
    [  0.  ,  40.  , 120.4 ,  27.  ,  52.2 ,  68.7 ,  40.5 ],
    [ 40.  ,   0.  , 125.4 ,  12.  ,  47.  ,  77.7 ,  39.8 ],
    [120.4 , 125.4 ,   0.  , 122.19,  78.4 ,  51.7 ,  86.8 ]
    ]

transport_matrix = [
    [  []  ,  [Train, Pipe]  , [Train] ,  [Pipe]  ,  [Pipe] ,  [Pipe] ,  [Train] ],
    [ [Train]  ,   []  , [Train, Pipe] ,  [Train]  ,  [Train]  ,  [Pipe] ,  [Train, Pipe] ],
    [[Pipe] , [Train, Pipe] ,   []  , [Train, Pipe],  [Pipe] ,  [Train] ,  [Train] ]
    ]

Arcs = Network(name= 'Arcs', source_locations= city_list, sink_locations= site_list, \
    distance_matrix= distance_matrix, transport_matrix= transport_matrix, label= 'connections between cities and sites')

# *-------------------------Scenario------------------------------------

case = Scenario(name= '', network= Arcs, scales= scales, \
    expenditure_scale_level= 0, scheduling_scale_level= 0, network_scale_level= 0, label= 'mpmilp case study')

# *-------------------------Model formulation------------------------------------

mpmilp = formulate_mpmilp(scenario= case)

result = SolverFactory('gurobi', solver_io= 'python').solve(mpmilp)


#%%





#%%

m = ConcreteModel()

#================================================================================================================
    #*                                                 Sets
#================================================================================================================

city = ["A","B","C"]
m.city = Set(initialize = range(len(city)), doc = 'city node indices')

site = ["A","B","C","A+B","B+C","A+C","A+B+C"]
m.site = Set(initialize = range(len(site)), doc = 'facility node indices')

time = np.arange(0,42,1) #42 time steps
m.time = Set(initialize = time, doc = 'time span of interest')

timenext = np.arange(1,42,1) #
m.timenext = Set(initialize = timenext, doc = 'time span of interest but without the first time period')

utility = ["electric", "gas", "water"]
m.utility = Set(initialize = range(len(utility)), doc = 'utility indices')

#================================================================================================================
    #*                                                 Parameters
#================================================================================================================

# finance

tax = 0.28 #corporate tax rate
lifetime = 10 #project lifetime to calculate salvage value
Cproduct = 350 #product sell price
Cbiomass = 55 #feedstock cost
Cutilities = [0.05, 1.20, 0.45] #utilities cost
Cbiomasstransport = 0.011 # cost of biomass transport per mile per ton
Cproducttransport = 0.015 # cost of product transport per mile per ton

# plant product capacity
conversion = 2.4
LB = 25000 #lower bound
UB = [50000, 50000, 50000, 75000, 75000, 75000, 100000] #upper bound
number_plant = 1 #max number of plants per site

# material availability

biomass_max = [2*45000, 2*100000, 2*75000] #max biomass available in each city
product_max = [2*0, 2*60000, 2*25000] #max demand in each city
u_perbiomass = [500, 0.08, 0.15] #unit of utility needed per ton of biomass

path_exist = [
    [1,1,0],
    [1,1,1],
    [0,1,1],
    [1,1,1],
    [1,1,1],
    [1,1,1],
    [1,0,1]       
]

# distance between city and each site
distance = [
    [0,40,120.4],
    [40,0,125.4],
    [120.4,125.4,0],
    [27,12,122.19],
    [52.2,47,78.4],
    [68.7,77.7,51.7],
    [40.5,39.8,86.8]
]

#this is for drawing, it's an order of magnitude smaller
shortdistance = [
    [0,4.0,12.04],
    [4.0,0,12.54],
    [12.04,12.54,0],
    [2.7,1.2,12.219],
    [5.22,4.7,7.84],
    [6.87,7.77,5.17],
    [4.05,3.98,8.68]
]

# steady state supply chain data

sites_chosen = [1,0,1,0,0,0,1]

# node recovery pattern
disrupted = [0,0,0,0,0,0,0] # disruption pattern

recovery = [
    [0,0,0,0,0,0,0],
    [0.15,0.13,0.05,0.05,0.05,0.05,0.06],
    [0.16,0.13,0.08,0.13,0.11,0.05,0.09],
    [0.19,0.16,0.08,0.15,0.11,0.08,0.1],
    [0.23,0.19,0.13,0.18,0.15,0.12,0.12],
    [0.25,0.21,0.14,0.19,0.17,0.16,0.13],
    [0.3,0.21,0.15,0.25,0.25,0.17,0.14],
    [0.32,0.24,0.18,0.25,0.29,0.18,0.18],
    [0.37,0.26,0.2,0.25,0.33,0.18,0.19],
    [0.38,0.27,0.24,0.26,0.37,0.18,0.2],
    [0.4,0.37,0.26,0.27,0.37,0.18,0.21],
    [0.41,0.38,0.27,0.28,0.39,0.2,0.24],
    [0.42,0.43,0.27,0.28,0.41,0.26,0.29],
    [0.43,0.55,0.27,0.33,0.43,0.28,0.29],
    [0.45,0.65,0.28,0.35,0.45,0.32,0.37],
    [0.49,0.67,0.32,0.37,0.48,0.33,0.42],
    [0.5,0.68,0.34,0.41,0.53,0.34,0.46],
    [0.63,0.69,0.37,0.44,0.54,0.35,0.46],
    [0.64,0.72,0.47,0.45,0.56,0.36,0.48],
    [0.64,0.72,0.47,0.45,0.56,0.36,0.48],
    [0.64,0.76,0.48,0.49,0.56,0.46,0.5],
    [0.68,0.76,0.5,0.5,0.61,0.49,0.5],
    [0.72,0.8,0.52,0.53,0.65,0.52,0.51],
    [0.71,0.81,0.52,0.54,0.67,0.54,0.61],
    [0.75,0.83,0.54,0.57,0.7,0.55,0.61],
    [0.76,0.84,0.57,0.58,0.71,0.57,0.61],
    [0.75,0.85,0.63,0.58,0.75,0.61,0.63],
    [0.77,0.86,0.65,0.63,0.77,0.61,0.63],
    [0.77,0.87,0.66,0.65,0.94,0.76,0.64],
    [0.77,0.92,0.68,0.7,0.96,0.77,0.65],
    [0.78,0.94,0.76,0.78,0.96,0.79,0.65],
    [0.8,0.95,0.79,0.82,0.96,0.85,0.67],
    [0.8,0.96,0.87,0.83,1,0.88,0.74],
    [0.81,0.97,0.89,0.84,1,0.98,0.76],
    [0.84,0.97,0.91,0.84,1,0.98,0.78],
    [0.86,0.99,0.95,0.85,1,0.98,0.79],
    [0.9,1,0.97,0.88,1,1,0.79],
    [0.91,1,0.99,0.88,1,1,0.8],
    [0.92,1,1,0.95,1,1,0.82],
    [0.93,1,1,0.99,1,1,0.97],
    [0.93,1,1,1,1,1,0.98],
    [1,1,1,1,1,1,1],
] #recovery pattern %%

deltaT = 10 # time period sizes

finalTime = time[-1] *deltaT # in hours

productmax_disrupted = np.zeros((len(time), len(site)))
for t in range(0,42,1):
    for l in m.site:
        if disrupted[l] == 0:
            productmax_disrupted[t,l] = UB[l]
        else:
            productmax_disrupted[t,l] = recovery[t][l] * UB[l]


choosesite = np.zeros((len(time), len(site)))
for t in range(0,42,1):
    for l in m.site:
        if productmax_disrupted[t,l] < LB:
            choosesite[t,l] = 0
        else:
            choosesite[t,l] = sites_chosen[l]
#================================================================================================================
    #*                                                 Variables
#================================================================================================================

# continuous variables

# production-related variables that could change as a result of a disruption

m.production = Var(m.time, m.site, domain = NonNegativeReals, initialize = 25000, doc = 'Amount of product made in site l at time t')
m.netproduct = Var(m.time,m.city, domain = NonNegativeReals, initialize = 25000, doc = 'Amount of product received by city i at time t')
m.productship = Var(m.time, m.site, m.city, domain = NonNegativeReals, initialize = 25000, doc = 'Amount of product shipped from site l to city i at time t')
m.biomassused = Var(m.time, m.site, bounds = (0,250000), initialize = 25000, doc = 'amount of biomass used for production in site l at time t')
m.biomassship = Var(m.time, m.site, m.city, domain = NonNegativeReals, initialize = 25000, doc = 'amount of biomass shipped from city i to site l at time t')

# economic variables
m.annualsales = Var(m.time, m.site, domain = NonNegativeReals, initialize = 2000000, doc = 'annual sales from site l given production levels at time t')
m.fixedcost = Var(m.time, m.site, bounds = (0,100000000), doc = 'fixed capital investment')
m.annualfixedcost = Var(m.time, m.site, domain = NonNegativeReals, doc = 'annualized fixed capital investment')
m.opex = Var(m.time, m.site, domain = NonNegativeReals, initialize = 300, doc = 'operational expenses')
m.profit = Var(m.time, m.site, domain = NonNegativeReals, initialize = 300, doc = 'annual net profit')

#================================================================================================================
    #*                                                 Constraints
#================================================================================================================

# finance calculations

m.Sales = ConstraintList(doc = 'calculate annual sales per site')
for l in m.site:
    for t in m.time:
        m.Sales.add(m.annualsales[t,l] == Cproduct * m.production[t,l])

m.fixedcapital = ConstraintList(doc = 'calculate fixed capital per site')
for l in m.site:
    for t in m.time:
        m.fixedcapital.add(m.fixedcost[t,l] == 10**6 * (m.biomassused[t,l]/1000)**0.84 * 0.16 * 6)

m.annualfixedcapital = ConstraintList(doc = 'annualize fixed capital per site')
for l in m.site:
    for t in m.time:
        m.annualfixedcapital.add(m.annualfixedcost[t,l] == m.fixedcost[t,l]/lifetime)

m.operatingcost = ConstraintList(doc = 'calculate OPEX per site')
for l in m.site:
    for t in m.time:
        m.operatingcost.add(m.opex[t,l] == (Cbiomass * m.biomassused[t,l]) + sum(Cutilities[u] * u_perbiomass[u] * m.biomassused[t,l] for u in m.utility) + (sum(Cbiomasstransport * m.biomassship[t,l,i] * distance[l][i] for i in m.city) + sum(Cproducttransport * m.productship[t,l,i] * distance[l][i] for i in m.city)))

m.annualprofit = ConstraintList(doc = 'calculate annual net profit per site')
for l in m.site:
    for t in m.time:
        m.annualprofit.add(m.profit[t,l] == (m.annualsales[t,l] - m.opex[t,l] - m.annualfixedcost[t,l]) * (1-tax) + m.annualfixedcost[t,l])

m.sizebounds = ConstraintList(doc = 'upper and lower bounds on site capacity')
for l in m.site:
    for t in m.time:
        m.sizebounds.add(m.production[t,l] >= LB * choosesite[t][l])
        m.sizebounds.add(m.production[t,l] <= productmax_disrupted[t][l] * choosesite[t][l])

# feasibility constraints

m.biomassLimit = ConstraintList(doc = 'biomass mass balance around city i')
for i in m.city:
    for t in m.time:
        m.biomassLimit.add(sum(m.biomassship[t,l,i] for l in m.site) <= biomass_max[i])

m.biomassShipment = ConstraintList(doc = 'biomass mass balance around site l')
for l in m.site:
    for t in m.time:
        m.biomassShipment.add(m.biomassused[t,l] == sum(m.biomassship[t,l,i] * path_exist[l][i] for i in m.city))

m.convert = ConstraintList(doc = 'conversion rate between biomass and product')
for l in m.site:
    for t in m.time:
        m.convert.add(m.production[t,l] == m.biomassused[t,l]/conversion)

m.productShipment = ConstraintList(doc = 'product mass balance around site l')
for l in m.site:
    for t in m.time:
        m.productShipment.add(m.production[t,l] == sum(m.productship[t,l,i] * path_exist[l][i] for i in m.city))

m.productLimit = ConstraintList(doc = 'product mass balance around city i')
for i in m.city:
    for t in m.time:
        m.productLimit.add(product_max[i] >= sum(m.productship[t,l,i] for l in m.site))

#================================================================================================================
    #*                                                 Objective
#================================================================================================================


m.obj = Objective(expr = (sum(m.profit[t,l] for t in m.time for l in m.site))/finalTime, sense=maximize, doc = 'objective: maximize steady-state profit')



result = SolverFactory('gams', solver= 'BARON').solve(m)

def draw_solution(m,result):
    dot = Digraph(engine='neato')
    #first we make the nodes
    for i in m.city:
        dot.node("City {}".format(i),shape='box')
    for l in m.site:
        dot.node("Site {}".format(l),shape='circle')
    #then we make the edges for the 3 cities
    for i in m.city:
        for j in m.city:
            dot.edge("City {}".format(i),"City {}".format(j),dir='none',len="{}".format(shortdistance[i][j]),style='invis')

    #now we make the edges for the sites
    for i in m.city:
        for l in m.site:
            dot.edge("City {}".format(i),"Site {}".format(l),dir='none',len="{}".format(shortdistance[l][i]),style='invis')
    #edges for supply lines
    for i in m.city:
        for l in m.site:
            if m.biomassship[len(time)-1,l,i].value != 0:
                flow = m.biomassship[len(time)-1,l,i].value
                dot.edge("City {}".format(i),"Site {}".format(l),len="{}".format(shortdistance[l][i]),color='red',label=(str(flow) + " ton/y RDF") if flow > 0 else '')
    #edges for demand lines
    for i in m.city:
        for l in m.site:
            if m.productship[len(time)-1,l,i].value != 0:
                flow = m.productship[len(time)-1,l,i].value
                dot.edge("Site {}".format(l),"City {}".format(i),len="{}".format(shortdistance[l][i]),color='green',label=(str(flow) + " ton/y MeOH") if flow > 0 else '')       
    return dot

draw_solution(m,result).view()

# plot profit over time for the system
x = time
y0 = np.zeros(len(time))
for i in m.time:
    y0[i] = sum(m.profit[i,l].value for l in m.site)

plt.plot(x,y0)
plt.title('System profit over time')
plt.xlabel('Time')
plt.ylabel('System profit [$]')
plt.show()


#%%

from sys import executable
from pyomo.environ import *
from pyomo.core import *
import numpy as np
from graphviz import Digraph
import matplotlib.pyplot as plt


def scenarioModel():
    m = ConcreteModel()

    #================================================================================================================
        #*                                                 Sets
    #================================================================================================================

    city = ["A","B","C"]
    m.city = Set(initialize = range(len(city)), doc = 'city node indices')

    site = ["A","B","C","A+B","B+C","A+C","A+B+C"]
    m.site = Set(initialize = range(len(site)), doc = 'facility node indices')

    time = np.arange(0,42,1)
    m.time = Set(initialize = time, doc = 'time span of interest')

    timenext = np.arange(1,42,1)
    m.timenext = Set(initialize = timenext, doc = 'time span of interest but without the first time period')

    utility = ["electric", "gas", "water"]
    m.utility = Set(initialize = range(len(utility)), doc = 'utility indices')

    #================================================================================================================
        #*                                                 Parameters
    #================================================================================================================

    # finance

    tax = 0.28 #corporate tax rate
    lifetime = 10 #project lifetime to calculate salvage value
    Cproduct = 350 #product sell price
    Cbiomass = 55 #feedstock cost
    Cutilities = [0.05, 1.20, 0.45] #utilities cost
    Cbiomasstransport = 0.011 # cost of biomass transport per mile per ton
    Cproducttransport = 0.015 # cost of product transport per mile per ton

    # plant product capacity
    conversion = 2.4
    LB = 25000 #lower bound
    UB = [60000, 50000, 60000, 75000, 75000, 75000, 85000] #upper bound
    number_plant = 1 #max number of plants per site

    # material availability

    # biomass_max = [45000, 100000, 75000] #max biomass available in each city
    # product_max = [0, 60000, 25000] #max demand in each city

    # DOUBLE material availability

    biomass_max = [2*45000, 2*100000, 2*75000] #max biomass available in each city
    product_max = [2*0, 2*60000, 2*25000] #max demand in each city
    u_perbiomass = [500, 0.08, 0.15] #unit of utility needed per ton of biomass

    # does a path exist between city and each site?

    path_exist = [
        [1,1,0],
        [1,1,1],
        [0,1,1],
        [1,1,1],
        [1,1,1],
        [1,1,1],
        [1,0,1]       
    ]

    # distance between city and each site
    distance = [
        [0,40,120.4],
        [40,0,125.4],
        [120.4,125.4,0],
        [27,12,122.19],
        [52.2,47,78.4],
        [68.7,77.7,51.7],
        [40.5,39.8,86.8]
    ]

    #this is for drawing, it's an order of magnitude smaller
    shortdistance = [
        [0,4.0,12.04],
        [4.0,0,12.54],
        [12.04,12.54,0],
        [2.7,1.2,12.219],
        [5.22,4.7,7.84],
        [6.87,7.77,5.17],
        [4.05,3.98,8.68]
    ]

    # steady state supply chain data

    sites_chosen = [1,0,1,0,0,0,1]

    # node recovery pattern
    disrupted = [0,0,1,0,0,0,0] # disruption pattern

    # recovery = [
    #     [0,0,0,0,0,0,0],
    #     [0.15,0.13,0.05,0.05,0.05,0.05,0.06],
    #     [0.16,0.13,0.08,0.13,0.11,0.05,0.09],
    #     [0.19,0.16,0.08,0.15,0.11,0.08,0.1],
    #     [0.23,0.19,0.13,0.18,0.15,0.12,0.12],
    #     [0.25,0.21,0.14,0.19,0.17,0.16,0.13],
    #     [0.3,0.21,0.15,0.25,0.25,0.17,0.14],
    #     [0.32,0.24,0.18,0.25,0.29,0.18,0.18],
    #     [0.37,0.26,0.2,0.25,0.33,0.18,0.19],
    #     [0.38,0.27,0.24,0.26,0.37,0.18,0.2],
    #     [0.4,0.37,0.26,0.27,0.37,0.18,0.21],
    #     [0.41,0.38,0.27,0.28,0.39,0.2,0.24],
    #     [0.42,0.43,0.27,0.28,0.41,0.26,0.29],
    #     [0.43,0.55,0.27,0.33,0.43,0.28,0.29],
    #     [0.45,0.65,0.28,0.35,0.45,0.32,0.37],
    #     [0.49,0.67,0.32,0.37,0.48,0.33,0.42],
    #     [0.5,0.68,0.34,0.41,0.53,0.34,0.46],
    #     [0.63,0.69,0.37,0.44,0.54,0.35,0.46],
    #     [0.64,0.72,0.47,0.45,0.56,0.36,0.48],
    #     [0.64,0.72,0.47,0.45,0.56,0.36,0.48],
    #     [0.64,0.76,0.48,0.49,0.56,0.46,0.5],
    #     [0.68,0.76,0.5,0.5,0.61,0.49,0.5],
    #     [0.72,0.8,0.52,0.53,0.65,0.52,0.51],
    #     [0.71,0.81,0.52,0.54,0.67,0.54,0.61],
    #     [0.75,0.83,0.54,0.57,0.7,0.55,0.61],
    #     [0.76,0.84,0.57,0.58,0.71,0.57,0.61],
    #     [0.75,0.85,0.63,0.58,0.75,0.61,0.63],
    #     [0.77,0.86,0.65,0.63,0.77,0.61,0.63],
    #     [0.77,0.87,0.66,0.65,0.94,0.76,0.64],
    #     [0.77,0.92,0.68,0.7,0.96,0.77,0.65],
    #     [0.78,0.94,0.76,0.78,0.96,0.79,0.65],
    #     [0.8,0.95,0.79,0.82,0.96,0.85,0.67],
    #     [0.8,0.96,0.87,0.83,1,0.88,0.74],
    #     [0.81,0.97,0.89,0.84,1,0.98,0.76],
    #     [0.84,0.97,0.91,0.84,1,0.98,0.78],
    #     [0.86,0.99,0.95,0.85,1,0.98,0.79],
    #     [0.9,1,0.97,0.88,1,1,0.79],
    #     [0.91,1,0.99,0.88,1,1,0.8],
    #     [0.92,1,1,0.95,1,1,0.82],
    #     [0.93,1,1,0.99,1,1,0.97],
    #     [0.93,1,1,1,1,1,0.98],
    #     [1,1,1,1,1,1,1],
    # ] #recovery pattern

    # recovery pattern -- node 0 is stepwise, node 2 is stepwise AND doesn't start at 0 AND doesn't end at 1, node 6 is stepwise
    recovery = [
        [0,0.03,0.2,0.01,0.03,0.01,0],
        [0,0.13,0.2,0.05,0.05,0.05,0],
        [0,0.13,0.2,0.13,0.11,0.05,0],
        [0,0.16,0.2,0.15,0.11,0.08,0],
        [0,0.19,0.2,0.18,0.15,0.12,0],
        [0,0.21,0.2,0.19,0.17,0.16,0],
        [0,0.21,0.2,0.25,0.25,0.17,0],
        [0,0.24,0.2,0.25,0.29,0.18,0],
        [0,0.26,0.2,0.25,0.33,0.18,0],
        [0,0.27,0.2,0.26,0.37,0.18,0.25],
        [0,0.37,0.4,0.27,0.37,0.18,0.25],
        [0.3,0.38,0.4,0.28,0.39,0.2,0.25],
        [0.3,0.43,0.4,0.28,0.41,0.26,0.25],
        [0.3,0.55,0.4,0.33,0.43,0.28,0.25],
        [0.3,0.65,0.4,0.35,0.45,0.32,0.25],
        [0.3,0.67,0.4,0.37,0.48,0.33,0.25],
        [0.3,0.68,0.4,0.41,0.53,0.34,0.25],
        [0.3,0.69,0.4,0.44,0.54,0.35,0.25],
        [0.3,0.72,0.4,0.45,0.56,0.36,0.25],
        [0.3,0.72,0.4,0.45,0.56,0.36,0.5],
        [0.3,0.76,0.6,0.49,0.56,0.46,0.5],
        [0.6,0.76,0.6,0.5,0.61,0.49,0.5],
        [0.6,0.8,0.6,0.53,0.65,0.52,0.5],
        [0.6,0.81,0.6,0.54,0.67,0.54,0.5],
        [0.6,0.83,0.6,0.57,0.7,0.55,0.5],
        [0.6,0.84,0.6,0.58,0.71,0.57,0.5],
        [0.6,0.85,0.6,0.58,0.75,0.61,0.5],
        [0.6,0.86,0.6,0.63,0.77,0.61,0.5],
        [0.6,0.87,0.6,0.65,0.94,0.76,0.5],
        [0.6,0.92,0.6,0.7,0.96,0.77,0.5],
        [0.6,0.94,0.8,0.78,0.96,0.79,0.75],
        [0.8,0.95,0.8,0.82,0.96,0.85,0.75],
        [0.95,0.96,0.8,0.83,1,0.88,0.75],
        [0.95,0.97,0.8,0.84,1,0.98,0.75],
        [0.95,0.97,0.8,0.84,1,0.98,0.75],
        [0.95,0.99,0.8,0.85,1,0.98,0.75],
        [0.95,1,0.8,0.88,1,1,0.75],
        [0.95,1,0.8,0.88,1,1,0.75],
        [0.95,1,0.8,0.95,1,1,0.75],
        [0.97,1,0.8,0.99,1,1,1],
        [0.99,1,0.8,1,1,1,1],
        [1,1,0.8,1,1,1,1]
    ]


    deltaT = 10 # time period sizes

    finalTime = time[-1] *deltaT # in hours

    productmax_disrupted = np.zeros((len(time), len(site)))
    for t in range(0,42,1):
        for l in m.site:
            if disrupted[l] == 0:
                productmax_disrupted[t,l] = UB[l]
            else:
                productmax_disrupted[t,l] = recovery[t][l] * UB[l]


    choosesite = np.zeros((len(time), len(site)))
    for t in range(0,42,1):
        for l in m.site:
            if productmax_disrupted[t,l] < LB:
                choosesite[t,l] = 0
            else:
                choosesite[t,l] = sites_chosen[l]
    #================================================================================================================
        #*                                                 Variables
    #================================================================================================================

    # continuous variables

    # production-related variables that could change as a result of a disruption

    m.production = Var(m.time, m.site, domain = NonNegativeReals, initialize = 25000, doc = 'Amount of product made in site l at time t')
    m.netproduct = Var(m.time,m.city, domain = NonNegativeReals, initialize = 25000, doc = 'Amount of product received by city i at time t')
    m.productship = Var(m.time, m.site, m.city, domain = NonNegativeReals, initialize = 25000, doc = 'Amount of product shipped from site l to city i at time t')
    m.biomassused = Var(m.time, m.site, bounds = (0,250000), initialize = 25000, doc = 'amount of biomass used for production in site l at time t')
    m.biomassship = Var(m.time, m.site, m.city, domain = NonNegativeReals, initialize = 25000, doc = 'amount of biomass shipped from city i to site l at time t')

    # economic variables
    m.annualsales = Var(m.time, m.site, domain = NonNegativeReals, initialize = 2000000, doc = 'annual sales from site l given production levels at time t')
    m.fixedcost = Var(m.time, m.site, bounds = (0,100000000), doc = 'fixed capital investment')
    m.annualfixedcost = Var(m.time, m.site, domain = NonNegativeReals, doc = 'annualized fixed capital investment')
    m.opex = Var(m.time, m.site, domain = NonNegativeReals, initialize = 300, doc = 'operational expenses')
    m.profit = Var(m.time, m.site, domain = NonNegativeReals, initialize = 300, doc = 'annual net profit')

    #================================================================================================================
        #*                                                 Constraints
    #================================================================================================================

    # finance calculations

    m.Sales = ConstraintList(doc = 'calculate annual sales per site')
    for l in m.site:
        for t in m.time:
            m.Sales.add(m.annualsales[t,l] == Cproduct * m.production[t,l])

    m.fixedcapital = ConstraintList(doc = 'calculate fixed capital per site')
    for l in m.site:
        for t in m.time:
            m.fixedcapital.add(m.fixedcost[t,l] == 10**6 * (m.biomassused[t,l]/1000)**0.84 * 0.16 * 6)

    m.annualfixedcapital = ConstraintList(doc = 'annualize fixed capital per site')
    for l in m.site:
        for t in m.time:
            m.annualfixedcapital.add(m.annualfixedcost[t,l] == m.fixedcost[t,l]/lifetime)

    m.operatingcost = ConstraintList(doc = 'calculate OPEX per site')
    for l in m.site:
        for t in m.time:
            m.operatingcost.add(m.opex[t,l] == (Cbiomass * m.biomassused[t,l]) + sum(Cutilities[u] * u_perbiomass[u] * m.biomassused[t,l] for u in m.utility) + (sum(Cbiomasstransport * m.biomassship[t,l,i] * distance[l][i] for i in m.city) + sum(Cproducttransport * m.productship[t,l,i] * distance[l][i] for i in m.city)))

    m.annualprofit = ConstraintList(doc = 'calculate annual net profit per site')
    for l in m.site:
        for t in m.time:
            m.annualprofit.add(m.profit[t,l] == (m.annualsales[t,l] - m.opex[t,l] - m.annualfixedcost[t,l]) * (1-tax) + m.annualfixedcost[t,l])

    m.sizebounds = ConstraintList(doc = 'upper and lower bounds on site capacity')
    for l in m.site:
        for t in m.time:
            m.sizebounds.add(m.production[t,l] >= LB * choosesite[t][l])
            m.sizebounds.add(m.production[t,l] <= productmax_disrupted[t][l] * choosesite[t][l])

    # feasibility constraints

    m.biomassLimit = ConstraintList(doc = 'biomass mass balance around city i')
    for i in m.city:
        for t in m.time:
            m.biomassLimit.add(sum(m.biomassship[t,l,i] for l in m.site) <= biomass_max[i])

    m.biomassShipment = ConstraintList(doc = 'biomass mass balance around site l')
    for l in m.site:
        for t in m.time:
            m.biomassShipment.add(m.biomassused[t,l] == sum(m.biomassship[t,l,i] * path_exist[l][i] for i in m.city))

    m.convert = ConstraintList(doc = 'conversion rate between biomass and product')
    for l in m.site:
        for t in m.time:
            m.convert.add(m.production[t,l] == m.biomassused[t,l]/conversion)

    m.productShipment = ConstraintList(doc = 'product mass balance around site l')
    for l in m.site:
        for t in m.time:
            m.productShipment.add(m.production[t,l] == sum(m.productship[t,l,i] * path_exist[l][i] for i in m.city))

    m.productLimit = ConstraintList(doc = 'product mass balance around city i')
    for i in m.city:
        for t in m.time:
            m.productLimit.add(product_max[i] >= sum(m.productship[t,l,i] for l in m.site))

    #================================================================================================================
        #*                                                 Objective
    #================================================================================================================


    m.obj = Objective(expr = (sum(m.profit[t,l] for t in m.time for l in m.site))/finalTime, sense=maximize, doc = 'objective: maximize steady-state profit')

    result = SolverFactory('gams', solver= 'BARON').solve(m)

# #generate a gif to show how things progress over time

#     # make the graphs at each time point
#     def draw_solution(m,result,t):
#         dot = Digraph(engine='neato',filename='time {}'.format(t), format='png')
#         #first we make the nodes
#         for i in m.city:
#             dot.node("City {}".format(i),shape='box')
#         for l in m.site:
#             dot.node("Site {}".format(l),shape='circle')
#         #then we make the edges for the 3 cities
#         for i in m.city:
#             for j in m.city:
#                 dot.edge("City {}".format(i),"City {}".format(j),dir='none',len="{}".format(shortdistance[i][j]),style='invis')

#         #now we make the edges for the sites
#         for i in m.city:
#             for l in m.site:
#                 dot.edge("City {}".format(i),"Site {}".format(l),dir='none',len="{}".format(shortdistance[l][i]),style='invis')
#         #edges for supply lines
#         for i in m.city:
#             for l in m.site:
#                 if m.biomassship[t,l,i].value != 0:
#                     flow = round(m.biomassship[t,l,i].value)
#                     dot.edge("City {}".format(i),"Site {}".format(l),len="{}".format(shortdistance[l][i]),color='red',label=(str(flow) + " ton/y RDF") if flow > 0 else '')
#         #edges for demand lines
#         for i in m.city:
#             for l in m.site:
#                 if m.productship[t,l,i].value != 0:
#                     flow = round(m.productship[t,l,i].value)
#                     dot.edge("Site {}".format(l),"City {}".format(i),len="{}".format(shortdistance[l][i]),color='green',label=(str(flow) + " ton/y MeOH") if flow > 0 else '')
#         dot.attr(label='time {} * 10 seconds'.format(t))
#         return dot

#     # save image files for every time point
#     filenames = []
#     filenames2 = []
#     for t in m.time:
#         draw_solution(m,result,t).render()
#         filename = 'time {}.png'.format(t)
#         filename2 = 'time {}'.format(t)
#         filenames2.append(filename2)
#         filenames.append(filename)

#     # make the gif
#     import imageio.v2 as imageio
#     import os

#     with imageio.get_writer('mygif.gif', mode='I', duration=0.5, loop=1) as writer:
#         for filename in filenames:
#             image = imageio.imread(filename)
#             writer.append_data(image)
    
#     # delete all the individual files to make this cleaner
#     for filename in set(filenames):
#         os.remove(filename)
#     for filename2 in set(filenames2):
#         os.remove(filename2)
    

    # extract profit values into an array

    fetch_profit = np.zeros((len(time), len(site)))
    for t in m.time:
        for l in m.site:
            fetch_profit[t][l] = m.profit[t,l].value

    return fetch_profit

#================================================================================================================
    #*                                                 Resilience Math
#================================================================================================================
# calculate resilience of system and of node outside the Pyomo environment

profit = scenarioModel()

city = ["A","B","C"]
site = ["A","B","C","A+B","B+C","A+C","A+B+C"]
time = np.arange(0,42,1)
timenext = np.arange(1,42,1)
deltaT = 10
finalTime = deltaT*time[-1]

cityset = range(len(city))
timenextset = range(len(timenext))
siteset = range(len(site))

noderes = np.zeros(len(site))

for l in siteset:
    noderes[l] = (sum(deltaT * 0.5 * (profit[t][l] + profit[t-1][l]) for t in timenextset))/(profit[len(time)-1][l] * finalTime)

systemres = np.zeros(1)

systemres = (sum(deltaT * 0.5 * (sum(profit[t][l] for l in siteset) + sum(profit[t-1][l] for l in siteset)) for t in timenextset))/(finalTime * sum(profit[len(time)-1][l] for l in siteset))

# plot profit over time for the system
x = time
y0 = np.zeros(len(time))
for i in time:
    y0[i] = sum(profit[i][l] for l in siteset)

plt.plot(x,y0)
plt.title('System profit over time')
plt.xlabel('Time')
plt.ylabel('System profit [$]')
plt.show()


print('The system resilience is ', systemres)
print('The node resiliences are ', noderes)
print('The steady-state system profit is ', sum(profit[len(time)-1][l] for l in siteset))

# %%

