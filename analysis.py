#%%
#!/usr/bin/env python3

"""Analysis the output from the energy systems MILP. 
Input can be provided as .pkl files
Plotting capabilities include:

1. Material, energy and capital flows 
2. Share of hydrogen production Blue vs Green
3. Evolution of LCOH under different cost scenarios
4. Interpolated hydrogen production and inventory 
5.
"""


__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "R. Cory Allen",  "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "1.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

import pandas as pd
import numpy as np
import datetime as datetime
from datetime import date
import random
import pickle as pkl
import csv
from itertools import product
import matplotlib 
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
import squarify 
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.ticker as ticker
import plotly.graph_objects as go
import matplotlib.patches as mpatches
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from scipy.optimize import curve_fit
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
from scipy.stats import zscore


# files = ['MASTER_CMA_NG4o5_CL20']#, 'MASTER_CMA_NG4o5_CL30', 'MASTER_CMA_NG4o5_CL40', 'MASTER_CMA_NG4o5_CL50']
# files = ['CX_C_NG4o5_CL5', 'CX_C_NG4o5_CL10', 'CX_C_NG4o5_CL15', 'CX_C_NG4o5_CL20', 'CX_C_NG4o5_CL25', 'CX_C_NG4o5_CL30', 'CX_C_NG4o5_CL35', \
#     'CX_C_NG4o5_CL40', 'CX_C_NG4o5_CL45', 'CX_C_NG4o5_CL50', 'CX_C_NG4o5_CL365']

# files = ['CX_C_NG4o5_CL50', 'CX_C_NG4o5_CL45', 'CX_C_NG4o5_CL40', 'CX_C_NG4o5_CL35', 'CX_C_NG4o5_CL30', 'CX_C_NG4o5_CL25', 'CX_C_NG4o5_CL20', \
#     'CX_C_NG4o5_CL15', 'CX_C_NG4o5_CL10', 'CX_C_NG4o5_CL5', ]

# red_list = [5, 10,11,12,13,14,15,16,17,18,19,20, 21, 22, 23, 24, 25, 30, 40, 50, 70]

# red_list = np.arange(2, 52, 2)

# files = ['CX_C_CL' + str(i) for i in red_list]

# files = ['CX_C_NG4o5_CL20']
# files = ['F_CX_C_CL20', 'V_CX_C_CL20']
# files = ['V_CX_C_CL20']
# files = ['CX_M_CL20']
# files = ['BCX_M_CL20_CO20']

# files = ['BCX_M_CL20_CO20o05', 'BCX_M_CL20_CO20o1', 'BCX_M_CL20_CO20o15', \
#     'BCX_M_CL20_CO20o2', 'BCX_M_CL20_CO20o25', 'BCX_M_CL20_CO20o5'] 

# full = ['CX_C_CL365']
# with open('CX_C_CL365.pkl', 'rb') as f_: full = pkl.load(f_)
# files = ['cs_a_sc23_cd0']
# files = ['cs_m_sc23_cd0']
files = ['base_case']



DATA = []
for data_ in files: 
    with open(data_ + '.pkl', 'rb') as f_: locals()[data_] = pkl.load(f_)
    DATA.append(locals()[data_])
    # days = int(data_.split("_CL",1)[1])

H = np.arange(0,24)#Time (t)
iter_ = 0
for DATA_ in DATA:
    iter_ +=1
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()] 
    if iter_ == 1:
        scenario_ = SCENARIO[0]
        I = [i for i in DATA_[scenario_][0]['Net_P']['HO'].keys()]
for DATA_ in DATA:
    YEAR = [year_ for year_ in DATA_[SCENARIO[0]].keys()] 
    
# D = np.arange(1, days)#Seasons (d) days in this case
D = np.arange(1, 20)#Seasons (d) days in this case

# YEAR = np.arange(0,10)
METRIC = ['Total', 'Net_P', 'Net_S', 'Sch_P', 'Sch_S']


conv = pd.read_csv('conversion.csv', index_col = 0)
conv = conv.dropna(axis = 'rows')
conv = conv.transpose()
dict_conversion  = conv.to_dict()


# I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'AKE', 'SMR', 'DAC', 'MEFC', 'EOR', 'AQoff_DAC', 'AQoff_SMR']
#Only blue hydrogen 
# I = ['LiI_c', 'LiI_d', 'CAES_c', 'CAES_d', 'PSH_c', 'PSH_d', 'PV', 'WF', 'SMRH', 'H2_C_c'\
#     , 'H2_C_d',  'H2_L_c', 'H2_L_d', 'EOR', 'AQoff_SMR', 'H2_Sink1', 'H2_Sink2' ] #AQoff_DAC, MEFC, AKE, DAC
#Only green hydrogen
# I = [LiI_c, LiI_d, CAES_c, CAES_d, PSH_c, PSH_d, PV, WF, AKE,  H2_C_c, H2_C_d,  H2_L_c, H2_L_d, EOR,  H2_Sink1, H2_Sink2 ] #AQoff_DAC, MEFC, AKE, DAC, SMRH, AQoff_SMR



I_labels_ = {
    'long':{
        'LiI_c' :  'Lithium -ion battery',
        'CAES_c': 'Compressed air energy storage (CAES)',
        'PSH_c': 'Pumped storage hydropower (PSH)',
        'PV': 'Solar photovoltaics (PV) array',
        'WF': 'Wind mill array',
        'AKE': 'Alkaline water electrolysis (AWE)',
        'SMRH': 'Steam methane reforming + CCUS',
        'H2_C_c': 'Hydrogen local storage (Liquefied)',
        'H2_L_c': 'Hydrogen geological storage',
        'MEFC': 'Catalytic methanol production',
        'DAC': 'Direct air capture',
        'EOR': 'CO2-Enhanced oil recovery',
        'AQoff_SMR': 'Offshore aquifer CO2 sequestration (SMR)',
        'AQoff_DAC': 'Offshore aquifer CO2 sequestration (DAC)',
        'AQoff': 'Offshore aquifer CO2 sequestration',
        'H2_Sink1': 'Blue Hydrogen production',
        'H2_Sink2': 'Green Hydrogen production',
        'ASMR' : 'Small modular nuclear reactor',
        'Power_dummy': 'Power sink'
    },
    'short':{
        'LiI_c' :  'Li-ion battery',
        'CAES_c': 'CAES',
        'PSH_c': 'PSH',
        'PV': 'PV',
        'WF': 'WF',
        'AKE': 'AWE',
        'SMRH': 'SMR + CC',
        'H2_C_c': 'H2 - local',
        'H2_L_c': 'H2 - geological',
        'MEFC': 'MefCO2',
        'DAC': 'DAC',
        'EOR': 'CO2-EOR',
        'AQoff_SMR': 'Offshore aquifer CO2 sequestration (SMR)',
        'AQoff_DAC': 'Offshore aquifer CO2 sequestration (DAC)',
        'AQoff': 'Offshore aquifer',
        'H2_Sink1': 'Blue H2',
        'H2_Sink2': 'Green H2',
        'ASMR' : 'Nuclear SMR',
        'Power_dummy': 'Power sink'
    }
    
}

J_labels_ = {
    'long':
        {
        'Charge': 'Battery energy storage (MW)',
        'Air_C': 'CAES energy storage (MW)',
        'H2O_E': 'PSH energy storage (MW)',
        'Power': 'Renewable power generated',
        'H2_C': 'Hydrogen - Local storage',
        'H2_L': 'Hydrogen - Geological storage',
        'H2_B': 'Blue hydrogen',
        'H2_G': 'Green hydrogen',
        'H2O': 'Water',
        'H2': 'Hydrogen', 
        'Solar': 'Solar Power',
        'Wind': 'Wind Power',
        'O2': 'Oxygen',
        'CH4': 'Methane',
        'CO2': 'Carbon dioxide',
        'CO2_DAC': 'Carbon dioxide - captured',
        'CO2_AQoff': 'Carbon dioxide - sequestered',
        'CO2_EOR': 'Carbon dioxide - EOR',
        'CH3OH': 'Methanol',
        'Power_Gr': 'Grid electricity',
        'Uranium': 'Uranium',
        'Lithium': 'Lithium'        
                
        },
    'short':
        {
        'Charge': 'Battery energy storage (MW)',
        'Air_C': 'CAES energy storage (MW)',
        'H2O_E': 'PSH energy storage (MW)',
        'Power': 'Renewable power generated',
        'H2_C': 'Hydrogen - Local storage',
        'H2_L': 'Hydrogen - Geological storage',
        'H2_B': 'Blue hydrogen',
        'H2_G': 'Green hydrogen',
        'H2O': 'Water',
        'H2': 'Hydrogen', 
        'Solar': 'Solar Power',
        'Wind': 'Wind Power',
        'O2': 'Oxygen',
        'CH4': 'Methane',
        'CO2': 'Carbon dioxide',
        'CO2_DAC': 'Carbon dioxide - captured',
        'CO2_AQoff': 'Carbon dioxide - sequestered',
        'CO2_EOR': 'Carbon dioxide - EOR',
        'CH3OH': 'Methanol',
        'Power_Gr': 'Grid electricity',
        'Uranium': 'Uranium',
        'Lithium': 'Lithium'                
        }
}

# I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'AKE', 'SMRH', 'DAC', 'MEFC', 'EOR', 'AQoff_DAC', 'AQoff_SMR', 'H2_C_c', 'H2_C_d', 'H2_L_c', 'H2_L_d' ]
# I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'AKE', 'SMRH', 'DAC', 'MEFC', 'EOR', 'AQoff_DAC', 'AQoff_SMR', 'H2_C_c', 'H2_C_d', 'H2_L_c', 'H2_L_d' ]
#%%

demand = [50, 100, 200, 400, 800]
year = [2022, 2023, 2024, 2025, 2026]

fig, ax = plt.subplots(figsize = (8,4))
    
ax.tick_params(axis = 'both', labelsize = 16)
ax.set_xlabel('Year', fontsize = 16)
ax.set_ylabel('[US tons/day]', fontsize = 16)
ax.set_xticks(year)    
ax.plot(year, demand, alpha = 0.7, color = 'seagreen')
plt.grid(alpha = 0.3)
plt.title('Daily hydrogen demand', fontsize = 16)
plt.tight_layout()
plt.savefig("h2demand.png", dpi=1200)
plt.show()





#%%
year_ = 4
LCOH, CO2_total = [], []
for DATA_ in DATA:
    
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    for scenario_ in SCENARIO:
        LCOH.append(DATA_[scenario_][year_]['Total']['HO']['LCOH'])
        CO2_total.append((4503196.905825601 - DATA_[scenario_][year_]['Total']['HO']['CO2_total'])/4503196.905825601)
CO2_total.sort(reverse = True)
fig, ax = plt.subplots(figsize = (10,7))
    
ax.tick_params(axis = 'both', labelsize = 16)
ax.set_xlabel('Emission compared to base case (%)', fontsize = 16)
ax.set_ylabel('LCOH', fontsize = 16)
    
ax.plot(CO2_total,LCOH)
plt.title('Cost of emission reduction (illustrative)', fontsize = 16)
plt.show()



#%%

for data in  DATA:
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    for scenario in SCENARIO:
        # y = [data[scenario][year]['Total']['HO']['LCOH'] for year in range(5)]
        y = [data[scenario][year]['Total']['HO']['CO2_total'] for year in range(5)]
        
        year = [2022 + i for i in range(5)]
    fig, ax = plt.subplots(figsize = (10,8))
    ax.bar(year, y)
    # ax.set_ylim([0,3])
    plt.show()

#%%




def error(DATA:list):
    iter_ = 0
    x, y , z= [], [], []
    fig, ax = plt.subplots(figsize = (10,6))
    ax1 = ax.twinx()
    for DATA_ in DATA:
        y_ = 100*(full['Conservative'][0]['Total']['HO']['Objective'] - DATA_['Conservative'][0]['Total']['HO']['Objective'])\
            / full['Conservative'][0]['Total']['HO']['Objective']
        z_ = -100*(full['Conservative'][0]['Total']['HO']['comp_time'] - DATA_['Conservative'][0]['Total']['HO']['comp_time'])\
            / full['Conservative'][0]['Total']['HO']['comp_time']
        # z_ = 100*DATA_['Conservative'][0]['Total']['HO']['comp_time']/full['Conservative'][0]['Total']['HO']['comp_time']
        
        ax.scatter(red_list[iter_], y_, color = 'red', marker = '*')
        # ax.set_ylim(0, 10)
        
        # ax.xaxis.set_ticks_position('both')
        # ax.yaxis.set_ticks_position('both')     
        
        x.append(red_list[iter_])
        y.append(y_)


        ax1.scatter(red_list[iter_], z_, color = 'blue', marker = 'x')
        # ax1.xaxis.set_ticks_position('both')
        # ax1.yaxis.set_ticks_position('both')    
        # ax1.set_ylim(-100, -85)
        z.append(z_)
        iter_ +=1
        # if iter_ == 10:
        #     z_annot = -100*(full['Conservative'][0]['Total']['HO']['comp_time'] - DATA_['Conservative'][0]['Total']['HO']['comp_time'])\
        #     / full['Conservative'][0]['Total']['HO']['comp_time'] 
        #     y_annot = 100*(full['Conservative'][0]['Total']['HO']['Objective'] - DATA_['Conservative'][0]['Total']['HO']['Objective'])\
        #     / full['Conservative'][0]['Total']['HO']['Objective']
        
        
    ax.plot(x,y, color = 'red', linestyle = 'dashed', alpha = 0.4)
    ax1.plot(x,z, color = 'blue', alpha = 0.4)
    
    ax.set_xlabel('Number of representative days', fontsize = 16)
    ax.set_ylabel('Objective error [%] (*)', fontsize = 16)
    ax1.set_ylabel('Computation time [%] (x)', fontsize = 16)
    
    ax.tick_params(axis = 'y', labelsize = 16, colors = 'red')
    ax1.tick_params(axis = 'y', labelsize = 16, colors = 'blue')
    ax.tick_params(axis = 'x', labelsize = 16)
    
    ax1.spines['left'].set_color('red')
    ax1.spines['right'].set_color('blue')

    
    # plt.grid(alpha = 0.5)
    plt.title('Comparison to full scale model', fontsize = 18)
    # ax.plot([20], [8], marker='o', color = 'blue')  
    # ax.annotate('(' + str('{:.2f}'.format(y_annot)) + '%,' + str('{:.2f}'.format(z_annot)) + '%)',
    #             xy=(20, 8.1), xycoords='data',
    #             xytext=(-15, 25), textcoords='offset points',
    #             arrowprops=dict(facecolor='blue', shrink=0.05),
    #             horizontalalignment='left', verticalalignment='bottom', fontsize = 15)

    plt.show()
    return
error(DATA)



#%%

def comp_time(DATA:list):
    iter_ = 0
    x, y = [], []
    fig, ax = plt.subplots(figsize = (10,6))
    for DATA_ in DATA:
        y_ = -100*(full['Conservative'][0]['Total']['HO']['comp_time'] - DATA_['Conservative'][0]['Total']['HO']['comp_time'])/ full['Conservative'][0]['Total']['HO']['comp_time'] 
        ax.scatter(red_list[iter_], y_)
        x.append(red_list[iter_])
        y.append(y_)
        iter_ +=1

    plt.plot(x,y)
    # ticks = np.arange(50,0,-5)
    # ticks = [si) for i in ticks]
    plt.xticks(x, fontsize = 16)
    plt.yticks(fontsize = 16)
    plt.xlabel('Number of representative days', fontsize = 16)
    plt.ylabel('Reduction in computation time [%]', fontsize = 16)
    
    plt.show()
    return
comp_time(DATA)


#%%

def long_graph(DATA_:dict):
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()] 
    fig, ax = plt.subplots(figsize = (10,8))
    for scenario_ in SCENARIO:
        for i_ in ['WF']:
            input_, year = [], []
            for year_ in YEAR:
                # input_.append(DATA_[scenario_][year_]['Net_P']['HO'][i_]['Cap_P'])
                # input_.append(DATA_[scenario_][year_]['Net_P']['HO'][i_]['Land'])
                
                input_.append(DATA_[scenario_][year_]['Material']['HO'][i_]['Lithium']/500)
                year.append(year_+ 2022)
            ax.tick_params(axis = 'both', labelsize = 16)
            ax.set_xlabel('Year', fontsize = 16)
            ax.set_ylabel('Lithium consumed (MMT) by year', fontsize = 16)
            print(input_)
            ax.bar(year, input_)
            ax.set_xticks(year)
            plt.title('System wide Lithium use (illustrative)', fontsize = 16)
            # plt.title(I_labels_['short'][i_])
            
            plt.show()

for DATA_ in DATA:
    p = long_graph(DATA_)


#%%       
# years = [0, 1, 2, 3, 4]
# years = np.arange(0,2)

# colors = ['teal', 'lightseagreen', 'blue', 'green', ]

def ng_sensitivity(DATA:list, years:list):
    """illustrates the sensitivity of hydrogen cost to 
    natural gas prices

    Args:
        DATA (list): List with dictionaries with case study data
        years (list): list of years for subplot1, 
        limited because model doesnot converge for extreme cases
    """
    fig, ax = plt.subplots(1,2,figsize = (12,6))
    # .title('Sensitivity of hydrogen cost to natural gas price', fontsize = 14)
    
    iter2_ = 0
    for year_ in years:
        if year_ <5:
            ng_price = [2,4,6,8,10] 
            iter_ = 0
            line = []
            for DATA_ in DATA:
                
                Cost = []
                SCENARIO = [scenario_ for scenario_ in DATA_.keys()] 
                for scenario_ in SCENARIO:
                    div_ = sum(DATA_[scenario_][year_]['Net_P']['HO'][k]['P_annual'] for k in ['H2_Sink1', 'H2_Sink2'])
                    Cost.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/div_)
                line.append(Cost[0]) 
                ax[0].scatter(ng_price[iter_], Cost, color = 'teal', marker = '.')
                iter_+= 1
                # ax.xaxis.set_ticks_position('both')
                # ax.yaxis.set_ticks_position('both')
            ax[0].plot(ng_price, line, color =  (0,0.5+iter2_*0.05,0.5-iter2_*0.05))
            
            ax[0].annotate(str(year_ + 2022), (ng_price[-1]+ 0.05, line[-1]+ 0.06), verticalalignment = 'top', horizontalalignment = 'center'\
                        , fontsize = 10, color =  (0,0.5+iter2_*0.05,0.5-iter2_*0.05))
            iter2_ += 1
        else:
            iter_ = 0
            line = []
            ng_price = [4,6,8]             
            for DATA_ in DATA[1:4]:
                Cost = []
                SCENARIO = [scenario_ for scenario_ in DATA_.keys()] 
                for scenario_ in SCENARIO:
                    div_ = sum(DATA_[scenario_][year_]['Net_P']['HO'][k]['P_annual'] for k in ['H2_Sink1', 'H2_Sink2'])
                    Cost.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/div_)
                line.append(Cost[0]) 
                ax[0].scatter(ng_price[iter_], Cost, color = 'teal', marker = '.')
                iter_+= 1
                # ax.xaxis.set_ticks_position('both')
                # ax.yaxis.set_ticks_position('both')
            ax[0].plot(ng_price, line, color =  (0,0.5+iter2_*0.05,0.5-iter2_*0.05))
            
            ax[0].annotate(str(year_ + 2022), (ng_price[-1]+ 0.05, line[-1]+ 0.06), verticalalignment = 'top', horizontalalignment = 'center'\
                        , fontsize = 10, color =  (0,0.5+iter2_*0.05,0.5-iter2_*0.05))
            iter2_ += 1
            
    ng_price = [2,4,6,8,10]     
    iter3_ = 0    
    iter4_ = 0
    for DATA_ in DATA:
        # if iter4_ == 0:
        Cost, X_ = [], []
        years = np.arange(0,5)
        for year_ in years:
            div_ = sum(DATA_[scenario_][year_]['Net_P']['HO'][k]['P_annual'] for k in ['H2_Sink1', 'H2_Sink2'])
            Cost.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/div_)
            X_.append(int(year_ + 2022))
        ax[1].scatter(X_, Cost, color = 'teal', marker = '.')
        ax[1].plot(X_, Cost, color =  (0,0.5+iter4_*0.1,0.5-iter4_*0.1))
        ax[1].annotate(ng_price[iter4_], (2022 - 0.14, Cost[0]+ 0.04), verticalalignment = 'top', horizontalalignment = 'center'\
                    , fontsize = 12, color =  (0,0.5+iter4_*0.1,0.5-iter4_*0.1))
        # elif iter4_ ==4:
        #     Cost, X_ = [], []
        #     years = np.arange(0,5)
        #     for year_ in years:
        #         div_ = sum(DATA_[scenario_][year_]['Net_P']['HO'][k]['P_annual'] for k in ['H2_Sink1', 'H2_Sink2'])
        #         Cost.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/div_)
        #         X_.append(int(year_ + 2022))
        #     ax[1].scatter(X_, Cost, color = 'teal', marker = '.')
        #     ax[1].plot(X_, Cost, color =  (0,0.5+iter4_*0.1,0.5-iter4_*0.1))
        #     ax[1].annotate(ng_price[iter4_], (2022 - 0.12, Cost[0]+ 0.02), verticalalignment = 'top', horizontalalignment = 'center'\
        #                 , fontsize = 12, color =  (0,0.5+iter4_*0.1,0.5-iter4_*0.1))
                 
        # else:     
        #     Cost, X_ = [], []
        #     years = np.arange(0,10)
        #     for year_ in years:
        #         div_ = sum(DATA_[scenario_][year_]['Net_P']['HO'][k]['P_annual'] for k in ['H2_Sink1', 'H2_Sink2'])
        #         Cost.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/div_)
        #         X_.append(int(year_ + 2022))
        #     ax[1].scatter(X_, Cost, color = 'teal', marker = '.')
        #     ax[1].plot(X_, Cost, color =  (0,0.5+iter4_*0.1,0.5-iter4_*0.1))
        #     ax[1].annotate(ng_price[iter4_], (2022 - 0.12, Cost[0]+ 0.02), verticalalignment = 'top', horizontalalignment = 'center'\
        #                 , fontsize = 12, color =  (0,0.5+iter4_*0.1,0.5-iter4_*0.1))
        iter4_ += 1
    
    ax[0].set_xticks(ng_price)
    ax[1].set_xticks(np.arange(2022,2027))

    
    x_line = [4]*16
    y_line = np.arange(2,3.6,0.1)
    ax[0].plot(x_line, y_line , '--', alpha = 0.8)
    ax[0].set_xlabel('Natural gas price [$/MMBtu]', fontsize = 14)
    ax[0].set_ylabel('LCOH [$\$/kg.H_{2}$]', fontsize = 14)
    ax[1].set_xlabel('Year', fontsize = 14)
    ax[1].set_ylabel('LCOH [$\$/kg.H_{2}$]', fontsize = 14)
    
    ax[0].set_ylim([2.0,3.5])
    ax[1].set_ylim([2.0,3.5])
    plt.suptitle('Sensitivity of LCOH to Natural gas prices', fontsize = 14)
    plt.savefig('natural_gas.jpeg', dpi = 200)
    plt.show()

ng_sensitivity(DATA,years)
        
#%%

def ng_var_fix(DATA_:dict, year_:float):
    """Compares capacity utilization for varying vs fixed natural gas prices

    Args:
        DATA_ (dict): containts output data for each year in the scenario
        year_ (float): year of choice to plot
    """
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    for scenario_ in SCENARIO:
        Green_H2, Blue_H2, X_ = ([] for _ in range(3))
        for h, d in product(H,D):
            green_ = DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink2'][h][d]['P']/(907.185)
            blue_ = DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink1'][h][d]['P']/(907.185)
            Green_H2.append(green_/(green_ + blue_))
            
            Blue_H2.append(blue_/(green_ + blue_))
        X_ = np.arange(0,len(Green_H2))    
        print(len(X_))
        print(len(Green_H2))
        print(len(Blue_H2))
        
        width = 0.8
        space = 0.2
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.bar(X_, Blue_H2, color= 'blue', label= 'Blue H2')
        ax.bar(X_, Green_H2, bottom= Blue_H2, color='green', label='Green H2')
        plt.title('Total hydrogen production under a ' + scenario_ + ' cost scenario', fontsize=20)
        plt.xlabel('Year', fontsize=20)
        plt.ylabel('US tonnes', fontsize=20)
        plt.legend(fontsize=20)
        plt.xticks(fontsize= 16)
        plt.yticks(fontsize= 16)
        # ax.set_xticks(X_)
        plt.show()    
    return       

for DATA_ in DATA:
    ng_var_fix(DATA_, 4)
    


#%%   
def full_pie_grid():
    """Plot a pie grid with three levels:
    1. power contribution over the year
    2. Carbon dioxide contribution
    
    3. hydrogen contribution 
    OR
    3. miles contribution
    """


    for DATA_ in DATA:
        SCENARIO = [scenario_ for scenario_ in DATA_.keys()] 
        for scenario_ in SCENARIO:
            Wind, Solar, Green_H2, Blue_H2, Loc_H2, Geo_H2, SMRH, EOR, \
                Miles_MEOH, Miles_H2, Miles_Pow, X_,\
                    Total_miles, Total_CO2, Total_H2_p, Total_H2_d, Total_Pow,\
                        temp_Total_miles, temp_Total_CO2, temp_Total_H2, temp_Total_Pow, \
                            temp_Wind, temp_Solar = ([] for _ in range(23))
            for year_ in YEAR:
                
                Wind.append(DATA_[scenario_][year_]['Net_P']['HO']['WF']['P_annual'])
                Solar.append(DATA_[scenario_][year_]['Net_P']['HO']['PV']['P_annual'])

                Green_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual'])
                Blue_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual'])
                
                Loc_H2.append(DATA_[scenario_][year_]['Net_S']['HO']['H2_C']['S_annual'])
                Geo_H2.append(DATA_[scenario_][year_]['Net_S']['HO']['H2_L']['S_annual'])
                
                SMRH.append(DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']*dict_conversion['SMRH']['CO2_Vent'])
                EOR.append(DATA_[scenario_][year_]['Net_P']['HO']['EOR']['P_annual']*dict_conversion['EOR']['CO2_Vent'])
                
                Miles_MEOH.append(DATA_[scenario_][year_]['Net_S']['HO']['CH3OH']['Mile_annual'])
                Miles_H2.append(sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L'])) 
                Miles_Pow.append(DATA_[scenario_][year_]['Net_S']['HO']['Power']['Mile_annual'])
                
                Total_CO2.append(DATA_[scenario_][year_]['Net_S']['HO']['CO2_Vent']['S_annual'])
                Total_H2_d.append(sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['S_annual'] for i_ in ['H2_C', 'H2_L']))
                Total_H2_p.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i_]['P_annual'] for i_ in ['H2_Sink1', 'H2_Sink2']))
                
                Total_miles.append(sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L', 'Power', 'CH3OH']))
                Total_Pow.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i_]['P_annual'] for i_ in ['PV', 'WF']))
                             
                X_.append(int(year_ + 2022))

            
            Y1_ = [1]*len(X_)
            Y2_ = [2]*len(X_)
            Y3_ = [3]*len(X_)
            Y4_ = [4]*len(X_)
            Y5_ = [5]*len(X_)

            fig, ax = plt.subplots(figsize = (12, 8))

            for year_ in YEAR:
                            
                r1 = Wind[year_]/Total_Pow[year_]
                r2 = r1 + Solar[year_]/Total_Pow[year_]   
                x1 = np.cos(2 * np.pi * np.linspace(0, r1))
                y1 = np.sin(2 * np.pi * np.linspace(0, r1))
                xy1 = np.row_stack([[0, 0], np.column_stack([x1, y1])])
            
                x2 = np.cos(2 * np.pi * np.linspace(r1, r2))
                y2 = np.sin(2 * np.pi * np.linspace(r1, r2))
                xy2 = np.row_stack([[0, 0], np.column_stack([x2, y2])])
            
                plt.scatter(X_[year_], Y1_[year_], s  = 3000*Total_Pow[year_]/max(Total_Pow), marker = xy1, color = 'royalblue')
                plt.scatter(X_[year_], Y1_[year_], s = 3000*Total_Pow[year_]/max(Total_Pow), marker = xy2, color = 'gold')
                
                if Total_CO2[year_] ==0:
                    r3 = 0
                    r4 = r3 + 0
                else:    
                    r3 = SMRH[year_]/Total_CO2[year_]
                    r4 = r3 + EOR[year_]/Total_CO2[year_]   
                
                x3 = np.cos(2 * np.pi * np.linspace(0, r3))
                y3 = np.sin(2 * np.pi * np.linspace(0, r3))
                xy3 = np.row_stack([[0, 0], np.column_stack([x3, y3])])
            
                x4 = np.cos(2 * np.pi * np.linspace(r3, r4))
                y4 = np.sin(2 * np.pi * np.linspace(r3, r4))
                xy4 = np.row_stack([[0, 0], np.column_stack([x4, y4])])
            
                plt.scatter(X_[year_], Y2_[year_], s  = 3000*Total_CO2[year_]/max(Total_CO2), marker = xy3, color = 'cadetblue')
                plt.scatter(X_[year_], Y2_[year_], s = 3000*Total_CO2[year_]/max(Total_CO2), marker = xy4, color = 'slategrey')
                
                r5 = Blue_H2[year_]/Total_H2_p[year_]
                r6 = r5 + Green_H2[year_]/Total_H2_p[year_]   
                x5 = np.cos(2 * np.pi * np.linspace(0, r5))
                y5 = np.sin(2 * np.pi * np.linspace(0, r5))
                xy5 = np.row_stack([[0, 0], np.column_stack([x5, y5])])
            
                x6 = np.cos(2 * np.pi * np.linspace(r5, r6))
                y6 = np.sin(2 * np.pi * np.linspace(r5, r6))
                xy6 = np.row_stack([[0, 0], np.column_stack([x6, y6])])
            
                plt.scatter(X_[year_], Y3_[year_], s  = 3000*Total_H2_p[year_]/max(Total_H2_p), marker = xy5, color = 'blue')
                plt.scatter(X_[year_], Y3_[year_], s = 3000*Total_H2_p[year_]/max(Total_H2_p), marker = xy6, color = 'green')
                
                r7 = Loc_H2[year_]/Total_H2_d[year_]
                r8 = r7 + Geo_H2[year_]/Total_H2_d[year_]   
                x7 = np.cos(2 * np.pi * np.linspace(0, r7))
                y7 = np.sin(2 * np.pi * np.linspace(0, r7))
                xy7 = np.row_stack([[0, 0], np.column_stack([x7, y7])])
            
                x8 = np.cos(2 * np.pi * np.linspace(r7, r8))
                y8 = np.sin(2 * np.pi * np.linspace(r7, r8))
                xy8 = np.row_stack([[0, 0], np.column_stack([x8, y8])])
            
                plt.scatter(X_[year_], Y4_[year_], s  = 3000*Total_H2_d[year_]/max(Total_H2_d), marker = xy7, color = 'yellow')
                plt.scatter(X_[year_], Y4_[year_], s = 3000*Total_H2_d[year_]/max(Total_H2_d), marker = xy8, color = 'orange')

                
                r9 = Miles_MEOH[year_]/Total_miles[year_]
                r10 = r9 + Miles_H2[year_]/Total_miles[year_]
                r11 = r9 + r10 + Miles_Pow[year_]/Total_miles[year_]   
                   
                x9 = np.cos(2 * np.pi * np.linspace(0, r9))
                y9 = np.sin(2 * np.pi * np.linspace(0, r9))
                xy9 = np.row_stack([[0, 0], np.column_stack([x9, y9])])
            
                x10 = np.cos(2 * np.pi * np.linspace(r9, r10))
                y10 = np.sin(2 * np.pi * np.linspace(r9, r10))
                xy10 = np.row_stack([[0, 0], np.column_stack([x10, y10])])
                
                x11 = np.cos(2 * np.pi * np.linspace(r10, r11))
                y11 = np.sin(2 * np.pi * np.linspace(r10, r11))
                xy11 = np.row_stack([[0, 0], np.column_stack([x11, y11])])
            
                plt.scatter(X_[year_], Y5_[year_], s  = 3000*Total_miles[year_]/max(Total_miles), marker = xy9, color = 'firebrick')
                plt.scatter(X_[year_], Y5_[year_], s = 3000*Total_miles[year_]/max(Total_miles), marker = xy10, color = 'mediumseagreen')
                plt.scatter(X_[year_], Y5_[year_], s = 3000*Total_miles[year_]/max(Total_miles), marker = xy11, color = 'mediumturquoise')
                            
            # colors = ['royalblue', 'gold', 'cadetblue', 'slategrey', 'blue', 'green', 'yellow', 'orange', 'firebrick', 'olive', 'mediumturquoise']
            
            # labels = ['Wind', 'Solar', 'SMR+CC', 'EOR',  'Blue $H_{2}$', 'Green $H_{2}$', 'Local', 'Geological',  'Methanol(90%)', 'HFCV', 'EV']

            colors = ['firebrick', 'mediumseagreen', 'mediumturquoise', 'yellow', 'orange', 'blue', 'green', 'cadetblue', 'slategrey',  'royalblue', 'gold' ]
            
            labels = ['Methanol(90%)', 'HFCV', 'EV', 'Local', 'Geological', 'Blue $H_{2}$', 'Green $H_{2}$',   'SMR+CC', 'EOR', 'Wind', 'Solar',   ]

            
            patches = []
            for i in range(len(colors)):
                patches.append(mpatches.Patch(color=colors[i], label=labels[i]))
            
            plt.legend(handles= patches, bbox_to_anchor=(1.03, 1))
                # lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--') for c in colors]
                # plt.legend(lines, labels)
                
            # plt.scatter(X_, Y1_, s = Total_CO2, marker = xy2)
            
            #plt.scatter(X_, Y3_, s = Total_H2)#, marker = xy3)
            
            #plt.scatter(X_, Y4_, s= Total_H2)#, marker = xy4)
            plt.grid(alpha = 0.4)
            plt.xticks(X_, fontsize = 14)
            bars = ('Power', '$CO_{2}$ emission', '$H_{2}$ production', '$H_{2}$ dispense', 'Total miles')
            y_pos = [1, 2, 3, 4, 5, 0, 6]    
            plt.yticks(y_pos, bars,  fontsize='14', horizontalalignment='right')
            plt.xlabel('Year', fontsize = 14)
            plt.title('Trajectories for ' + scenario_.lower() +' cost scenario', fontsize = 14)
            x_line = [2027]*61
            y_line = np.arange(0,6.1,0.1)
            plt.plot(x_line, y_line , '--', alpha = 0.4, color = 'slateblue')
            plt.ylim([0.5,5.5])

            plt.annotate('End of term 1', (2027, 5.45), verticalalignment = 'top', horizontalalignment = 'center'\
                    , fontsize = 14, color = 'slateblue')

            plt.show()           
    return
plot_ = full_pie_grid()            

#%%

def h2_pie_grid():
    """Plot a pie grid with three levels:
    1. power contribution over the year
    2. Carbon dioxide contribution
    3. hydrogen contribution 
    OR
    3. miles contribution
    """


    for DATA_ in DATA:
        SCENARIO = [scenario_ for scenario_ in DATA_.keys()] 
        for scenario_ in SCENARIO:
            Wind, Solar, Green_H2, Blue_H2, Loc_H2, Geo_H2, SMRH, EOR, \
                Miles_MEOH, Miles_H2, Miles_Pow, X_,\
                    Total_miles, Total_CO2, Total_H2_p, Total_H2_d, Total_Pow,\
                        temp_Total_miles, temp_Total_CO2, temp_Total_H2, temp_Total_Pow, \
                            temp_Wind, temp_Solar = ([] for _ in range(23))
            for year_ in YEAR:
                
                Wind.append(DATA_[scenario_][year_]['Net_P']['HO']['WF']['P_annual'])
                Solar.append(DATA_[scenario_][year_]['Net_P']['HO']['PV']['P_annual'])

                Green_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual'])
                Blue_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual'])
                
                Loc_H2.append(DATA_[scenario_][year_]['Net_S']['HO']['H2_C']['S_annual'])
                Geo_H2.append(DATA_[scenario_][year_]['Net_S']['HO']['H2_L']['S_annual'])
                
                SMRH.append(DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']*dict_conversion['SMRH']['CO2_Vent'])
                EOR.append(DATA_[scenario_][year_]['Net_P']['HO']['EOR']['P_annual']*dict_conversion['EOR']['CO2_Vent'])
                
                Miles_MEOH.append(DATA_[scenario_][year_]['Net_S']['HO']['CH3OH']['Mile_annual'])
                Miles_H2.append(sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L'])) 
                Miles_Pow.append(DATA_[scenario_][year_]['Net_S']['HO']['Power']['Mile_annual'])
                
                Total_CO2.append(DATA_[scenario_][year_]['Net_S']['HO']['CO2_Vent']['S_annual'])
                Total_H2_p.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i_]['P_annual'] for i_ in ['H2_Sink1', 'H2_Sink2']))
                Total_H2_d.append(sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['S_annual'] for i_ in ['H2_C', 'H2_L']))
                Total_miles.append(sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L', 'Power', 'CH3OH']))
                Total_Pow.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i_]['P_annual'] for i_ in ['PV', 'WF']))
                             
                X_.append(int(year_ + 2022))

            
            Y1_ = [1]*len(X_)
            Y2_ = [2]*len(X_)
            Y3_ = [3]*len(X_)
            Y4_ = [4]*len(X_)
            Y5_ = [5]*len(X_)

            fig, ax = plt.subplots(figsize = (12, 8))

            for year_ in YEAR:
                            
                r1 = Wind[year_]/Total_Pow[year_]
                r2 = r1 + Solar[year_]/Total_Pow[year_]   
                x1 = np.cos(2 * np.pi * np.linspace(0, r1))
                y1 = np.sin(2 * np.pi * np.linspace(0, r1))
                xy1 = np.row_stack([[0, 0], np.column_stack([x1, y1])])
            
                x2 = np.cos(2 * np.pi * np.linspace(r1, r2))
                y2 = np.sin(2 * np.pi * np.linspace(r1, r2))
                xy2 = np.row_stack([[0, 0], np.column_stack([x2, y2])])
            
                plt.scatter(X_[year_], Y1_[year_], s  = 3000*Total_Pow[year_]/max(Total_Pow), marker = xy1, color = 'royalblue')
                plt.scatter(X_[year_], Y1_[year_], s = 3000*Total_Pow[year_]/max(Total_Pow), marker = xy2, color = 'gold')
                
                if Total_CO2[year_] ==0:
                    r3 = 0
                    r4 = r3 + 0
                else:    
                    r3 = SMRH[year_]/Total_CO2[year_]
                    r4 = r3 + EOR[year_]/Total_CO2[year_]   
                
                x3 = np.cos(2 * np.pi * np.linspace(0, r3))
                y3 = np.sin(2 * np.pi * np.linspace(0, r3))
                xy3 = np.row_stack([[0, 0], np.column_stack([x3, y3])])
            
                x4 = np.cos(2 * np.pi * np.linspace(r3, r4))
                y4 = np.sin(2 * np.pi * np.linspace(r3, r4))
                xy4 = np.row_stack([[0, 0], np.column_stack([x4, y4])])
            
                plt.scatter(X_[year_], Y2_[year_], s  = 3000*Total_CO2[year_]/max(Total_CO2), marker = xy3, color = 'cadetblue')
                plt.scatter(X_[year_], Y2_[year_], s = 3000*Total_CO2[year_]/max(Total_CO2), marker = xy4, color = 'slategrey')
                
                r5 = Blue_H2[year_]/Total_H2_p[year_]
                r6 = r5 + Green_H2[year_]/Total_H2_p[year_]   
                x5 = np.cos(2 * np.pi * np.linspace(0, r5))
                y5 = np.sin(2 * np.pi * np.linspace(0, r5))
                xy5 = np.row_stack([[0, 0], np.column_stack([x5, y5])])
            
                x6 = np.cos(2 * np.pi * np.linspace(r5, r6))
                y6 = np.sin(2 * np.pi * np.linspace(r5, r6))
                xy6 = np.row_stack([[0, 0], np.column_stack([x6, y6])])
            
                plt.scatter(X_[year_], Y3_[year_], s  = 3000*Total_H2_p[year_]/max(Total_H2_p), marker = xy5, color = 'blue')
                plt.scatter(X_[year_], Y3_[year_], s = 3000*Total_H2_p[year_]/max(Total_H2_p), marker = xy6, color = 'green')
                
                r7 = Loc_H2[year_]/Total_H2_d[year_]
                r8 = r7 + Geo_H2[year_]/Total_H2_d[year_]   
                x7 = np.cos(2 * np.pi * np.linspace(0, r7))
                y7 = np.sin(2 * np.pi * np.linspace(0, r7))
                xy7 = np.row_stack([[0, 0], np.column_stack([x7, y7])])
            
                x8 = np.cos(2 * np.pi * np.linspace(r7, r8))
                y8 = np.sin(2 * np.pi * np.linspace(r7, r8))
                xy8 = np.row_stack([[0, 0], np.column_stack([x8, y8])])
            
                plt.scatter(X_[year_], Y4_[year_], s  = 3000*Total_H2_d[year_]/max(Total_H2_d), marker = xy7, color = 'yellow')
                plt.scatter(X_[year_], Y4_[year_], s = 3000*Total_H2_d[year_]/max(Total_H2_d), marker = xy8, color = 'orange')

                
                # r9 = Miles_MEOH[year_]/Total_miles[year_]
                # r10 = r9 + Miles_H2[year_]/Total_miles[year_]
                # r11 = r9 + r10 + Miles_Pow[year_]/Total_miles[year_]   
                   
                # x9 = np.cos(2 * np.pi * np.linspace(0, r9))
                # y9 = np.sin(2 * np.pi * np.linspace(0, r9))
                # xy9 = np.row_stack([[0, 0], np.column_stack([x9, y9])])
            
                # x10 = np.cos(2 * np.pi * np.linspace(r9, r10))
                # y10 = np.sin(2 * np.pi * np.linspace(r9, r10))
                # xy10 = np.row_stack([[0, 0], np.column_stack([x10, y10])])
                
                # x11 = np.cos(2 * np.pi * np.linspace(r10, r11))
                # y11 = np.sin(2 * np.pi * np.linspace(r10, r11))
                # xy11 = np.row_stack([[0, 0], np.column_stack([x11, y11])])
            
                # plt.scatter(X_[year_], Y5_[year_], s  = 3000*Total_miles[year_]/max(Total_miles), marker = xy9, color = 'firebrick')
                # plt.scatter(X_[year_], Y5_[year_], s = 3000*Total_miles[year_]/max(Total_miles), marker = xy10, color = 'mediumseagreen')
                # plt.scatter(X_[year_], Y5_[year_], s = 3000*Total_miles[year_]/max(Total_miles), marker = xy11, color = 'mediumturquoise')
                            
            # colors = ['royalblue', 'gold', 'cadetblue', 'slategrey', 'blue', 'green', 'yellow', 'orange', 'firebrick', 'olive', 'mediumturquoise']
            
            # labels = ['Wind', 'Solar', 'SMR+CC', 'EOR',  'Blue $H_{2}$', 'Green $H_{2}$', 'Local', 'Geological',  'Methanol(90%)', 'HFCV', 'EV']

            colors = ['yellow', 'orange', 'blue', 'green', 'cadetblue', 'slategrey',  'royalblue', 'gold' ]
            
            labels = ['Local', 'Geological', 'Blue $H_{2}$', 'Green $H_{2}$',   'SMR+CC', 'EOR', 'Wind', 'Solar',   ]

            
            patches = []
            for i in range(len(colors)):
                patches.append(mpatches.Patch(color=colors[i], label=labels[i]))
            
            plt.legend(handles= patches, bbox_to_anchor=(1.03, 1))
                # lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--') for c in colors]
                # plt.legend(lines, labels)
                
            # plt.scatter(X_, Y1_, s = Total_CO2, marker = xy2)
            
            #plt.scatter(X_, Y3_, s = Total_H2)#, marker = xy3)
            
            #plt.scatter(X_, Y4_, s= Total_H2)#, marker = xy4)
            plt.grid(alpha = 0.4)
            plt.xticks(X_, fontsize = 14)
            bars = ('Power', '$CO_{2}$ emission', '$H_{2}$ production', '$H_{2}$ dispense')
            y_pos = [1, 2, 3, 4, 5, 0]    
            plt.yticks(y_pos, bars,  fontsize='14', horizontalalignment='right')
            plt.xlabel('Year', fontsize = 14)
            plt.title('Trajectories for ' + scenario_.lower() +' cost scenario', fontsize = 14)
            x_line = [2027]*61
            y_line = np.arange(0,6.1,0.1)
            plt.plot(x_line, y_line , '--', alpha = 0.4, color = 'slateblue')
            plt.ylim([0.5,4.5])

            plt.annotate('End of term 1', (2027, 4.45), verticalalignment = 'top', horizontalalignment = 'center'\
                    , fontsize = 14, color = 'slateblue')

            plt.show()           
    return
plot_ = h2_pie_grid()            
#%%
# YEAR = np.arange(0,10)
def h_cost_contr(DATA_:dict):
    """Provides a breakdown of the cost contribution
    in $/kg.H2

    Args:
        DATA_ (dict): contains results 
    """
    I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'AKE', 'SMRH', 'H2_C_c', 'H2_L_c', 'DAC', 'MEFC', 'EOR', 'AQoff_SMR']# 'AQoff_DAC',
    
    I2 = [ 'H2_C_c', 'H2_L_c', 'DAC', 'MEFC', 'EOR', 'AQoff_SMR']
    
    h2_list = ['H2_Blue', 'H2_Green']
    # h2_list = ['H2_Blue']
    
    
    df = pd.DataFrame(columns = I)
    df2 = pd.DataFrame(columns = ['Power System', 'Electrolysis', 'SMR + CC', 'Rest'])

    SCENARIO = [scenario_ for scenario_ in DATA_.keys()] 
    for scenario_ in SCENARIO:
        for year_ in YEAR:
            div_ = sum(DATA_[scenario_][year_]['Net_P']['HO'][k]['P_annual'] for k in h2_list)
            list_ = []
            for i in I:
                list_.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i][j] for j in ['Capex', 'Opex_fix', 'Opex_var'])/div_)
            # print(list_)
            
            df.loc[year_] = list_
        # view data
        df['Year'] = df.index
        df['AQoff'] = df['AQoff_SMR'] #+ df['AQoff_DAC']
        df['Rest'] = sum(df[i] for i in I2)
        df2['Power System'] = sum(df[i] for i in ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c'])
        # df2['Power System'] = df2['Power System']/max(df2['Power System'])
        df2['Electrolysis'] = df['AKE']#/max(df['AKE'])
        df2['SMR + CC'] = df['SMRH']#/max(df['SMRH'])
        df2['Rest'] = df['Rest']
        
        list2_, list3_, list4_, list5_ = ([] for _ in range(4))
        for year_ in YEAR:
            div_ = sum(DATA_[scenario_][year_]['Net_P']['HO'][k]['P_annual'] for k in h2_list)
            list2_.append(-1*DATA_[scenario_][year_]['Net_P']['HO']['EOR']['Credit']/div_)
            list3_.append(-1*sum(DATA_[scenario_][year_]['Net_P']['HO'][i]['Credit'] for i in ['AQoff_SMR'] )/div_)#'AQoff_DAC', 
            list4_.append(-1*DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['Credit']/div_)
            list5_.append(DATA_[scenario_][year_]['Net_S']['HO']['CH4']['B_annual']/div_)
            
        df2['45Q-EOR'] = list2_
        df2['45Q-Aquifer'] = list3_
        df2['45Q-Methanol'] = list4_
        df2['NG Purchase'] = list5_
        
        cols = ['Power System', 'Electrolysis', 'SMR + CC', 'Rest', '45Q-EOR', '45Q-Aquifer', '45Q-Methanol']
        # df2[cols] = df2[cols].div(df2[cols].sum(axis=1), axis=0).multiply(100)
        df2['Year'] = df2.index + 2022
    # plot data in stack manner of bar type
        width = 0.8
        space = 0.9
        fig, ax = plt.subplots(figsize=(10, 5))
        bar1 = ax.bar(df2['Year'], df2['Power System'], width, color= 'darkorange', label= 'Power System')
        bar2 = ax.bar(df2['Year'], df2['Electrolysis'], width, bottom= df2['Power System'], color='forestgreen', label='Electrolysis')
        bar3 = ax.bar(df2['Year'], df2['SMR + CC'], width, bottom= df2['Power System'] + df2['Electrolysis'], color='cadetblue', label='SMR + CC')
        bar4 = ax.bar(df2['Year'], df2['Rest'], width, bottom= df2['Power System'] + df2['Electrolysis'] + df2['SMR + CC'], color='indianred', label='H2 Storage ')
        
        bar5 = ax.bar(df2['Year'], df2['NG Purchase'], width, bottom= df2['Power System'] + df2['Electrolysis'] + df2['SMR + CC'] \
            + df2['Rest'], color='slategrey', label='NG Purchase')

        bar6 = ax.bar(df2['Year'], df2['45Q-EOR'], width, bottom = df2['45Q-Aquifer']+ df2['45Q-Methanol'], color = 'slateblue',  label = '45Q-EOR')
        bar7 = ax.bar(df2['Year'], df2['45Q-Aquifer'],   width, bottom = df2['45Q-Methanol'], color = 'saddlebrown', label = '45Q-Aquifer')
        bar8 = ax.bar(df2['Year'], df2['45Q-Methanol'], width, color = 'teal', label = '45Q-Methanol')
        
        bar5 = ax.bar(df2['Year'], df2['45Q-EOR'], width)

        plt.title('Contribution to total hydrogen cost [\$/kg.$H_{2}$] \n under a ' + scenario_.lower() + ' cost scenario', fontsize=16, color = 'midnightblue', y = 1)
        # plt.subtitle(, fontsize=14, y = 0.98)
        plt.xlabel('Year', fontsize=14)
        plt.ylabel('$', fontsize=14)
        plt.legend(fontsize=14)
        plt.xticks(fontsize= 14)
        plt.yticks(fontsize= 14)
        ax.set_xticks(df2['Year'])
        
        ax.xaxis.set_ticks_position('both')
        ax.yaxis.set_ticks_position('both')
        
        # x_ = list(range(2022,2032))
        x_ = [i + 2022 for i in YEAR]
        y_ = [1.0]*len(x_)
        ax.scatter(x_, y_, alpha =0.0001, color = 'black', marker = '*')
        
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        annot, Y_ = [], []
        for year_ in YEAR:
            
            value = DATA_[scenario_][year_]['Total']['HO']['LCOH']

            annot.append(str(round(value,2))) 
            Y_.append(value)
            
        for i, txt in enumerate(annot):
            ax.annotate(txt, (x_[i], y_[i]), verticalalignment = 'top', horizontalalignment = 'center'\
                , fontsize = 14, color = 'midnightblue')


        ax.scatter(x_, Y_,  s=20, facecolors='r', edgecolors='r', zorder = 2)
        ax.plot(x_, Y_, color = 'r', zorder = 2)
        lgd = plt.legend( bbox_to_anchor=(1.005, 1), fontsize = 13)
        # plt.ylim([-0.5,1.5])
        plt.grid(alpha = 0.25)
        plt.tight_layout()
        plt.savefig('h2_contr_' + scenario_.lower() + '.png', dpi = 1200)
        plt.show()    
        
    return

for DATA_ in DATA:
    plot_ = h_cost_contr(DATA_)

# df2.plot(x='Year', kind='bar', stacked=True,
    # title='Stacked Bar Graph by dataframe', colors = colors_).legend(loc='lower left')

#%%

def mile_cost_contr(DATA_:dict):
    """Provides a breakdown of the cost contribution
    in $/mile

    Args:
        DATA_ (dict): contains results 
    """
    I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'AKE', 'SMRH',  'EOR',  'H2_C_c', 'H2_L_c', 'DAC', 'MEFC','AQoff_SMR'] #'AQoff_DAC', 
    I2 = [ 'DAC', 'MEFC', 'EOR','AQoff_SMR', 'H2_C_c', 'H2_L_c'] # 'AQoff_DAC', 

    df = pd.DataFrame(columns = I)
    df2 = pd.DataFrame(columns = ['Power System', 'Electrolysis', 'SMR + CC', 'Rest'])
                

                
                
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()] 
    for scenario_ in SCENARIO:
        for year_ in YEAR:

            div_ = sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L', 'CH3OH', 'Power'])

            list_ = []
            for i in I:
                list_.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i][j] for j in ['Capex', 'Opex_fix', 'Opex_var'])/div_)
            # print(list_)
            
            df.loc[year_] = list_
        # view data
        df['Year'] = df.index
        df['AQoff'] = df['AQoff_SMR']  #+ df['AQoff_DAC']
        df['Rest'] = sum(df[i] for i in I2)
        df2['Power System'] = sum(df[i] for i in ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c'])
        # df2['Power System'] = df2['Power System']/max(df2['Power System'])
        df2['Electrolysis'] = df['AKE']#/max(df['AKE'])
        df2['SMR + CC'] = df['SMRH']#/max(df['SMRH'])
        df2['Rest'] = df['Rest']
        
        list2_, list3_, list4_, list5_ = ([] for _ in range(4))
        for year_ in YEAR:
            div_ = sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L', 'CH3OH', 'Power'])
            list2_.append(-1*DATA_[scenario_][year_]['Net_P']['HO']['EOR']['Credit']/div_)
            list3_.append(-1*sum(DATA_[scenario_][year_]['Net_P']['HO'][i]['Credit'] for i in [ 'AQoff_SMR'] )/div_) #'AQoff_DAC',
            list4_.append(-1*DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['Credit']/div_)
            list5_.append(DATA_[scenario_][year_]['Net_S']['HO']['CH4']['B_annual']/div_)
            
        df2['45Q-EOR'] = list2_
        df2['45Q-Aquifer'] = list3_
        df2['45Q-Methanol'] = list4_
        df2['NG Purchase'] = list5_
        
        cols = ['Power System', 'Electrolysis', 'SMR + CC', 'Rest', '45Q-EOR', '45Q-Aquifer', '45Q-Methanol']
        # df2[cols] = df2[cols].div(df2[cols].sum(axis=1), axis=0).multiply(100)
        df2['Year'] = df2.index + 2022
    # plot data in stack manner of bar type
        width = 0.8
        space = 0.9
        fig, ax = plt.subplots(figsize=(10, 5))
        bar1 = ax.bar(df2['Year'], df2['Power System'], width, color= 'darkorange', label= 'Power System')
        bar2 = ax.bar(df2['Year'], df2['Electrolysis'], width, bottom= df2['Power System'], color='forestgreen', label='Electrolysis')
        bar3 = ax.bar(df2['Year'], df2['SMR + CC'], width, bottom= df2['Power System'] + df2['Electrolysis'], color='cadetblue', label='SMR + CC')
        bar4 = ax.bar(df2['Year'], df2['Rest'], width, bottom= df2['Power System'] + df2['Electrolysis'] + df2['SMR + CC'], color='indianred', label='H2 Storage ')
        
        bar5 = ax.bar(df2['Year'], df2['NG Purchase'], width, bottom= df2['Power System'] + df2['Electrolysis'] + df2['SMR + CC'] \
            + df2['Rest'], color='slategrey', label='NG Purchase')

        bar6 = ax.bar(df2['Year'], df2['45Q-EOR'], width, bottom = df2['45Q-Aquifer']+ df2['45Q-Methanol'], color = 'slateblue',  label = '45Q-EOR')
        bar7 = ax.bar(df2['Year'], df2['45Q-Aquifer'],   width, bottom = df2['45Q-Methanol'], color = 'saddlebrown', label = '45Q-Aquifer')
        bar8 = ax.bar(df2['Year'], df2['45Q-Methanol'], width, color = 'teal', label = '45Q-Methanol')
        
        # bar5 = ax.bar(df2['Year'], df2['45Q-EOR'], width)

        plt.title('Contribution to total mile cost [\$/mile] \n under a ' + scenario_.lower() + ' cost scenario', fontsize=16, color = 'midnightblue', y = 1)
        # plt.subtitle(, fontsize=14, y = 0.98)
        plt.xlabel('Year', fontsize=14)
        plt.ylabel('$', fontsize=14)
        plt.legend(fontsize=14)
        plt.xticks(fontsize= 14)
        plt.yticks(fontsize= 14)
        ax.set_xticks(df2['Year'])
        
        ax.xaxis.set_ticks_position('both')
        ax.yaxis.set_ticks_position('both')
        
        x_ = list(range(2022,2032))
        y_ = [0.65]*10
        ax.scatter(x_, y_, alpha =0.0001, color = 'black', marker = '*')
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        annot = []
        for year_ in YEAR:
            div_ = sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L', 'CH3OH', 'Power'])
            value = DATA_[scenario_][year_]['Total']['HO']['Objective']/div_

            annot.append(str(round(value,2))) 
            
        for i, txt in enumerate(annot):
            ax.annotate(txt, (x_[i], y_[i]), verticalalignment = 'top', horizontalalignment = 'center'\
                , fontsize = 14, color = 'midnightblue')
        plt.legend( bbox_to_anchor=(1.005, 1), fontsize = 13)
        # plt.ylim([-0.75,3.5])
        plt.grid(alpha = 0.25)
        plt.show()    
        
    return

for DATA_ in DATA:
    plot_ = mile_cost_contr(DATA_)
    



#%%MATERIAL FLOW SANKEY

for DATA_ in DATA:
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]

    year_ = 0

    for scenario_ in SCENARIO:
        fig = go.Figure(data=[go.Sankey(
            node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = ["Water", "Carbon dioxide (captured)", "Natural gas",\
                "Hydrogen (Green)", "Hydrogen (Blue)",\
                "Carbon dioxide (sequestered)", "Carbon dioxide (vented)",\
                    "Methanol", 'Enhanced Oil Recovery', 'Crude oil'],
            color = ['turquoise', 'darksalmon', 'darkslategrey', 'forestgreen', \
                'cadetblue', 'sandybrown', 'darkred', 'seagreen', 'darkorange', 'dimgray']
            ),
            link = dict(
            source = [0, 1, 2, 2, 2, 3, 2, 8, 8, 0], # indices correspond to labels, eg A1, A2, A1, B1, ...
            target = [3, 7, 4, 5, 6, 7, 8, 9, 6, 4],
            color = ['mediumaquamarine', 'salmon', 'powderblue', 'peachpuff', 'red',\
                'mediumseagreen', 'orange', 'lightgray', 'red', 'powderblue'],
            value =  [DATA_[scenario_][year_]['Net_P']['HO']['AKE']['P_annual']*dict_conversion['AKE']['H2_G'],\
                DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual']*dict_conversion['MEFC']['CH3OH'],\
                    DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']*dict_conversion['SMRH']['H2_B'],\
                        DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']*dict_conversion['SMRH']['CO2'],\
                            DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']*dict_conversion['SMRH']['CO2_Vent'],\
                                DATA_[scenario_][year_]['Net_P']['HO']['DAC']['P_annual']*dict_conversion['DAC']['CO2_DAC']*-1,\
                                    DATA_[scenario_][year_]['Net_P']['HO']['EOR']['P_annual']*dict_conversion['EOR']['CO2']*-1,\
                                        DATA_[scenario_][year_]['Net_P']['HO']['EOR']['P_annual']*dict_conversion['EOR']['CO2_EOR']*136,\
                                            DATA_[scenario_][year_]['Net_P']['HO']['EOR']['P_annual']*dict_conversion['EOR']['CO2_Vent'],\
                                                DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']*dict_conversion['SMRH']['H2O']*-1]
            # value = [10]*9
        ))])
        # fig.update_layout(title_text='Material flow for ' + str(2022+ year_) + ' under a ' + scenario_.lower() + ' cost scenario', font_size=14)
        # fig.savefig(, dpi = 300)
        pio.write_image(fig, 'MF_' + str(2022+year_) + '_' + scenario_.lower() + '.png',  scale=1)

        fig.show()
        
#%%ENERGY FLOWS

for DATA_ in DATA:
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    year_ = 4

    for scenario_ in SCENARIO:
        I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'AKE', 'SMRH', 'DAC', 'MEFC', 'EOR', 'AQoff', 'Power_dummy']
        fig = go.Figure(data=[go.Sankey(
            node = dict(
            pad = 10,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = [I_labels_['short'][i] for i in I ],
            color = ['darkorange', 'cornflowerblue', 'yellow', 'royalblue', \
                'darkgoldenrod', 'forestgreen', 'cadetblue', 'indigo', 'teal', 'slategrey', 'saddlebrown', 'cadetblue']
            ),
            link = dict(
            source = [0, 1, 11, 2, 11, 3, 11, 4, 11, 11, 11, 11, 11, 11], # indices correspond to labels, eg A1, A2, A1, B1, ...
            target = [11, 11, 2, 11, 3, 11, 4, 11, 5, 6, 7, 8, 9, 10],
            # color = ['mediumaquamarine', 'lightsteelblue', 'powderblue', 'peachpuff', 'red',\
            #     'mediumseagreen', 'orange', 'lightgray', 'red', 'powderblue'],
            color = ['orange', 'lightblue', 'khaki', 'aquamarine', 'cornflowerblue', 'aquamarine', 'coral', 'aquamarine', \
                'lightsteelblue', 'lightsteelblue', 'lightsteelblue', 'lightsteelblue', 'lightsteelblue', 'lightsteelblue' ],
            value =  [
                DATA_[scenario_][year_]['Net_P']['HO']['PV']['P_annual']*dict_conversion['PV']['Power'],
                DATA_[scenario_][year_]['Net_P']['HO']['WF']['P_annual']*dict_conversion['WF']['Power'],
                DATA_[scenario_][year_]['Net_P']['HO']['LiI_c']['P_annual']*dict_conversion['LiI_c']['Charge'],
                DATA_[scenario_][year_]['Net_P']['HO']['LiI_d']['P_annual']*dict_conversion['LiI_d']['Power'],
                DATA_[scenario_][year_]['Net_P']['HO']['PSH_c']['P_annual']*dict_conversion['PSH_c']['H2O_E'],
                DATA_[scenario_][year_]['Net_P']['HO']['PSH_d']['P_annual']*dict_conversion['PSH_d']['Power'],
                DATA_[scenario_][year_]['Net_P']['HO']['CAES_c']['P_annual']*dict_conversion['CAES_c']['Air_C'],
                DATA_[scenario_][year_]['Net_P']['HO']['CAES_d']['P_annual']*dict_conversion['CAES_d']['Power'],
                DATA_[scenario_][year_]['Net_P']['HO']['AKE']['P_annual']*dict_conversion['AKE']['Power']*-1,
                DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']*dict_conversion['SMRH']['Power']*-1,
                DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual']*dict_conversion['MEFC']['Power']*-1,
                DATA_[scenario_][year_]['Net_P']['HO']['DAC']['P_annual']*dict_conversion['DAC']['Power']*-1,
                DATA_[scenario_][year_]['Net_P']['HO']['EOR']['P_annual']*dict_conversion['EOR']['Power']*-1,
                # DATA_[scenario_][year_]['Net_P']['HO']['AQoff_DAC']['P_annual']*dict_conversion['AQoff_DAC']['Power']*-1 + \
                DATA_[scenario_][year_]['Net_P']['HO']['AQoff_SMR']['P_annual']*dict_conversion['AQoff_SMR']['Power']*-1
                ]
            # value = [10]*9
        ))])
        fig.update_layout(title_text='Energy flow', font_size=14)
        fig.show()

#%%

I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'AKE', 'SMRH', 'DAC', 'MEFC', 'EOR', 'AQoff_DAC', 'AQoff_SMR']

label = [I_labels_['short'][i] for i in I ]


#%%

def annual_bg(DATA_):
    """Plots annual blue and green hydrogen contribution to the overall demand over the entire planning horizon

    Args:
        DATA_ (list): list containing dictionaiers with data 
    """
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    for scenario_ in SCENARIO:
        Green_H2, Blue_H2, X_ = ([] for _ in range(3))
        for year_ in YEAR:
            # Green_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['AKE']['P_annual']*37.50/(365*907.185))
            Green_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual']/(907.185))
            
            # print(Green_H2)
            # Blue_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']/(365*907.185))
            Blue_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual']/(907.185))
            
            # print(Blue_H2)
            X_.append(int(year_ + 2022))
            
        print(Green_H2)
        print(Blue_H2)
        
        width = 0.8
        space = 0.2
        fig, ax = plt.subplots(figsize=(8.27/3, 11.69/3))
        ax.bar(X_, Blue_H2, width, color= 'lightsteelblue', label= 'Blue H2')
        ax.bar(X_, Green_H2, width, bottom= Blue_H2, color='mediumseagreen', label='Green H2')
        plt.title('Total hydrogen production under a ' + scenario_ + ' cost scenario', fontsize=20)
        plt.xlabel('Year', fontsize=20)
        plt.ylabel('US tonnes', fontsize=20)
        plt.legend(fontsize=20)
        plt.xticks(fontsize= 16)
        plt.yticks(fontsize= 16)
        ax.set_xticks(X_)
        plt.show()    
    return       

for DATA_ in DATA:
    annual_bg(DATA_)
    
        
#%%
def h2_cost(DATA:list):
    """Compares the cost of hydrogen production under

    Args:
        DATA (list): list containing dictionaiers with data 
    """
    iter_ = 0
    fig, ax = plt.subplots(figsize=(20, 6))
    color = ['lightcoral', 'palegoldenrod', 'yellowgreen', 'lightcoral', 'palegoldenrod', 'yellowgreen']
    width = 0.3
    space = 0.2
    for DATA_ in DATA:
        SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
        scenario_ = SCENARIO[0]
        Y_, X_ = [], []
        
        for year_ in YEAR:
            Y_.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/(DATA_[scenario_][year_]['Net_S']['HO']['H2_C']['S_annual']\
                + DATA_[scenario_][year_]['Net_S']['HO']['H2_L']['S_annual']))
            # Green_H2.append(RESULTS[scenario_][year_]['Total']['HO']['Objective']/(RESULTS[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']))
            X_.append(year_ + 2022)# + iter_*width)    

        # ax.(X_, Y_, width, color = color[iter_], label = scenario_, align='edge')
        ax.plot(X_, Y_, color = color[iter_], label = scenario_)
        ax.scatter(X_, Y_, color = color[iter_])
        
        iter_+= 1
    plt.title('Cost of hydrogen production under different cost scenarios', fontsize=20)
    plt.xlabel('Year', fontsize=20)
    plt.ylabel('$/kg.H2', fontsize=20)
    plt.legend(fontsize=20)
    plt.xticks(fontsize= 16)
    plt.yticks(fontsize= 16)
    plt.grid(axis = 'y', color = '0.85')
    ax.set_xticks(X_)# - (iter_-1)*width for x in X_])
    # ax.set_yticks(np.arange(0,7))# - (iter_-1)*width for x in X_])
    plt.show()
    return


h2_cost(DATA)

#%%

def mile_cost(DATA:list):
    """Compares the cost of hydrogen production under

    Args:
        DATA (list): list containing dictionaiers with data 
    """
    iter_ = 0
    fig, ax = plt.subplots(figsize=(20, 6))
    color = ['lightcoral', 'palegoldenrod', 'yellowgreen', 'lightcoral', 'palegoldenrod', 'yellowgreen']
    width = 0.3
    space = 0.2
    for DATA_ in DATA:
        SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
        scenario_ = SCENARIO[0]
        Y_, X_ = [], []
        
        for year_ in YEAR:
            Y_.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/sum(DATA_[scenario_][year_]['Net_S']['HO'][j]['Mile_annual'] for j in ['Power', 'H2_C', 'H2_L', 'CH3OH']))
            # Green_H2.append(RESULTS[scenario_][year_]['Total']['HO']['Objective']/(RESULTS[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']))
            X_.append(year_ + 2022)# + iter_*width)    

        # ax.(X_, Y_, width, color = color[iter_], label = scenario_, align='edge')
        ax.plot(X_, Y_, color = color[iter_], label = scenario_)
        ax.scatter(X_, Y_, color = color[iter_])
        
        iter_+= 1
    plt.title('Cost per mile under different cost scenarios', fontsize=20)
    plt.xlabel('Year', fontsize=20)
    plt.ylabel('$/kg.H2', fontsize=20)
    plt.legend(fontsize=20)
    plt.xticks(fontsize= 16)
    plt.yticks(fontsize= 16)
    plt.grid(axis = 'y', color = '0.85')
    ax.set_xticks(X_)# - (iter_-1)*width for x in X_])
    # ax.set_yticks(np.arange(0,7))# - (iter_-1)*width for x in X_])
    plt.show()
    return

mile_cost(DATA)
#%%
# J = ['H2O_E']
# J = ['Air_C', 'Charge', 'H2O_E', 'CO2_AQoff', 'CO2_DAC']
# J = ['CO2_EOR']
# J = ['PV']
# J = ['LiI_c', 'LiI_d', 'CAES_c', 'CAES_d', 'PSH_c', 'PSH_d', 'PV', 'WF', 'AKE',\
    # 'SMRH', 'H2_C_c', 'H2_C_d', 'H2_L_c', 'H2_L_d',  'MEFC', 'DAC', 'EOR', 'AQoff_SMR','AQoff_DAC', 'H2_Sink1', 'H2_Sink2']

# J = ['Charge', 'Air_C', 'H2O_E', 'Solar', 'Wind', 'Power', 'H2_C', 'H2_L', 'H2', \
#     'H2_B', 'H2_G', 'H2O', 'O2', 'CH4', 'CO2', 'CO2_DAC', 'CO2_AQoff', \
#         'CO2_EOR', 'CH3OH']

J = ['Charge', 'Air_C', 'H2O_E', 'CO2_AQoff', 'CO2_EOR']


def inventory(DATA_:list):
    """Plots inventory levels of all storage facilities

    Args:
        DATA_ (list): list containing dictionaiers with data 
        year_ (int): year being plotted
    """
    Inv = []
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    scenario_ = SCENARIO[0]
    for y, d, h in product(YEAR, D, H):
        Inv.append(DATA_[scenario_][y]['Sch_S']['HO'][j][h][d]['Inv'])
        # Inv.append(DATA_[scenario_][year_]['Sch_P']['HO'][j][h][d]['P'])
        # Inv.append(DATA_[scenario_][year_]['Sch_S']['HO'][j][h][d]['S'])
    pos_list = [8760*y for y in YEAR] # hours of the year corresponding to month]
    name_list = [y + 2022 for y in YEAR]    
        
    fig, ax = plt.subplots(figsize = (12,6))
    X_ = np.arange(1,87601)    
    ax.plot(X_, Inv, color = 'dodgerblue', label = 'Blue pathway')
    ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
    ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
    ax.tick_params(axis='x', labelsize =13)
    plt.grid(alpha  = 0.40)
    plt.title(str(j))
    plt.show()
    
    return
for DATA_ in DATA:
    for j in J:
        plot = inventory(DATA_)
    

   pos_list = [8760*y for y in YEAR] # hours of the year corresponding to month]
    name_list = [y + 2022 for y in YEAR]  
        ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
    ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
#%%
def h2_prod_inv(DATA_:list, year_:int):
    """Plots green and blue hydrogen production for a chosen year alongside hydrogen local and geological storage

    Args:
        DATA_ (list): list containing dictionaiers with data 
        year_ (int): year being plotted
    """
    Green, Blue, Local, Geo, H2, Solar, Wind, Pow_stor, Pow_rel = ([] for _ in range(9))
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    scenario_ = SCENARIO[0]
    for d, h in product(D, H):
        Local.append(DATA_[scenario_][year_]['Sch_S']['HO']['H2_C'][h][d]['Inv']/907.185)
        Geo.append(DATA_[scenario_][year_]['Sch_S']['HO']['H2_L'][h][d]['Inv']/907.185)
        H2.append((DATA_[scenario_][year_]['Sch_S']['HO']['H2_C'][h][d]['S'] \
            + DATA_[scenario_][year_]['Sch_S']['HO']['H2_L'][h][d]['S'])/907.185)
        
        Green.append(DATA_[scenario_][year_]['Sch_P']['HO']['AKE'][h][d]['P']*dict_conversion['AKE']['H2_G']/907.185)
        Blue.append(DATA_[scenario_][year_]['Sch_P']['HO']['SMRH'][h][d]['P']/907.185)
        # value = DATA_[scenario_][year_]['Sch_P']['HO']['AKE'][h][d]['P']*dict_conversion['AKE']['H2_G'] +  DATA_[scenario_][year_]['Sch_P']['HO']['SMRH'][h][d]['P']
        Solar.append(DATA_[scenario_][year_]['Sch_P']['HO']['PV'][h][d]['P'])
        Wind.append(DATA_[scenario_][year_]['Sch_P']['HO']['WF'][h][d]['P'])
        Pow_stor.append(-1*sum(DATA_[scenario_][year_]['Sch_P']['HO'][i][h][d]['P'] for i in ['LiI_c', 'CAES_c', 'PSH_c']))
        Pow_rel.append(sum(DATA_[scenario_][year_]['Sch_P']['HO'][i][h][d]['P'] for i in ['LiI_d', 'CAES_d', 'PSH_d']))
        
    fig, (ax1, ax3) = plt.subplots(2, 1 , figsize = (24,12))
    X_ = np.arange(1,8761)    
    ax1.bar(X_, Blue, color = 'dodgerblue', label = 'Blue pathway')
    ax1.bar(X_, Green, bottom = Blue, color = 'seagreen', label = 'Green pathway')
    ax1.set_ylabel('Production [US tons/hour]', fontsize= 14)
    ax1.tick_params(axis='y', colors='red', labelsize =14)
    
    ax1.yaxis.label.set_color('red')
    leg1 = ax1.legend(bbox_to_anchor=(1.18, 1), fontsize= 12)
    
    pos_list = [0, 744, 1344, 2160, 2800, 3624, 4344, 5088, 5832, 6552, 7296, 8016] # hours of the year corresponding to month
    name_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    ax1.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
    ax1.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
    ax1.tick_params(axis='x', labelsize =13)
   
    ax2 = ax1.twinx()
    ax2.plot(X_, Local, color = 'yellow', label = 'Local storage')
    ax2.plot(X_, Geo, color = 'darkorange', label = 'Geological storage')
    ax2.set_ylabel('Inventory levels [US tons]', fontsize= 14)
    ax2.spines['right'].set_color('blue')
    ax2.spines['left'].set_color('red')    
    
    ax2.tick_params(axis='y', colors='blue', labelsize =14)
    ax2.yaxis.label.set_color('blue')
    # ax2.set_ylim([0, 20000])
    leg2 = ax2.legend(bbox_to_anchor=(1.18, 0.8), fontsize= 12)
    
    leg1.get_frame().set_edgecolor('r')
    leg2.get_frame().set_edgecolor('b')
    
    ax1.set_title('Production and inventory levels for year ' + str(year_ + 2022) + \
        ' under a(n) ' + scenario_.lower() + ' cost scenario', fontsize= 14)
    
    ax3.bar(X_, Solar, color = 'darkorange', label = 'Solar')
    ax3.bar(X_, Wind, bottom = Solar, color = 'darkgreen', label = 'Wind')
    ax3.bar(X_, Pow_rel, bottom = [sum(x) for x in zip(Wind, Solar)], color = 'cornflowerblue', label = 'Power discharged')
    # print(len(Solar), len(Wind), len(Pow_stor), len(Pow_rel))
    ax3.bar(X_, Pow_stor, color = 'indianred', label = 'Power stored')
    ax3.set_title('Renewable power generation', fontsize = 14)
    ax3.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
    ax3.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
    ax3.set_ylabel('[MW]', fontsize= 14)
    ax3.tick_params(axis='x', labelsize =13)
    ax3.tick_params(axis='y', labelsize =14)
    
    leg3 = ax3.legend(bbox_to_anchor=(1.18, 1), fontsize = 12)
    leg3.get_frame().set_edgecolor('black')
    
    ax1.xaxis.set_ticks_position('both')
    ax3.yaxis.set_ticks_position('both')
    ax3.xaxis.set_ticks_position('both')
    
    plt.show()
    
    return


for DATA_ in DATA:
    h2_prod_inv(DATA_, 2)

#%%

def scale(list_:list):
    div = max(list_)
    list2_ = [100*i/div for i in list_]
    return list2_

def schedule(DATA_:list, year_:int):
    """Plots green and blue hydrogen production for a chosen year alongside hydrogen local and geological storage

    Args:
        DATA_ (list): list containing dictionaiers with data 
        year_ (int): year being plotted
    """
    Green, Blue, Local, Geo, H2, Solar, Wind, Pow_stor, Pow_rel = ([] for _ in range(9))
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    scenario_ = SCENARIO[0]
    for d, h in product(D, H):
        Local.append(DATA_[scenario_][year_]['Sch_S']['HO']['H2_C'][h][d]['Inv']/907.185)
        Geo.append(DATA_[scenario_][year_]['Sch_S']['HO']['H2_L'][h][d]['Inv']/907.185)
        H2.append((DATA_[scenario_][year_]['Sch_S']['HO']['H2_C'][h][d]['S'] \
            + DATA_[scenario_][year_]['Sch_S']['HO']['H2_L'][h][d]['S'])/907.185)
        
        Green.append(DATA_[scenario_][year_]['Sch_P']['HO']['AKE'][h][d]['P']*dict_conversion['AKE']['H2_G']/907.185)
        Blue.append(DATA_[scenario_][year_]['Sch_P']['HO']['SMRH'][h][d]['P']/907.185)
        # value = DATA_[scenario_][year_]['Sch_P']['HO']['AKE'][h][d]['P']*dict_conversion['AKE']['H2_G'] +  DATA_[scenario_][year_]['Sch_P']['HO']['SMRH'][h][d]['P']
        Solar.append(DATA_[scenario_][year_]['Sch_P']['HO']['PV'][h][d]['P'])
        Wind.append(DATA_[scenario_][year_]['Sch_P']['HO']['WF'][h][d]['P'])
        Pow_stor.append(
            sum(DATA_[scenario_][year_]['Sch_P']['HO'][i][h][d]['P'] for i in ['LiI_c', 'CAES_c', 'PSH_c'])
            )
        Pow_rel.append(
            sum(DATA_[scenario_][year_]['Sch_P']['HO'][i][h][d]['P'] for i in ['LiI_d', 'CAES_d', 'PSH_d'])
        )

    
    Local = scale(Local)
    Geo = scale(Geo)
    Green = scale(Green)
    Blue = scale(Blue)
    Solar = scale(Solar)
    Wind = scale(Wind)
    Pow_rel = scale(Pow_rel)
    Pow_stor = scale(Pow_stor)

    fig, ax = plt.subplots(8,1, figsize = (16,18))
    X_ = np.arange(1,8761)    
    pos_list = [0, 744, 1344, 2160, 2800, 3624, 4344, 5088, 5832, 6552, 7296, 8016] # hours of the year corresponding to month
    name_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    ax[0].plot(X_, Blue, color = 'dodgerblue', label = 'Blue pathway')
    ax[0].title.set_text('(a) Steam methane reforming + Carbon capture')
    ax[0].fill_between(X_, Blue, color = 'dodgerblue', alpha = 0.5)

    ax[1].plot(X_, Green, color = 'seagreen', label = 'Green pathway')
    ax[1].title.set_text('(b) Alkaline water electrolysis')
    ax[1].fill_between(X_, Blue, color = 'seagreen', alpha = 0.9)
    
    ax[2].plot(X_, Local, color = 'teal', label = 'Local storage')
    ax[2].fill_between(X_, Local, color = 'teal', alpha = 0.9)
    ax[2].title.set_text('(c) Liquefied local $H_{2}$ storage')
    
    ax[3].plot(X_, Geo, color = 'darkorange', label = 'Geological storage')    
    ax[3].fill_between(X_, Geo, color = 'darkorange', alpha = 0.9)
    ax[3].title.set_text('(d) Geological $H_{2}$ storage')
    
    ax[4].plot(X_, Solar, color = 'orange', label = 'Solar')
    ax[4].fill_between(X_, Solar, color = 'orange', alpha = 0.9)
    ax[4].title.set_text('(e) Solar photovoltaic array')
    
    ax[5].plot(X_, Wind, color = 'darkgreen', label = 'Wind')
    ax[5].fill_between(X_, Wind, color = 'darkgreen', alpha = 0.9)  
    ax[5].title.set_text('(f) Wind mill array')
     
    ax[6].plot(X_, Pow_rel, color = 'cornflowerblue', label = 'Power discharged')
    ax[6].fill_between(X_, Pow_rel, color = 'cornflowerblue', alpha = 0.9)      
    ax[6].title.set_text('(g) Power discharged')
    
    ax[7].plot(X_, Pow_stor, color = 'indianred', label = 'Power stored')
    ax[7].fill_between(X_, Pow_stor, color = 'indianred', alpha = 0.9)   
    ax[7].title.set_text('(i) Power stored')
       
    ax[7].tick_params(axis='x', labelsize =12.5)
    ax[0].tick_params(axis='x', labelsize =12.5)
    
    
    

    for i in range(7):
        ax[i].axes.xaxis.set_ticklabels([])
        # ax[i].set_xticks('w')   
    for i in range(8):    
        ax[i].tick_params(axis='y', labelsize =13)
        ax[i].grid(True, axis = 'x')
        ax[i].tick_params(axis='y', which='minor')
        ax[i].xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
        ax[i].xaxis.set_ticks_position('both')
    ax[7].xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
    # ax[0].xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
    # ax[0].tick_params(labelbottom=False,labeltop=True)

    plt.savefig('capacity_utilization.png')
    plt.show()
    
    return


for DATA_ in DATA:
    schedule(DATA_, 4)
   
#%%

def carbon_eq(DATA:list):
    """Compares the carbon intensity of hydrogen production [kg.CO2/kg.H2] under

    Args:
        DATA (list): list containing dictionaiers with data 
    """
    iter_ = 0
    fig, ax = plt.subplots(figsize=(10, 6))
    color = [ 'lightcoral', 'palegoldenrod', 'yellowgreen']
    width = 0.2
    space = 0.2
    for DATA_ in DATA:
        SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
        scenario_ = SCENARIO[0]
        Y_, X_ = [], []
        
        for year_ in YEAR:
            Y_.append(DATA_[scenario_][year_]['Net_S']['HO']['CO2_Vent']['S_annual']/(DATA_[scenario_][year_]['Net_S']['HO']['H2_C']['S_annual']\
                + DATA_[scenario_][year_]['Net_S']['HO']['H2_L']['S_annual']))
            X_.append(year_ + 2022)
        ax.bar([i  + width*(-1+iter_) for i in X_] , Y_, width, color = color[iter_], label = scenario_)
        # ax.plot(X_ , Y_, color = color[iter_], label = scenario_)
        
        iter_+= 1
    ax.set_xticks(X_)
    x_line = [2026.5]*70
    y_line = np.arange(0,7,0.1)
    ax.plot(x_line, y_line, '--', alpha = 0.5, color = 'slateblue')
    plt.ylim([0, 7.5])
    plt.title('Carbon intensity under different cost scenarios', fontsize=14)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('$kg.CO_{2}/kg.H_{2}$', fontsize=14)
    plt.legend(fontsize=14, loc="upper left", mode = "expand", ncol = 3)
    plt.xticks(fontsize= 14)
    plt.yticks(fontsize= 14)
    plt.grid(axis = 'y', alpha = 0.4, color = '0.85')
    plt.annotate('End of term 1', (2026.5, 6.25), verticalalignment = 'top', horizontalalignment = 'center'\
                    , fontsize = 14, color = 'slateblue')
    plt.savefig('carbon_intensity.jpeg', dpi = 200)
    plt.show()
    return

carbon_eq(DATA)

#%%

def cost_h2(DATA:list):
    """Compares the cost of hydrogen production under

    Args:
        DATA (list): list containing dictionaiers with data 
    """
    iter_ = 0
    fig, ax = plt.subplots(figsize=(10, 6))
    color = [ 'lightcoral', 'palegoldenrod', 'yellowgreen']
    width = 0.2
    space = 0.2
    for DATA_ in DATA:
        SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
        scenario_ = SCENARIO[0]
        Y_, X_ = [], []
        
        for year_ in YEAR:
            Y_.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/(DATA_[scenario_][year_]['Net_S']['HO']['H2_C']['S_annual']\
                + DATA_[scenario_][year_]['Net_S']['HO']['H2_L']['S_annual']))
            # Y_.append(DATA_[scenario_][year_]['Total']['HO']['Land_total'])
            X_.append(year_ + 2022)
        ax.bar([i  + width*(-1+iter_) for i in X_] , Y_, width, color = color[iter_], label = scenario_)
        # ax.plot(X_ , Y_, color = color[iter_], label = scenario_)
        # ax.scatter(X_ , Y_, color = color[iter_], marker = '.')
        
        
        
        iter_+= 1
    ax.set_xticks(X_)
    x_line = [2026.5]*61
    y_line = np.arange(0,6.1,0.1)
    ax.plot(x_line, y_line, '--', alpha = 0.5, color = 'slateblue')
    plt.ylim([0, 3.5])
    plt.title('Levelized cost of hydrogen under different cost sc', fontsize=14)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('$\$/kg.H_{2}$', fontsize=14)
    plt.legend(fontsize=14, loc="upper left", mode = "expand", ncol = 3)
    plt.xticks(fontsize= 14)
    plt.yticks(fontsize= 14)
    plt.grid(axis = 'y', alpha = 0.5, color = '0.85')
    plt.annotate('End of term 1', (2026.5, 3), verticalalignment = 'top', horizontalalignment = 'center'\
                    , fontsize = 14, color = 'slateblue')
    plt.savefig('lcoh.jpeg', dpi = 200)
    plt.show()
    return

cost_h2(DATA)
       

#%%
YEAR = np.arange(0,5)
def opportunistic_h2(DATA_:dict):
    """fitted lines to show the relationship between 
    renewable generation potential and green H2 production

    Args:
        DATA_ (dict): dictionary with output data
    """
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    for scenario_ in SCENARIO:
        iter_ = 0
        fig, ax = plt.subplots(figsize = (10,10))
        
        patches = []
        for year_ in YEAR:
            patches.append(mpatches.Patch(color=(0, 0 + year_*0.1, 1 - year_*0.1), label= year_ + 2022))

        for year_ in YEAR:
            xdata, ydata = [], []
            df = pd.DataFrame()
            df_plot = pd.DataFrame()
            for d in D:
                div = sum(DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink1'][h][d]['P'] + DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink2'][h][d]['P'] for h in H)
                if div >0:
                    ydata.append(sum(DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink2'][h][d]['P'] for h in H)*100 /div)
                    xdata.append(sum(DATA_[scenario_][year_]['Sch_P']['HO']['PV'][h][d]['P'] + DATA_[scenario_][year_]['Sch_P']['HO']['WF'][h][d]['P'] for h in H))
            xdata = [i*100/max(xdata) for i in xdata]
            ydata = np.array(ydata)
            xdata = np.array(xdata)
            
            df['x'] = xdata
            df['y'] = ydata
 

            z_scores = zscore(df)

            abs_z_scores = np.abs(z_scores)
            filtered_entries = (abs_z_scores < 1).all(axis=1)
            filtered_df = df[filtered_entries]
                
            # theta  = np.polyfit(x=df['x'], y=df['y'], deg=2)
            theta  = np.polyfit(x=filtered_df['x'], y=filtered_df['y'], deg=2)
            
            # print(f'The parameters of the curve: {theta}')

            # Now, calculating the y-axis values against x-values according to
            # the parameters theta0, theta1 and theta2
            y_line = theta[2] + theta[1] * pow(filtered_df['x'], 1) + theta[0] * pow(filtered_df['x'], 2) 
            # y_line = theta[3] + theta[2] * pow(xdata, 1) + theta[1] * pow(xdata, 2) +  theta[0] * pow(xdata, 3) 
            
            filtered_df['yline'] = y_line

            filtered_df = filtered_df.sort_values(by='x')

            
            plot_df = pd.concat([filtered_df['x'], filtered_df['yline']], axis=1, keys= ['x', 'yline'])
   
            plt.plot(filtered_df['x'], filtered_df['yline'], color =  (0, 0 + iter_*0.1, 1 - iter_*0.1), label = iter_)
            if year_ < 5:
                plt.annotate(str(year_ + 2022), (filtered_df['x'].iloc[-1]+ 2, filtered_df['yline'].iloc[-1]), verticalalignment = 'top', horizontalalignment = 'center'\
                    , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
            elif year_ == 9:
                plt.annotate(str(year_ + 2022), (filtered_df['x'].iloc[0] - 1, filtered_df['yline'].iloc[0] -1), verticalalignment = 'top', horizontalalignment = 'center'\
                    , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
            else:
                plt.annotate(str(year_ + 2022), (filtered_df['x'].iloc[0] - 2, filtered_df['yline'].iloc[0]), verticalalignment = 'top', horizontalalignment = 'center'\
                    , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
            iter_+= 1
        ax.xaxis.set_ticks_position('both')
        ax.yaxis.set_ticks_position('both')
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        plt.title('Opportunistic production of green $H_{2}$ \n under a(n) ' + scenario_.lower() + ' cost scenario', fontsize = 14)
        plt.xlabel('Renewable power capacity utilization ', fontsize = 14)
        plt.ylabel('Green hydrogen [$\%$ ]', fontsize = 14)
        plt.xlim([10,75])
        # plt.ylim([0,100])
        
        # plt.legend(handles= patches, bbox_to_anchor=(1.05, 1))   
        plt.grid(alpha = 0.25)
        

        plt.show()
    return 
    
for DATA_ in DATA:
    plot_ = opportunistic_h2(DATA_)
    
#%%


def split_opportunistic_h2(DATA_:dict):
    """fitted lines to show the relationship between 
    renewable generation potential and green H2 production

    Args:
        DATA_ (dict): dictionary with output data
    """
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    for scenario_ in SCENARIO:
        iter_ = 0
        fig, axs = plt.subplots(1,3, sharex = True, sharey = True, figsize = (15,5))
        fig.add_subplot(111, frameon=False)
        patches = []
        for year_ in YEAR:
            patches.append(mpatches.Patch(color=(0, 0 + year_*0.1, 1 - year_*0.1), label= year_ + 2022))

        for year_ in YEAR:
            xdata, ydata = [], []
            df = pd.DataFrame()
            df_plot = pd.DataFrame()
            for d in D:
                div = sum(DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink1'][h][d]['P'] + DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink2'][h][d]['P'] for h in H)
                if div >0:
                    ydata.append(sum(DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink2'][h][d]['P'] for h in H)*100 /div)
                    xdata.append(sum(DATA_[scenario_][year_]['Sch_P']['HO']['PV'][h][d]['P'] + DATA_[scenario_][year_]['Sch_P']['HO']['WF'][h][d]['P'] for h in H))
            xdata = [i*100/max(xdata) for i in xdata]
            ydata = np.array(ydata)
            xdata = np.array(xdata)
            
            df['x'] = xdata
            df['y'] = ydata
 

            z_scores = zscore(df)

            abs_z_scores = np.abs(z_scores)
            filtered_entries = (abs_z_scores < 1).all(axis=1)
            filtered_df = df[filtered_entries]
                
            # theta  = np.polyfit(x=df['x'], y=df['y'], deg=2)
            theta  = np.polyfit(x=filtered_df['x'], y=filtered_df['y'], deg=2)
            
            # print(f'The parameters of the curve: {theta}')

            # Now, calculating the y-axis values against x-values according to
            # the parameters theta0, theta1 and theta2
            y_line = theta[2] + theta[1] * pow(filtered_df['x'], 1) + theta[0] * pow(filtered_df['x'], 2) 
            # y_line = theta[3] + theta[2] * pow(xdata, 1) + theta[1] * pow(xdata, 2) +  theta[0] * pow(xdata, 3) 
            
            filtered_df['yline'] = y_line

            filtered_df = filtered_df.sort_values(by='x')

            
            plot_df = pd.concat([filtered_df['x'], filtered_df['yline']], axis=1, keys= ['x', 'yline'])
   

            # plt.plot(filtered_df['x'], filtered_df['yline'], color =  (0, 0 + iter_*0.1, 1 - iter_*0.1), label = iter_)
            
            if year_ < 5:
                axs[0].plot(filtered_df['x'], filtered_df['yline'], color =  (0, 0 + iter_*0.1, 1 - iter_*0.1), label = iter_)
                if year_ <3:
                    axs[0].annotate(str(year_ + 2022), (filtered_df['x'].iloc[-1]+ 4, filtered_df['yline'].iloc[-1]), verticalalignment = 'top', horizontalalignment = 'center'\
                        , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
                else:
                    axs[0].annotate(str(year_ + 2022), (filtered_df['x'].iloc[-1]+ 4, filtered_df['yline'].iloc[-1]+ 2), verticalalignment = 'top', horizontalalignment = 'center'\
                        , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
            elif year_ in [5,6]:
                axs[1].plot(filtered_df['x'], filtered_df['yline'], color =  (0, 0 + iter_*0.1, 1 - iter_*0.1), label = iter_)
                if year_ == 6:
                    axs[1].annotate(str(year_ + 2022), (filtered_df['x'].iloc[-1] + 4, filtered_df['yline'].iloc[-1]), verticalalignment = 'top', horizontalalignment = 'center'\
                        , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
                else:
                    axs[1].annotate(str(year_ + 2022), (filtered_df['x'].iloc[-1] + 4, filtered_df['yline'].iloc[-1] + 3), verticalalignment = 'top', horizontalalignment = 'center'\
                        , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
            else:
                axs[2].plot(filtered_df['x'], filtered_df['yline'], color =  (0, 0 + iter_*0.1, 1 - iter_*0.1), label = iter_)
                if year_ == 8:
                    axs[2].annotate(str(year_ + 2022), (filtered_df['x'].iloc[-1] + 4, filtered_df['yline'].iloc[-1]), verticalalignment = 'top', horizontalalignment = 'center'\
                        , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
                else:
                    axs[2].annotate(str(year_ + 2022), (filtered_df['x'].iloc[-1] + 4, filtered_df['yline'].iloc[-1] + 2), verticalalignment = 'top', horizontalalignment = 'center'\
                        , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
            iter_+= 1

        plt.suptitle('Opportunistic co-production of $H_{2}$ under a ' + scenario_.lower() + ' cost scenario', fontsize = 14)
        plt.xlabel('Renewable power capacity utilization [$\%$ ]', fontsize = 14)
        plt.ylabel('Green hydrogen [$\%$ ]', fontsize = 14)
        plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)
        plt.subplots_adjust(wspace=0.05, hspace=0)
        # plt.ylim([0,100])
        
        # plt.legend(handles= patches, bbox_to_anchor=(1.05, 1))   
        for i in range(3):
            axs[i].grid(alpha = 0.25)
            axs[i].xaxis.set_ticks_position('both')
            axs[i].yaxis.set_ticks_position('both')
            # axs[i].yaxis.set_minor_locator(AutoMinorLocator())
            axs[i].set_xlim([15,78])
            # axs[i].set_xlabel('Renewable power capacity utilization ', fontsize = 14)
            # axs[i].set_ylabel('Green hydrogen [$\%$ ]', fontsize = 14)
        
    
        plt.show()
    return 
    
for DATA_ in DATA:
    plot_ = split_opportunistic_h2(DATA_)
# %%

def power_schedule(DATA_, year_):
    Solar, Wind, Charge, PSH, CAES = ([] for _ in range(5))
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    scenario_ = SCENARIO[0]
    for d, h in product(D, H):
        Solar.append(DATA_[scenario_][year_]['Sch_P']['HO']['PV'][h][d]['P'])
        Wind.append(DATA_[scenario_][year_]['Sch_P']['HO']['WF'][h][d]['P'])
        Charge.append(DATA_[scenario_][year_]['Sch_S']['HO']['Charge'][h][d]['Inv'])
        PSH.append(DATA_[scenario_][year_]['Sch_S']['HO']['H2O_E'][h][d]['Inv'])
        CAES.append(DATA_[scenario_][year_]['Sch_S']['HO']['Air_C'][h][d]['Inv'])
    fig, ax1 = plt.subplots()
    X_ = np.arange(1,8761)    
    ax1.bar(X_, Wind)
    ax1.bar(X_, Solar, bottom = Wind)
    ax2 = ax1.twinx()
    ax2.plot(X_, Charge, color = 'green')
    plt.show()
    # plt.show()
    # plt.plot(X_, Charge)
    # plt.show()
    # plt.plot(X_, PSH)
    # plt.show()
    # plt.plot(X_, CAES)
    # plt.show()
power_schedule(TEST, 7)

# for year_ in YEAR:    
# power_schedule(CON, year_)

# %%

# %%
# %%

    
# %%



def annual_bgm(DATA_):
    """Plots annual blue and green hydrogen contribution to the overall demand over the entire planning horizon

    Args:
        DATA_ (list): list containing dictionaiers with data 
    """
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    for scenario_ in SCENARIO:
        Green_H2, Blue_H2, MEOH, X_ = ([] for _ in range(4))
        for year_ in YEAR:
            Green_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual']/(365*907.185))
            Blue_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual']/(365*907.185))
            MEOH.append(DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual']/(365*907.185))
            X_.append(int(year_ + 2022))
        width = 0.8
        space = 0.2
        fig, ax = plt.subplots(figsize=(8.27/3, 11.69/3))
        ax.bar(X_, Blue_H2, width, color= 'lightsteelblue', label= 'Blue H2')
        ax.bar(X_, Green_H2, width, bottom= Blue_H2, color='mediumseagreen', label='Green H2')
        ax.bar(X_, MEOH, width, bottom= [sum(x) for x in zip(Blue_H2, Green_H2)] , color='r', label='Methanol')
        plt.title('Total fuels production under a ' + scenario_ + ' cost scenario', fontsize=20)
        plt.xlabel('Year', fontsize=20)
        plt.ylabel('US tonnes', fontsize=20)
        plt.legend(fontsize=20)
        plt.xticks(fontsize= 16)
        plt.yticks(fontsize= 16)
        ax.set_xticks(X_)
        plt.show()    
    return       

for DATA_ in DATA:
    annual_bgm(DATA_)
    
#%%

def h2_cost(DATA:list):
    """Compares the cost of hydrogen production under

    Args:
        DATA (list): list containing dictionaiers with data 
    """
    iter_ = 0
    fig, ax = plt.subplots(figsize=(8.27/3, 11.69/3))
    color = ['lightcoral', 'palegoldenrod', 'yellowgreen']
    width = 0.3
    space = 0.2
    for DATA_ in DATA:
        SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
        scenario_ = SCENARIO[0]
        Y_, X_ = [], []
        
        for year_ in YEAR:
            Y_.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/(DATA_[scenario_][year_]['Net_S']['HO']['H2_C']['S_annual']\
                + DATA_[scenario_][year_]['Net_S']['HO']['H2_L']['S_annual']))
            # Green_H2.append(RESULTS[scenario_][year_]['Total']['HO']['Objective']/(RESULTS[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']))
            X_.append(year_ + 2022)# + iter_*width)    

        # ax.(X_, Y_, width, color = color[iter_], label = scenario_, align='edge')
        ax.plot(X_, Y_, color = color[iter_], label = scenario_)
        ax.scatter(X_, Y_, color = color[iter_])
        
        iter_+= 1
    plt.title('Cost of hydrogen production under different cost scenarios', fontsize=20)
    plt.xlabel('Year', fontsize=20)
    plt.ylabel('$/kg.H2', fontsize=20)
    plt.legend(fontsize=20)
    plt.xticks(fontsize= 16)
    plt.yticks(fontsize= 16)
    plt.grid(axis = 'y', color = '0.85')
    ax.set_xticks(X_)# - (iter_-1)*width for x in X_])
    ax.set_yticks(np.arange(0,7))# - (iter_-1)*width for x in X_])
    plt.show()
    return


h2_cost(DATA)

        
# %%


def annual_mile(DATA_):
    """Plots percentage fuels contribution to meet mileage over the entire planning horizon

    Args:
        DATA_ (list): list containing dictionaiers with data 
    """
    I = ['H2_Sink2', 'H2_Sink1', 'MEFC']
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    for scenario_ in SCENARIO:
        Green_H2, Blue_H2, MEOH,  Green_H2x, Blue_H2x, MEOHx, X_, SUM = ([] for _ in range(8))
        for year_ in YEAR:
            Green_H2x.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual']*0.0315)
            Blue_H2x.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual']*0.0315)
            MEOHx.append(DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual']*0.19)
            SUM.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual']*0.0315 + \
                DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual']*0.0315 + \
                    DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual']*0.19)
            Green_H2 = [a/b*100 for a,b in zip(Green_H2x, SUM)]
            Blue_H2 = [a/b*100 for a,b in zip(Blue_H2x, SUM)]
            MEOH = [a/b*100 for a,b in zip(MEOHx, SUM)]
            X_.append(int(year_ + 2022))
        width = 0.8
        space = 0.2
        fig, ax = plt.subplots(figsize=(8.27/3, 11.69/3))
        ax.bar(X_, Blue_H2, width, color= 'lightsteelblue', label= 'Blue H2')
        ax.bar(X_, Green_H2, width, bottom= Blue_H2, color='mediumseagreen', label='Green H2')
        ax.bar(X_, MEOH, width, bottom= [sum(x) for x in zip(Blue_H2, Green_H2)] , color='r', label='Methanol')
        plt.title('Percentage of miles met by fuel source for a ' + scenario_ + ' cost scenario', fontsize=20)
        plt.xlabel('Year', fontsize=20)
        plt.ylabel('Percentage', fontsize=20)
        plt.legend(fontsize=20)
        plt.xticks(fontsize= 16)
        plt.yticks(fontsize= 16)
        ax.set_xticks(X_)
        plt.show()    
    return       

for DATA_ in DATA:
    annual_mile(DATA_)
    
# %%

def annual_prod(DATA_):
    """Plots percentage fuels contribution to meet mileage over the entire planning horizon

    Args:
        DATA_ (list): list containing dictionaiers with data 
    """
    I = ['H2_Sink2', 'H2_Sink1', 'MEFC']
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    for scenario_ in SCENARIO:
        Green_H2, Blue_H2, MEOH,  Green_H2x, Blue_H2x, MEOHx, X_, SUM = ([] for _ in range(8))
        for year_ in YEAR:
            Green_H2x.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual'])
            Blue_H2x.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual'])
            MEOHx.append(DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual'])
            SUM.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual'] + \
                DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual'] + \
                    DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual'])
            Green_H2 = [a/b*100 for a,b in zip(Green_H2x, SUM)]
            Blue_H2 = [a/b*100 for a,b in zip(Blue_H2x, SUM)]
            MEOH = [a/b*100 for a,b in zip(MEOHx, SUM)]
            X_.append(int(year_ + 2022))
        width = 0.9
        space = 0.2
        fig, ax = plt.subplots(figsize=(8.27/3, 11.69/3))
        ax.bar(X_, Blue_H2, width, color= 'lightsteelblue', label= 'Blue H2')
        ax.bar(X_, Green_H2, width, bottom= Blue_H2, color='mediumseagreen', label='Green H2')
        ax.bar(X_, MEOH, width, bottom= [sum(x) for x in zip(Blue_H2, Green_H2)] , color='r', label='Methanol')
        plt.title('Percentage production by products ' + scenario_ + ' cost scenario', fontsize=20)
        plt.xlabel('Year', fontsize=20)
        plt.ylabel('Percentage', fontsize=20)
        plt.legend(fontsize=20)
        plt.xticks(fontsize= 16)
        plt.yticks(fontsize= 16)
        ax.set_xticks(X_)
        plt.show()    
    return       

for DATA_ in DATA:
    annual_prod(DATA_)
#%%

def annual_bgm(DATA_):
    """Plots annual blue and green hydrogen, and methanol contribution to the overall mileage over the entire planning horizon

    Args:
        DATA_ (list): list containing dictionaiers with data 
    """
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
    for scenario_ in SCENARIO:
        Green_H2, Blue_H2, MEOH, X_ = ([] for _ in range(4))
        for year_ in YEAR:
            Green_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual']*0.0315*10**(-3)/(365))
            Blue_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual']*0.0315*10**(-3)/(365))
            MEOH.append(DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual']*0.19*10**(-3)/(365))
            X_.append(int(year_ + 2022))
        width = 0.6
        space = 0.2
        fig, ax = plt.subplots(figsize=(8.27/3, 11.69/3))
        ax.bar(X_, Blue_H2, width, color= 'lightsteelblue', label= 'Blue H2')
        ax.bar(X_, Green_H2, width, bottom= Blue_H2, color='mediumseagreen', label='Green H2')
        ax.bar(X_, MEOH, width, bottom= [sum(x) for x in zip(Blue_H2, Green_H2)] , color='r', label='Methanol')
        plt.title('Mileage controbution by fuel source under a ' + scenario_ + ' cost scenario', fontsize=20)
        plt.xlabel('Year', fontsize=20)
        plt.ylabel('1000 Miles/day', fontsize=20)
        plt.legend(fontsize=20)
        plt.xticks(fontsize= 16)
        plt.yticks(fontsize= 16)
        ax.set_xticks(X_)
        plt.show()    
    return       
 
for DATA_ in DATA:
    annual_bgm(DATA_)
# %%


def mile_cost(DATA:list):
    """Compares the cost of hydrogen production under

    Args:
        DATA (list): list containing dictionaiers with data 
    """
    iter_ = 0
    fig, ax = plt.subplots(figsize=(8.27/3, 11.69/3))
    color = ['lightcoral', 'palegoldenrod', 'yellowgreen']
    width = 0.3
    space = 0.2
    for DATA_ in DATA:
        SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
        scenario_ = SCENARIO[0]
        Y_, X_ = [], []
        
        for year_ in YEAR:
            Y_.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/((2 + year_*2)*1000*1.5*365))
            # Green_H2.append(RESULTS[scenario_][year_]['Total']['HO']['Objective']/(RESULTS[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']))
            X_.append(year_ + 2022)# + iter_*width)    

        # ax.(X_, Y_, width, color = color[iter_], label = scenario_, align='edge')
        ax.plot(X_, Y_, color = color[iter_], label = scenario_)
        ax.scatter(X_, Y_, color = color[iter_])
        
        iter_+= 1
    plt.title('Cost per mile under different cost scenarios', fontsize=20)
    plt.xlabel('Year', fontsize=20)
    plt.ylabel('$/mile', fontsize=20)
    plt.legend(fontsize=20)
    plt.xticks(fontsize= 16)
    plt.yticks(fontsize= 16)
    plt.grid(axis = 'y', color = '0.85')
    ax.set_xticks(X_)# - (iter_-1)*width for x in X_])
    # ax.set_yticks(np.arange(0,7))# - (iter_-1)*width for x in X_])
    plt.show()
    return

mile_cost(DATA)

# %%

dict_demand = {
    0: 10,
    1: 20,
    2: 40,
    3: 80,
    4: 160,
    5: 320,
    6: 420,
    7: 520,
    8: 620,
    9: 720,
    10: 820
}
list_ = sorted(dict_demand.items())
x, y = zip(*list_)
x = [x + 2021 for x in x] 
plt.plot(x,y)
plt.title('Hydrogen demand')
plt.xlabel('Year')
plt.ylabel('USton/day')
plt.xticks(x)



# %%
y = [(2 + year_*2)*1000 for year_ in YEAR]
x = [year_ + 2021 for year_ in YEAR]
plt.plot(x,y)
plt.title('Mileage demand')
plt.xlabel('Year')
plt.ylabel('miles/day')
plt.xticks(x)

# %%
#%%CAPACITY PLOT

YEAR = np.arange(0,3)
I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'AKE', 'SMRH', 'DAC', 'MEFC', 'EOR', 'AQoff_DAC', 'AQoff_SMR', 'H2_C_c', 'H2_C_d', 'H2_L_c', 'H2_L_d' ]

for DATA_ in DATA:
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()] 
    for scenario_ in SCENARIO:
        for i_ in I:
            input_ = []
            for year_ in YEAR:
                input_.append(DATA_[scenario_][year_]['Net_P']['HO'][i_]['Cap_P'])
            plt.plot(input_)
            plt.title(i_)
            # plt.title(I_labels_['short'][i_])
            plt.show()

#%%Total mileage
for DATA_ in DATA:
    SCENARIO = [scenario_ for scenario_ in DATA_.keys()] 
    for scenario_ in SCENARIO:
            input_ = []
            for year_ in YEAR:
                input_.append(DATA_[scenario_][year_]['Total']['HO']['Objective'])
            plt.plot(input_)
            
            plt.title('Total miles')
            plt.show()
    print(input_)

#%%TEXAS STATE ENERGY PROFILE 2022
size_ = 0.3

#Consumption by source
dict_con_source =   {
    'Coal': 992.7,
    'Hydroelectric Power':13.1,
    'Natural Gas':4795.2,
    'Motor Gasoline excl. Ethanol':1634,
    'Distillate Fuel Oil':1148.7,
    'Jet Fuel':320.5,
    'Hydro-carbon gas liquid':2355,
    'Residual Fuel':165.6,
    'Other Petroleum':1261.5,
    'Nuclear Electric Power':431.2,
    'Biomass':262.4,
    'Other Renewables':795.5,
    # 'Net Electricity Imports':-15.2
    # 'Net Interstate Flow of Electricity':111.5
}

inner_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown',\
    'tab:olive', 'tab:cyan', 'tab:pink', 'tab:gray', 'indianred', 'teal']

# create data
dict_ = dict_con_source
names = [i + ' (' + str(dict_[i]) + ')' for i in dict_.keys()]
size = [dict_[i] for i in dict_.keys()]

# Create a circle at the center of the plot
# my_circle = plt.Circle( (0,0), 0.7, color='white')
# Give color names
plt.pie(size, labels=names, colors = inner_colors, textprops={'fontsize': 14}, wedgeprops={"edgecolor": 'white','linewidth': 3 , 'antialiased': True}, radius=1)
p = plt.gcf()
# p.gca().add_artist(my_circle)
p.set_size_inches(10,10)
# Show the graph
plt.title('Outer - Texas power consumption by source (Trillion Btu) \
    \n Inner - Texas power consumption by sector (%)', fontsize = 16)
# plt.legend(bbox_to_anchor=(1, 1), fontsize = 14)


#Consumption by sector
dict_con_sec =   {
    'Residential': 12.4,
    'Commercial': 11.4,
    'Industrial': 52.7,
    'Transportation': 23.5
}


inner_colors2 = ['powderblue', 'darkseagreen', 'moccasin', 'darksalmon']

# create data
dict_ =  dict_con_sec
names = [i + ' (' + str(dict_[i]) + '%)' for i in dict_.keys()]
size = [dict_[i] for i in dict_.keys()]

patches = []
for i in range(len(inner_colors2)):
    patches.append(mpatches.Patch(color=inner_colors2[i], label=names[i]))

plt.legend(handles= patches, bbox_to_anchor=(1.03, 1))
# Create a circle at the center of the plot
my_circle = plt.Circle( (0,0), 0.7 - size_, color='white')
# Give color names
plt.pie(size,  colors = inner_colors2, textprops={'fontsize': 14, 'color' : 'white'}, wedgeprops={"edgecolor": 'white','linewidth': 3 , 'antialiased': True}, radius = 1 - size_)
p = plt.gcf()
p.gca().add_artist(my_circle)
# p.set_size_inches(10,10)
# Show the graph
# plt.title('Texas power consumption by sector (%)', fontsize = 16)
# plt.legend()
plt.show()

#%%

#Production by source

dict_prod_source = {
    'Coal' :  308.4,
    'Natural Gas - Marketed' :  11224.1,
    'Wood and Waste' :  86.4,
    'Crude Oil' :  10545.4,
    'Nuclear Electric Power' :  431.2,
    'Biofuels' :  67.8,
    'Noncombustible Renewables' :  808.6,
}

dict_  = dict_prod_source
# create data
names = [i + ' (' + str(dict_[i]) + ')' for i in dict_.keys()]
size = [dict_[i] for i in dict_.keys()]


# Create a circle at the center of the plot
my_circle = plt.Circle( (0,0), 0.7, color='white')
# my_circle2 = plt.Circle( (0,0), 0.71, color='white')

# Give color names
plt.pie(size, labels=names, textprops={'fontsize': 14}, radius=1)
p = plt.gcf()
p.set_size_inches(10,10)

p.gca().add_artist(my_circle)
# p.gca().add_artist(my_circle2)

# plt.legend()
# p.set_size_inches(8,8)
plt.title('Texas power production by source (Trillion Btu)', fontsize = 16)
plt.show()





# %%


dict_con_source =   {
    'Coal': 992.7,
    'Hydroelectric':13.1,
    'Natural Gas':4795.2,
    'Motor Gasoline':1634,
    'Distillate Fuel Oil':1148.7,
    'Jet Fuel':320.5,
    'Hydro-carbon gas liq.':2355,
    'Residual Fuel':165.6,
    'Other Petroleum':1261.5,
    'Nuclear':431.2,
    'Biomass':262.4,
    'Other Renewables':795.5,
    # 'Net Electricity Imports':-15.2
    # 'Net Interstate Flow of Electricity':111.5
}

inner_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown',\
    'tab:olive', 'tab:cyan', 'tab:pink', 'tab:gray', 'indianred', 'teal']

# create data
dict_ = dict_con_source
names = [i + ' (' + str(dict_[i]) + ')' for i in dict_.keys()]
size = [dict_[i] for i in dict_.keys()]

# Create a circle at the center of the plot
my_circle = plt.Circle( (0,0), 0.7, color='white')
# Give color names
plt.pie(size, labels=names, colors = inner_colors, textprops={'fontsize': 14}, wedgeprops={"edgecolor": 'white','linewidth': 0 , 'antialiased': True}, radius=1)
p = plt.gcf()
p.gca().add_artist(my_circle)
p.set_size_inches(10,10)
# Show the graph
plt.title('Texas power consumption by source (Trillion Btu)' , fontsize = 16)
# plt.legend(bbox_to_anchor=(1, 1), fontsize = 14)


# %%
dict_con_sec =   {
    'Residential': 12.4,
    'Commercial': 11.4,
    'Industrial': 52.7,
    'Transportation': 23.5
}


inner_colors2 = ['powderblue', 'darkseagreen', 'moccasin', 'darksalmon']

# create data
dict_ =  dict_con_sec
names = [i + ' (' + str(dict_[i]) + '%)' for i in dict_.keys()]
size = [dict_[i] for i in dict_.keys()]

patches = []
for i in range(len(inner_colors2)):
    patches.append(mpatches.Patch(color=inner_colors2[i], label=names[i]))

# plt.legend(handles= patches, bbox_to_anchor=(1, 1), fontsize = 14)
# Create a circle at the center of the plot
my_circle = plt.Circle( (0,0), 0.7, color='white')
# Give color names
plt.pie(size, labels = names, colors = inner_colors2, textprops={'fontsize': 14}, wedgeprops={"edgecolor": 'white','linewidth': 3 , 'antialiased': True}, radius = 1)
p = plt.gcf()
p.gca().add_artist(my_circle)
p.set_size_inches(10,10)
# Show the graph
plt.title('Texas power consumption by sector (%)', fontsize = 16)
# plt.legend()
plt.show()
# %%

def f_conv(i):
    with open('F_CONV.pkl', 'rb') as f:
        data = pkl.load(f)
    D = np.arange(1,366)#Seasons (d) days in this case
    H = np.arange(0,24)#Time (t)
    list_ = []
    for d, h in product(D,H):
        list_.append(data['HO'][i][d][h])
    pos_list = [0, 744, 1344, 2160, 2800, 3624, 4344, 5088, 5832, 6552, 7296, 8016] # hours of the year corresponding to month
    name_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']      
    fig, ax = plt.subplots(figsize=(20,5))
    # plt.figure(figsize=(20,5))
    ax.set_title(I_labels_['long'][i] , fontsize = 14)
    ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
    ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
    ax.plot(list_)
    plt.show()
    return

f_conv('PV')
f_conv('WF')

    
# %%

# %%
