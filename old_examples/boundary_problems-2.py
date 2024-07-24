# %%
"""Evaluates hypothetical pathways to analyze the boundary values of the model
coded in pyomo
uses gurobi solver
input: .pkl files
outputs: .pkl files
Can be submitted as batch file to HPRC

==================================
MILP framework description 
==================================

"""

import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "R. Cory Allen", "Swaminathan Sundar",
               "Marcello Di Martino", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "1.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"


import pandas as pd
import numpy as np
import datetime as datetime
import random
import pickle as pkl
import csv
from pyomo.environ import *
from itertools import product
from functools import reduce
from pyomo.opt import SolverStatus, TerminationCondition
import time
from subprocess import call
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches

# %%

url = 'https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/parquet/2022/ATBe.parquet'
raw_data = pd.read_parquet(url)
raw_data = raw_data.astype(
    dtype={
        'core_metric_key': 'string',
        'core_metric_parameter': 'string',
        'core_metric_case': 'string',
        'crpyears': 'string',
        'technology': 'string',
        'technology_alias': 'string',
        'techdetail': 'string',
        'display_name': 'string',
        'scenario': 'string',
        'units': 'string'
    })
# %%


def atb_gttr(core_metric_parameters, core_metric_case, crpyear, technology, techdetail, scenario):
    df_out = pd.DataFrame()
    for i in core_metric_parameters:
        df = pd.DataFrame(raw_data[
            (raw_data.core_metric_parameter == i) &
            (raw_data.core_metric_case == core_metric_case) &
            (raw_data.crpyears == str(crpyear)) &
            (raw_data.technology == technology) &
            (raw_data.techdetail == techdetail) &
            (raw_data.scenario == scenario)
        ][['value']])
        df = df.rename({'value': i}, axis='columns')
        df = df.reset_index()
        df_out = pd.concat([df_out, df], axis='columns')
        df_out = df_out.loc[:, ~df_out.columns.duplicated()].copy()
        df_out = df_out.fillna(0)
        df_out = df_out.drop(columns=['index'])
    return df_out

# %%


hig_trl_adv = [(1 - i/(31*15)) for i in range(31)]
hig_trl_mod = [(1 - i/(31*10)) for i in range(31)]
hig_trl_con = [(1 - i/(31*5)) for i in range(31)]

med_trl_adv = [(1 - i/(31*40)) for i in range(31)]
med_trl_mod = [(1 - i/(31*30)) for i in range(31)]
med_trl_con = [(1 - i/(31*20)) for i in range(31)]

low_trl_adv = [(1 - i/(31*70)) for i in range(31)]
low_trl_mod = [(1 - i/(31*50)) for i in range(31)]
low_trl_con = [(1 - i/(31*30)) for i in range(31)]

hig_trl_adv_df = pd.DataFrame(
    data={'CAPEX': hig_trl_adv, 'Fixed O&M': hig_trl_adv, 'Variable O&M': hig_trl_adv})
hig_trl_mod_df = pd.DataFrame(
    data={'CAPEX': hig_trl_mod, 'Fixed O&M': hig_trl_mod, 'Variable O&M': hig_trl_mod})
hig_trl_con_df = pd.DataFrame(
    data={'CAPEX': hig_trl_con, 'Fixed O&M': hig_trl_con, 'Variable O&M': hig_trl_con})
med_trl_adv_df = pd.DataFrame(
    data={'CAPEX': med_trl_adv, 'Fixed O&M': med_trl_adv, 'Variable O&M': med_trl_adv})
med_trl_mod_df = pd.DataFrame(
    data={'CAPEX': med_trl_mod, 'Fixed O&M': med_trl_mod, 'Variable O&M': med_trl_mod})
med_trl_con_df = pd.DataFrame(
    data={'CAPEX': med_trl_con, 'Fixed O&M': med_trl_con, 'Variable O&M': med_trl_con})
low_trl_adv_df = pd.DataFrame(
    data={'CAPEX': low_trl_adv, 'Fixed O&M': low_trl_adv, 'Variable O&M': low_trl_adv})
low_trl_mod_df = pd.DataFrame(
    data={'CAPEX': low_trl_mod, 'Fixed O&M': low_trl_mod, 'Variable O&M': low_trl_mod})
low_trl_con_df = pd.DataFrame(
    data={'CAPEX': low_trl_con, 'Fixed O&M': low_trl_con, 'Variable O&M': low_trl_con})
constant_df = pd.DataFrame(
    data={'CAPEX': [1]*31, 'Fixed O&M': [1]*31, 'Variable O&M': [1]*31})


param_list = ['CAPEX', 'Fixed O&M', 'Variable O&M']

moderate_dict = {
    'PV': atb_gttr(core_metric_parameters=param_list, core_metric_case='Market', crpyear=30, technology='UtilityPV', techdetail='Class1', scenario='Moderate'),
    'WF': atb_gttr(core_metric_parameters=param_list, core_metric_case='Market', crpyear=30, technology='LandbasedWind', techdetail='Class1', scenario='Moderate'),
    'LiI': atb_gttr(core_metric_parameters=param_list, core_metric_case='R&D', crpyear=30, technology='Commercial Battery Storage', techdetail='8Hr Battery Storage', scenario='Moderate'),
    'LII_discharge': constant_df,
    'PSH': atb_gttr(core_metric_parameters=param_list, core_metric_case='Market', crpyear=30, technology='Pumped Storage Hydropower', techdetail='NatlClass10', scenario='Moderate'),
    'PSH_discharge': constant_df,
    'ASMR': atb_gttr(core_metric_parameters=param_list, core_metric_case='Market', crpyear=30, technology='Nuclear', techdetail='NuclearSMR', scenario='Moderate'),
    'NPP': atb_gttr(core_metric_parameters=param_list, core_metric_case='Market', crpyear=30, technology='Nuclear', techdetail='Nuclear', scenario='Moderate'),
    'NGCC': atb_gttr(core_metric_parameters=param_list, core_metric_case='Market', crpyear=30, technology='NaturalGas_FE', techdetail='CCCCSHFrame95%', scenario='Conservative'),
    'SMR': hig_trl_mod_df,
    'SMRH': hig_trl_mod_df,
    'AqOff': hig_trl_mod_df,
    'DAC': low_trl_mod_df,
    'PEM': low_trl_mod_df,
    'H2_Comp': med_trl_mod_df,
}

# %%


start_time = time.time()

ng_price = 4.62  # $/MMBtu
water_price = 31.70  # $/5000gallons
power_price = 8  # cents/kWh
ur_price = 42.70  # 250 Pfund U308

# SCENARIO = np.array(['Conservative', 'Moderate', 'Advanced'])
# SCENARIO = np.array(['Conservative'])
SCENARIO = np.array(['Moderate'])
# SCENARIO = np.array(['Advanced'])

start_year = 2022
end_year = 2022
YEAR = np.arange(start_year - 2022, end_year - 2021)


class opt:
    """
    choose how to optimize the model
    """

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name


class scenario:
    """
    choose a cost scenario
    """

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name


class process:
    """
    creates a process object
    """

    def __init__(self, name: str, scale_up: float, near: bool, mid: bool, far: bool,
                 prod_max: float, prod_min: float, q45: bool, tax_cred: dict, gwp: float, block: str, label: str):
        self.name = name
        self.scale_up = scale_up
        self.near = near
        self.mid = mid
        self.far = far
        self.prod_max = prod_max
        self.prod_min = prod_min
        self.q45 = q45
        self.tax_cred = tax_cred
        self.gwp = gwp
        self.block = block
        self.label = label

    def __repr__(self):
        return self.name


class resource:
    """
    creates a resource object
    """

    def __init__(self, name: str, near: bool, mid: bool, far: bool, sell: bool, q45: bool,
                 store_max: float, store_min: float, consumption_max: float, loss: float, revenue: float, tax_cred: dict,
                 purc_cost: float, mile: float, ghg: float, label: str):

        self.name = name
        self.near = near
        self.mid = mid
        self.far = far
        self.sell = sell
        self.q45 = q45
        self.store_max = store_max
        self.store_min = store_min
        self.consumption_max = consumption_max
        self.loss = loss
        self.revenue = revenue
        self.tax_cred = tax_cred
        self.purc_cost = purc_cost
        self.mile = mile
        self.ghg = ghg
        self.label = label

    def __repr__(self):
        return self.name


LiI_c = process('LiI_c', 80, True, True, True, 1000, 0, False, {
                'near': 0, 'mid': 0, 'far': 0}, 112000, 'power_storage', 'Lithium-ion battery')
LiI_d = process('LiI_d', 80, True, True, True, 1000, 0, False, {
                'near': 0, 'mid': 0, 'far': 0}, 0, 'power_storage', 'Lithium-ion battery discharge')
CAES_c = process('CAES_c', 80, False, True, True, 1000, 0, False, {
                 'near': 0, 'mid': 0, 'far': 0}, 0, 'power_storage', 'Compressed air energy storage (CAES)')
CAES_d = process('CAES_d', 80, False, True, True, 1000, 0, False, {
                 'near': 0, 'mid': 0, 'far': 0}, 0, 'power_storage', 'Compressed air energy storage (CAES) discharge')
PSH_c = process('PSH_c', 80, True, True, True, 1000, 0, False, {
                'near': 0, 'mid': 0, 'far': 0}, 0, 'power_storage', 'Pumped storage hydropower (PSH)')
PSH_d = process('PSH_d', 80, True, True, True, 1000, 0, False, {
                'near': 0, 'mid': 0, 'far': 0}, 0, 'power_storage', 'Pumped storage hydropower (PSH) discharge')


# PV = process('PV', True, True, True, 2.5*10**3, 'power_generation')
# WF = process('WF', True, True, True, 2.5*10**3, 'power_generation')
PV = process('PV', 10**9, True, True, True, 150, 0.25, False,
             {'near': 0, 'mid': 0, 'far': 0}, 53, 'power_generation', 'Solar photovoltaics (PV) array')
WF = process('WF', 10**9, True, True, True, 150, 0.25, False,
             {'near': 0, 'mid': 0, 'far': 0}, 10.4, 'power_generation', 'Wind mill array')
AKE = process('AKE', 10**9, True, True, True, 150, 5, False, {'near': 0, 'mid': 0, 'far': 0}, 0.61*19.474,
              'material_production', 'Alkaline water electrolysis (AWE)')  # 20.833 MW required to produce 1000t/day.H2
SMRH = process('SMRH', 10**9, True, True, True, 3*10**4, 10**3, False,
               {'near': 0, 'mid': 0, 'far': 0}, 0, 'material_production', 'Steam methane reforming + CCUS')
SMR = process('SMR', 10**9, True, True, True, 3*10**4, 10**3, False,
              {'near': 0, 'mid': 0, 'far': 0}, 0, 'material_production', 'Steam methane reforming')
ASMR = process('ASMR', 10**9, True, True, True, 3*10**4, 10**3, False,
               {'near': 0, 'mid': 0, 'far': 0}, 9.1, 'power_generation', 'Small modular reactors (SMRs)')

# AKE = process('AKE', True, True, True, 10**5, 'material_production')
# SMRH = process('SMRH', True, True, True, 10**5, 'material_production')
H2_C_c = process('H2_C_c', 10**9, True, True, True, 10**5, 0, False,
                 {'near': 0, 'mid': 0, 'far': 0}, 0, 'material_storage', 'Hydrogen local storage (Compressed)')
H2_C_d = process('H2_C_d', 10**9, True, True, True, 10**5, 0, False,
                 {'near': 0, 'mid': 0, 'far': 0}, 0, 'material_storage', 'Hydrogen local storage (Compressed) discharge')
H2_L_c = process('H2_L_c', 10**9, True, True, True, 10**5, 0, False,
                 {'near': 0, 'mid': 0, 'far': 0}, 0, 'material_storage', 'Hydrogen geological sequestration')
H2_L_d = process('H2_L_d', 10**9, True, True, True, 10**5, 0, False,
                 {'near': 0, 'mid': 0, 'far': 0}, 0, 'material_storage', 'Hydrogen geological sequestration discharge')
SMRM = process('SMRM', 10**9, True, True, True, 10**5, 100, False,
               {'near': 0, 'mid': 0, 'far': 0}, 0, 'material_production', 'Methanol SMR')
MEFC = process('MEFC', 0.20*2058, False, True, True, 10000, 100,  True,
               {'near': 0.03177, 'mid': 0.05, 'far': 0.05}, 0, 'material_production', 'Catalytic methanol production')  # 10,000t/y
DAC = process('DAC', 0.20*4*10**5, False, True, True, 10**5, 100,  True,
              {'near': 0, 'mid': 0, 'far': 0}, 0, 'CCUS', 'Direct air capture')
DOWC = process('DOWC', 0.20*10**5, False, True, True, 10**5, 100, False,
               {'near': 0, 'mid': 0, 'far': 0},  0, 'CCUS', 'Depleted oil wells')
EOR = process('EOR', 10**9, True, True, False, 10**5, 1000, True,
              {'near': 0.02022, 'mid': 0.035, 'far': 0.035}, 0, 'CCUS', 'CO2-Enhanced oil recovery')
AQoff_SMR = process('AQoff_SMR', 0.40*10**5,  False, True, True, 10**5, 1000, True,
                    {'near': 0.03177, 'mid': 0.05, 'far': 0.05}, 0, 'CCUS', 'Offshore aquifer CO2 sequestration (SMR)')
AQoff_DAC = process('AQoff_DAC', 0.40*10**5, False, True, True, 10**5, 1000, True,
                    {'near': 0.03177, 'mid': 0.05, 'far': 0.05}, 0, 'CCUS', 'Offshore aquifer CO2 sequestration (DAC)')
Grid = process('Grid', 10**12, True, True, True, 10**10, 0, False,
               {'near': 0, 'mid': 0, 'far': 0}, 0, 'power_generation', 'Grid electricity')
H2_Sink1 = process('H2_Sink1', 10**15, True, True, True, 10**8, 0,  False,
                   {'near': 0, 'mid': 0, 'far': 0}, 0, 'dummy', 'Blue Hydrogen production')
H2_Sink2 = process('H2_Sink2', 10**15, True, True, True, 10**8, 0, False,
                   {'near': 0, 'mid': 0, 'far': 0}, 0, 'dummy', 'Green Hydrogen production')


# {'CAPEX':, 'Fixed O&M':, 'Variable O&M': }
dict_cost2 = {'PV': {'CAPEX': 1333.26, 'Fixed O&M': 0, 'Variable O&M': 22.62},
              'WF': {'CAPEX': 1462.0, 'Fixed O&M': 0, 'Variable O&M': 43.0},
              'SMRH': {'CAPEX': 252, 'Fixed O&M': 945, 'Variable O&M': 0.0515},
              'SMR': {'CAPEX': 240, 'Fixed O&M': 800, 'Variable O&M': 0.03},
              'EOR': {'CAPEX': 0.0001, 'Fixed O&M': 0, 'Variable O&M': 0},
              'H2_Sink1': {'CAPEX': 0.0001, 'Fixed O&M': 0, 'Variable O&M': 0},
              'H2_Sink2': {'CAPEX': 0.0001, 'Fixed O&M': 0, 'Variable O&M': 0},
              'H2_C_c': {'CAPEX': 0.0001, 'Fixed O&M': 0, 'Variable O&M': 0},
              'H2_C_d': {'CAPEX': 0.0001, 'Fixed O&M': 0, 'Variable O&M': 0},
              'AKE': {'CAPEX': 1.55*10**3, 'Fixed O&M': 0, 'Variable O&M': 40},
              'Grid': {'CAPEX': 1032, 'Fixed O&M': 0, 'Variable O&M': 9},
              # https://www.davidpublisher.com/Public/uploads/Contribute/619af4f9dffe4.pdf
              'ASMR': {'CAPEX': 3000, 'Fixed O&M': 0, 'Variable O&M': 20}
              }

Charge = resource('Charge', True, True, True, False, False, 400, 1, 0, 8.9286*10 **
                  (-5), 0, {'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'Battery energy storage (MW)')
Air_C = resource('Air_C', False, True, True, False, False, 400, 50, 0, 0, 0, {
                 'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'CAES energy storage (MW)')
H2O_E = resource('H2O_E', True, True, True, False, False, 400, 50, 0, 0, 0, {
                 'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'PSH energy storage (MW)')
Solar = resource('Solar', True, True, True, False, False, 0, 0, 10**20,
                 0, 0, {'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'Solar Power (MW)')
Wind = resource('Wind', True, True, True, False, False, 0, 0, 10**20,
                0, 0, {'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'Wind Power (MW)')

Uranium = resource('Uranium', True, True, True, False, False, 0, 0,  10**20, 0,
                   0, {'near': 0, 'mid': 0, 'far': 0}, ur_price/(250/2), 0, 0, 'Uranium (kg)')
Lithium = resource('Lithium', True, True, True, False, False, 0, 0,  10 **
                   20, 0, 0, {'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'Lithium (kg)')


# Power = resource('Power', True, True, True, True, False, 0, 0, 0, 0, {'near': 0, 'mid':0, 'far':0}, 0, (10**6)/0.2167432, 0, 'Renewable power generated (MW)')
H2_C = resource('H2_C', True, True, True, True, False, 10**10, 0, 0, 0.025/24, 2,
                {'near': 0, 'mid': 0, 'far': 0}, 0, 1/(0.1180535*1.60934), 0.482803, 'Hydrogen - Local storage (kg)')
H2_L = resource('H2_L', True, True, True, True, False, 10**10, 0, 0, 0, 2,
                {'near': 0, 'mid': 0, 'far': 0}, 0, 1/(0.1180535*1.60934), 0.482803, 'Hydrogen - Geological storage (kg)')
H2 = resource('H2', True, True, True, False, False, 0, 0, 0, 0, 0, {
              'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'Hydrogen')
H2_B = resource('H2_B', True, True, True, False, False, 0, 0,  0, 0, 0, {
                'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'Blue hydrogen (kg)')
H2_G = resource('H2_G', True, True, True, False, False, 0, 0, 0, 0, 0, {
                'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'Green hydrogen (kg)')
# H2O = resource('H2O', True, True, True, False, False, 0, 0, 10**20, 0, 0,
#                {'near': 0, 'mid': 0, 'far': 0}, water_price/(5000*3.7854), 0, 0, 'Water (kg)')
H2O = resource('H2O', True, True, True, False, False, 0, 0, 10**20, 0, 0,
               {'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'Water (kg)')
O2 = resource('O2', True, True, True, True, False, 0, 0,  0, 0.07, 0, {
              'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'Oxygen (kg)')
CH4 = resource('CH4', True, True, True, False, False, 0, 0,  10**20, 0, 0,
               {'near': 0, 'mid': 0, 'far': 0}, ng_price/(28.32*0.68), 0, 0, 'Methane (kg)')
# CH4 price from compressed NG: $/(1000ft3) = $/(1000 ft3 * 0.0283168 m3/ft3 * 128.2 kg/m3) = $/kg
CO2 = resource('CO2', True, True, True, False, False, 0, 0, 0, 0, 0, {
               'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'Carbon dioxide (kg)')
CO2_DAC = resource('CO2_DAC', False, True, True, False, False, 0, 0, 0, 0, 0, {
                   'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'Carbon dioxide - captured (kg)')
# CO2_DOW = resource('CO2_DOW', False, True, True, False, True, 10**7, 0, 0, {'near': 0.03177, 'mid':0.05, 'far':0}, 0, 0, 0)
CO2_AQoff = resource('CO2_AQoff', False, True, True, False, True, 10**10, 100, 0,  0, 0,
                     {'near': 0.03177, 'mid': 0.05, 'far': 0}, 0, 0, 0, 'Carbon dioxide - sequestered (kg)')
CO2_EOR = resource('CO2_EOR', True, True, False, False, True, 10**10, 0, 0, 0, 0,
                   {'near': 0.02022, 'mid': 0.035, 'far': 0}, 0, 0, 0, 'Carbon dioxide - EOR (kg)')
CH3OH = resource('CH3OH', True, True, True, True, False, 0, 0, 0, 0, 0.5, {
                 'near': 0.03177*1.2143, 'mid': 0.05*1.2143, 'far': 0}, 0, 1/(0.0195508*1.60934), 0.0917, 'Methanol (kg)')
# Power_Gr = resource('Power_Gr', True, True, True, False, False, 0, 0, 10**20, 0, 0,
#                     {'near': 0, 'mid': 0, 'far': 0}, power_price*(10**(-2))*10**3, 0, 0, 'Grid electricity (MW)')
Power_Gr = resource('Power_Gr', True, True, True, False, False, 0, 0, 10**20, 0, 0,
                    {'near': 0, 'mid': 0, 'far': 0}, power_price*(10**(-2)), 0, 0, 'Grid electricity (MW)')
CO2_Vent = resource('CO2_Vent', True, True, True, True, False, 0, 0,  0, 0, 0, {
                    'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'Carbon dioxide - Vented (kg)')
# WO SMRM and DOWC
# I = [LiI_c, LiI_d, CAES_c, CAES_d, PSH_c, PSH_d, PV, WF, AKE, SMRH, H2_C_c, H2_C_d,  H2_L_c, H2_L_d, EOR, H2_Sink1, H2_Sink2, AQoff_DAC, AQoff_SMR, MEFC, DAC]
# J = [Charge, Air_C, H2O_E, Solar, Wind, Power, H2_C, H2_L, H2, H2_B, H2_G, H2O, O2, CH4, CO2, CO2_DAC, CO2_AQoff, CO2_EOR, CH3OH, CO2_Vent]
# Only blue hydrogen
# I = [LiI_c, LiI_d, CAES_c, CAES_d, PSH_c, PSH_d, PV, WF, SMRH, H2_C_c, H2_C_d,  H2_L_c, H2_L_d, EOR, AQoff_SMR, H2_Sink1, H2_Sink2 ] #AQoff_DAC, MEFC, AKE, DAC
# Only green hydrogen
# I = [LiI_c, LiI_d, CAES_c, CAES_d, PSH_c, PSH_d, PV, WF, AKE,  H2_C_c, H2_C_d,  H2_L_c, H2_L_d, EOR,  H2_Sink1, H2_Sink2 ] #AQoff_DAC, MEFC, AKE, DAC, SMRH, AQoff_SMR

# =================================================================================
# Hypothetical pathways are developed through the combination of the following sets
# Power generation = {Wind, Solar, Nuclear, Natural gas}
# Production technology = {Steam methane reforming (SMR),
#                          SMR + carbon capture (CC),
#                          Alkaline water electrolysis (AWE)}
# Energy vector = {Hydrogen, Electricity}
# Hydrogen for transport applications is utilized through hydrogen fuel cells
# Electricity through EVs
# =================================================================================


demand_ = 2.28227*10**(11)  # total miles driven in TX

# imports
FILES = ['F_CONV', 'COST']
for file_ in FILES:
    with open(file_ + '.pkl', 'rb') as f_:
        locals()[file_] = pkl.load(f_)

dict_f_conv = F_CONV
dict_cost = COST


tx_miles = opt('tx_miles')

conservative = scenario('Conservative')
moderate = scenario('Moderate')
advanced = scenario('Advanced')

# CHOOSE TO RUN MODEL TILL THE END OF YEAR


m = ConcreteModel()

# ===========================================================================================
# SETS
# ===========================================================================================

# ======================= GLOBAL ================================
D = np.arange(1, 366)  # Seasons (d) days in this case
H = np.arange(0, 24)  # Time (t)
A = np.array(['HO'])  # Locations (a)
# U = np.array(['on', 'off'])#Modes (u)
# Production capacity gradient for retiring/introducing newer technologies

BigM = 2  # A very large (small) number
J_demand = np.array(['H2_C', 'H2_L'])

conv = pd.read_csv('conversion.csv', index_col=0)
conv = conv.dropna(axis='rows')
conv = conv.transpose()
dict_conversion = conv.to_dict()

# ===========================================================================================
# MODEL
# ===========================================================================================


def hccus(m_: ConcreteModel(), scenario_: str, year_: int, opt_: str, solver_: str):
    """hccus solves a planning and scheduling MILP problem for the production of hydrogen and CCUS

    Args:
        m_ ([type]): recieves pyomo concrete model as input
        scenario_ (str): choose between different cost scenarios
        year_ (int): year within the planning period
        opt_ (str): select objective 
        binaries_ (dict): recieves binaries from previous period
        solver_ (str): choose solver 
        inv_cycle_ (dict): recieves inventory levels from end of previous period
        capacity_cycle_ (dict): recieves capacity from previous period

    Returns:
        RESULTS_[dict]: a dictionary with results 
        BINARY[dict]: a dictionary with the binaries from the planning problem 
        INV_[dict]: a dictionary with the inventory levels for the end of the year
    """

    print('\n==========================================================================================================')
    print('Optimizing ' + opt_.replace('_', ' ') + ' in a(n) ' +
          scenario_.lower() + ' cost scenario for the year ' + str(2022 + year_))

    Y = [year_]  # current year

    if year_ <= 3:
        period_ = 'near'
        II = [i for i in I if i.near is True]
        JJ = [j for j in J if j.near is True]

    elif year_ >= 4 and year_ <= 10:
        period_ = 'mid'
        II = [i for i in I if i.mid is True]
        JJ = [j for j in J if j.mid is True]

    else:
        period_ = 'far'
        II = [i for i in I if i.far is True]
        JJ = [j for j in J if j.far is True]

    I_ = [i.name for i in II]
    J_ = [j.name for j in JJ]
    I_mp = [i.name for i in II if i.block in [
        'material_production', 'power_generation']]
    I_Q45 = [i.name for i in II if i.q45 is True]
    J_nosell = [j.name for j in JJ if j.sell is False]
    J_sell = [j.name for j in JJ if j.sell is True]
    J_Q45 = [j.name for j in JJ if j.q45 is True]
    J_store = [j.name for j in JJ if j.store_max > 0]
    J_nostore = [j.name for j in JJ if j.store_max == 0]
    J_mile = [j.name for j in JJ if j.mile > 0]
    J_ghg = [j.name for j in JJ if j.ghg > 0]
    I_labels = [i.label for i in II]
    J_labels = [j.label for j in JJ]
    I_power = [i.name for i in II if i.block in ['power_storage']]

    I_nopower = [i for i in I_ if i not in I_power]

    # print(J_mile)
    # print(J_sell)
    # print(J_nosell)

    # ===========================================================================================
    # SETS
    # ===========================================================================================

    if year_ > YEAR[0]:
        for a in A:
            I_int = np.intersect1d(
                np.array([*BINARY[scenario_][year_-1]['P'][a]]), I_)
            print(I_int)
            J_int = np.intersect1d(
                np.array([*BINARY[scenario_][year_-1]['S'][a]]), J_)
            J_int = np.intersect1d(J_int, J_store)
            m.I_int = Set(
                initialize=I_int, doc='intersection of processes between current and past year')
            m.J_int = Set(
                initialize=J_int, doc='intersection of resources between current and past year')

    m.I = Set(initialize=I_, doc='active processes')
    m.I_mp = Set(initialize=I_mp, doc='processes for material production')
    m.I_Q45 = Set(initialize=I_Q45,
                  doc='Processes (i) that get 45Q carbon credits when produced')
    m.I_power = Set(initialize=I_power,
                    doc='Dummy processes for power storage')
    m.I_nopower = Set(initialize=I_nopower,
                      doc='Not dummy processes for power storage')
    m.J = Set(initialize=J_, doc='active resources')
    m.J_nosell = Set(initialize=J_nosell, doc='resources that cannot be sold')
    m.J_sell = Set(initialize=J_sell, doc='resources that can be sold')
    m.J_Q45 = Set(initialize=J_Q45,
                  doc='resource that get 45Q carbon credits when produced')
    m.J_store = Set(initialize=J_store, doc='resources that can be stored')
    m.J_nostore = Set(initialize=J_nostore, doc='resources that can be stored')
    m.J_mile = Set(initialize=J_mile,
                   doc='resources that can be used as transportation fuels')
    m.J_ghg = Set(initialize=J_ghg, doc='GHG emitting transport fuel')
    m.Y = Set(initialize=Y, doc='year of the planning period')
    m.D = Set(initialize=D, doc='Seasons 1 to 365')
    m.H = Set(initialize=H, doc='Hours 1 to 24')
    m.A = Set(initialize=A, doc='locations')

    # =============================
    # VARIABLES
    # =============================
    # =========================Non-negative========================
    m.Opex_fix = Var(m.A, m.I, m.Y, within=NonNegativeReals,
                     doc='fixed operational expenditure of each process (i)')
    m.Opex_var = Var(m.A, m.I, m.Y, within=NonNegativeReals,
                     doc='variable operational expenditure of each process (i)')
    m.Capex = Var(m.A, m.I, m.Y, within=NonNegativeReals,
                  doc='capital expenditure on process (i)')
    m.P_annual = Var(m.A, m.I, m.Y, within=NonNegativeReals,
                     doc='Annual production for each resource in each location')
    m.Cap_P = Var(m.A, m.I, m.Y, within=NonNegativeReals,
                  doc='production (MW or kg/h) capacity of process (i) at location (a)')
    m.Opex = Var(m.A, m.I, m.Y, within=NonNegativeReals,
                 doc='operational expenditure of each process (i)')
    m.GWP = Var(m.A, m.I, m.Y, within=NonNegativeReals,
                doc='GWP (kg.CO2) of facility (i) for rated capacity')
    m.GWP_total = Var(m.A, m.Y, within=NonNegativeReals,
                      doc='Total GWP (kg.CO2) of the system')

    m.B_total = Var(m.A, m.J, m.Y, within=NonNegativeReals,
                    doc='Total expenditure in purchasing resource (j) in location (a)')
    m.S_annual = Var(m.A, m.J, m.Y, within=NonNegativeReals,
                     doc='Annual sales of each resource in each location')
    m.C_annual = Var(m.A, m.J, m.Y, within=NonNegativeReals,
                     doc='Annual consumption of each resource in each location')
    m.GHG_total = Var(m.A, m.J, m.Y, within=NonNegativeReals,
                      doc='Annual GHG emissions due to mobility')
    m.Mile_total = Var(m.A, m.Y, within=NonNegativeReals, doc='Annual mileage')
    m.Credit = Var(m.A, m.I, m.Y, within=NonNegativeReals,
                   doc='carbon credit from process (i)')
    m.Cap_S = Var(m.A, m.J_store, m.Y, within=NonNegativeReals,
                  doc='storage capacity (MW or kg) for resource (j) at location (a)')

    m.Opex_fix_total = Var(m.A, m.Y, within=NonNegativeReals,
                           doc='annualized fixed operational expenditure ($)')
    m.Opex_var_total = Var(m.A, m.Y, within=NonNegativeReals,
                           doc='annualized variable operational expenditure ($)')
    m.Opex_total = Var(m.A, m.Y, within=NonNegativeReals,
                       doc='annualized total operational expenditure ($)')
    m.Capex_total = Var(m.A, m.Y, within=NonNegativeReals,
                        doc='total annual capital expenditure at location (a)')
    m.Credit_total = Var(m.A, m.Y, within=NonNegativeReals,
                         doc='annualized total carbon credit')

    # m.Revenue = Var(m.A, m.J_sell, m.Y, doc = 'profit made from selling resource (j)')
    # m.Revenue_total = Var(m.A, m.Y) #annualized total profit
    m.P = Var(m.A, m.I,  m.H, m.D, m.Y, within=NonNegativeReals,
              doc='amount ($) of resource produced by process (i) at location (a) in time period(t) of season (h)')

    m.B = Var(m.A, m.J, m.H, m.D, m.Y, within=NonNegativeReals,
              doc='amount ($) spent on purchase of resource (j)')
    m.C = Var(m.A, m.J, m.H, m.D, m.Y, within=NonNegativeReals,
              doc='amount ($)  of  resource  (j)  consumed  at  location  (a)  in  time  period  (t)  of  season  (h)')
    # m.P_M = Var(m.A, m.I, m.U, m.H, m.D, m.Y, within = NonNegativeReals)
    m.S = Var(m.A, m.J, m.H, m.D, m.Y, within=NonNegativeReals,
              doc='amount ($) of resource (j) discharged at location (a) in time period (t) of season (h)')
    m.Inv = Var(m.A, m.J, m.H, m.D, m.Y, within=NonNegativeReals,
                doc='inventory level of resource (j) at location (a) in time period (t) of season (h)')

    # =========================Binary=========================
    m.X_P = Var(m.A, m.I, m.Y, within=Binary,
                doc='equals 1 if process (i) is built at location (a) in planning period')
    m.X_S = Var(m.A, m.J_store, m.Y, within=Binary,
                doc='equals 1 if storage facility for resource (j) is built at location (a) in planning period')
    # m.Y_P = Var(m.A, m.I, m.U, m.H, m.D, m.Y, within = Binary)

    # =========================Global=========================
    m.Cost_Total = Var(m.Y, doc='annualized total cost to system')
    # print('parameters, sets, variables defined')

    # =============================
    # CONSTRAINTS
    # =============================

    # # ======================= NETWORK DESIGN  ==================================*GRAD_PROD[y][i]*
    # #PRODUCTION CAPACITY

    def Prod_Cap_rule(m, a, i, y):
        return m.Cap_P[a, i, y] <= next((i_.scale_up for i_ in I if i_.name == i))
    m.Prod_Cap_cons = Constraint(
        m.A, m.I, m.Y, rule=Prod_Cap_rule, doc='Constrains production capacity to max or 0')

    # ======================= RESOURCE BALANCE ==================================
    # NAMEPLATE PRODUCTION CAPACITY UPPER

    def Nameplate_Prod_UB_rule(m, a, i, h, d, y):
        return m.P[a, i, h, d, y] <= m.Cap_P[a, i, y]*dict_f_conv[a][i][d][h]
    m.Nameplate_Prod_UB_cons = Constraint(
        m.A, m.I, m.H, m.D, m.Y, rule=Nameplate_Prod_UB_rule, doc='Constrains production within capacity')

    # NAMEPLATE STORAGE CAPACITY UPPER

    def Nameplate_Store_UB_rule(m, a, j, h, d, y):
        return m.Inv[a, j, h, d, y] <= m.Cap_S[a, j, y]
    m.Nameplate_Store_UB_cons = Constraint(
        m.A, m.J_store, m.H, m.D, m.Y, rule=Nameplate_Store_UB_rule, doc='Constrains storage within capacity')

    def Nameplate_Store_UB_rule2(m, a, j, h, d, y):
        return m.Inv[a, j, h, d, y] == 0
    m.Nameplate_Store_UB_cons2 = Constraint(
        m.A, m.J_nostore, m.H, m.D, m.Y, rule=Nameplate_Store_UB_rule2, doc='Constrains storage within capacity2')

    # RESOURCE AVAILABILITY

    def Resource_Avail_rule(m, a, j, h, d, y):
        return m.C[a, j, h, d, y] <= next((j_.consumption_max for j_ in J if j_.name == j))
    m.Resource_Avail_cons = Constraint(
        m.A, m.J, m.H, m.D, m.Y, rule=Resource_Avail_rule, doc='Constrains resource consumption')

    # INVENTORY BALANCE

    def Inventory_Balance_rule(m, a, j, h, d, y):
        if (h == 0) and (d == 1) and (year_ == YEAR[0]):
            # if (h == 0) and (d == 1):
            return m.Inv[a, j, h, d, y] == \
                + sum(dict_conversion[i][j]*m.P[a, i, h, d, y] for i in m.I)\
                + m.C[a, j, h, d, y] - m.S[a, j, h, d, y]
        elif (h == 0) and (d == 1) and (year_ > YEAR[0]):
            return m.Inv[a, j, h, d, y] == (1 - next((j_.loss for j_ in J if j_.name == j)))*INV[a][j]\
                + sum(dict_conversion[i][j]*m.P[a, i, h, d, y] for i in m.I)\
                + m.C[a, j, h, d, y] - m.S[a, j, h, d, y]
        elif (d > 1) and (h == 0):
            return m.Inv[a, j, h, d, y] == (1 - next((j_.loss for j_ in J if j_.name == j)))*m.Inv[a, j, 23, d-1, y]\
                + sum(dict_conversion[i][j]*m.P[a, i, h, d, y] for i in m.I)\
                + m.C[a, j, h, d, y] - m.S[a, j, h, d, y]
        else:
            return m.Inv[a, j, h, d, y] == (1 - next((j_.loss for j_ in J if j_.name == j)))*m.Inv[a, j, h-1, d, y] \
                + sum(dict_conversion[i][j]*m.P[a, i, h, d, y] for i in m.I)\
                + m.C[a, j, h, d, y] - m.S[a, j, h, d, y]
    m.Inventory_Balance_cons = Constraint(
        m.A, m.J, m.H, m.D, m.Y, rule=Inventory_Balance_rule, doc='Balances and cycles inventory between consecutive periods')

    # NO SELL RULE

    def No_Sell_rule(m, a, j, h, d, y):
        return m.S[a, j, h, d, y] == 0
    m.No_Sell_cons = Constraint(m.A, m.J_nosell, m.H, m.D, m.Y, rule=No_Sell_rule,
                                doc='Restricts the sale of items that cannot be sold')

    # ANNUAL SALES
    def Annual_Sales_rule(m, a, j, y):
        return m.S_annual[a, j, y] == sum(sum(m.S[a, j, h, d, y] for h in m.H) for d in m.D)
    m.Annual_Sales_cons = Constraint(
        m.A, m.J, m.Y, rule=Annual_Sales_rule, doc='Calculates the annual sale of each resource')

    # ANNUAL PURCHASE
    def Annual_Purch_rule(m, a, j, y):
        return m.C_annual[a, j, y] == sum(sum(m.C[a, j, h, d, y] for h in m.H) for d in m.D)
    m.Annual_Purch_cons = Constraint(
        m.A, m.J, m.Y, rule=Annual_Purch_rule, doc='Calculates the annual purchase of each resource')

    # ANNUAL PRODUCTION
    def Annual_Prod_rule(m, a, i, y):
        return m.P_annual[a, i, y] == sum(sum(m.P[a, i, h, d, y] for h in m.H) for d in m.D)
    m.Annual_Prod_cons = Constraint(
        m.A, m.I, m.Y, rule=Annual_Prod_rule, doc='Calculates the annual production of each resource')

    # ======================= COSTING FUNCTIONS ==================================

    # #ANNUAL CAPEX
    # def Capex_rule(m, a, i ,y):
    #      return m.Capex[a, i, y] == 0.05*dict_cost[scenario_][year_][i]['CAPEX']*m.Cap_P[a, i, y]
    # m.Capex_cons = Constraint(m.A, m.I, m.Y, rule = Capex_rule, doc = 'Calculates capital expenditure for each process (i)')

    # #TOTAL ANNUAL CAPEX
    # def Capex_total_rule(m, a ,y):
    #      return m.Capex_total[a, y] == sum(m.Capex[a, i, y] for i in m.I)
    # m.Capex_total_cons = Constraint(m.A, m.Y, rule = Capex_total_rule, doc = 'Calculates capital expenditure')

    # #ANNUAL FIXED OPEX
    # def Opex_fix_rule(m, a, i, y):
    #     return m.Opex_fix[a, i, y] == dict_cost[scenario_][year_][i]['Fixed O&M']*m.Cap_P[a, i, y]
    # m.Opex_fix_cons = Constraint(m.A, m.I, m.Y, rule = Opex_fix_rule, doc = 'Calculates operational expenditure for each process (i)')

    # #ANNUAL VARIABLE OPEX
    # def Opex_var_rule(m, a, i, y):
    #     return m.Opex_var[a, i, y] == dict_cost[scenario_][year_][i]['Variable O&M']*m.P_annual[a, i, y]
    # m.Opex_var_cons = Constraint(m.A, m.I, m.Y, rule = Opex_var_rule, doc = 'Calculates operational expenditure for each process (i)')

    # ANNUAL CAPEX
    def Capex_rule(m, a, i, y):
        return m.Capex[a, i, y] == 0.05*dict_cost2[i]['CAPEX']*m.Cap_P[a, i, y]
    m.Capex_cons = Constraint(m.A, m.I, m.Y, rule=Capex_rule,
                              doc='Calculates capital expenditure for each process (i)')

    # TOTAL ANNUAL CAPEX
    def Capex_total_rule(m, a, y):
        return m.Capex_total[a, y] == sum(m.Capex[a, i, y] for i in m.I)
    m.Capex_total_cons = Constraint(
        m.A, m.Y, rule=Capex_total_rule, doc='Calculates capital expenditure')

    # ANNUAL FIXED OPEX

    def Opex_fix_rule(m, a, i, y):
        return m.Opex_fix[a, i, y] == dict_cost2[i]['Fixed O&M']*m.Cap_P[a, i, y]
    m.Opex_fix_cons = Constraint(m.A, m.I, m.Y, rule=Opex_fix_rule,
                                 doc='Calculates operational expenditure for each process (i)')

    # ANNUAL VARIABLE OPEX
    def Opex_var_rule(m, a, i, y):
        return m.Opex_var[a, i, y] == dict_cost2[i]['Variable O&M']*m.P_annual[a, i, y]
    m.Opex_var_cons = Constraint(m.A, m.I, m.Y, rule=Opex_var_rule,
                                 doc='Calculates operational expenditure for each process (i)')

    # ANNUAL OPEX
    def Opex_rule(m, a, i, y):
        return m.Opex[a, i, y] == m.Opex_var[a, i, y] + m.Opex_fix[a, i, y]
    m.Opex_cons = Constraint(m.A, m.I, m.Y, rule=Opex_rule,
                             doc='Calculates operational expenditure for each process (i)')

    # TOTAL VARIABLE ANNUAL OPEX

    def Opex_var_total_rule(m, a, y):
        return m.Opex_var_total[a, y] == sum(m.Opex_var[a, i, y] for i in m.I)
    m.Opex_var_total_cons = Constraint(
        m.A, m.Y, rule=Opex_var_total_rule, doc='Calculates operational expenditure')

    # TOTAL VARIABLE ANNUAL OPEX

    def Opex_fix_total_rule(m, a, y):
        return m.Opex_fix_total[a, y] == sum(m.Opex_fix[a, i, y] for i in m.I)
    m.Opex_fix_total_cons = Constraint(
        m.A, m.Y, rule=Opex_fix_total_rule, doc='Calculates operational expenditure')

    # TOTAL VARIABLE ANNUAL OPEX

    def Opex_total_rule(m, a, y):
        return m.Opex_total[a, y] == m.Opex_var_total[a, y] + m.Opex_fix_total[a, y]
    m.Opex_total_cons = Constraint(
        m.A, m.Y, rule=Opex_total_rule, doc='Calculates operational expenditure')

    # ANNUAL EXPENDITURE ON PURCHASE OF RESOURCE

    def B_total_rule(m, a, j, y):
        return m.B_total[a, j, y] == next((j_.purc_cost for j_ in J if j_.name == j))*m.C_annual[a, j, y]
    m.B_total_cons = Constraint(m.A, m.J, m.Y, rule=B_total_rule,
                                doc='Calculates expenditure on purchase of raw material')

    # ANNUAL TAX CREDIT
    def Credit_rule(m, a, i, y):
        return m.Credit[a, i, y] == next((i_.tax_cred[period_] for i_ in I if i_.name == i))*m.P_annual[a, i, y]
    m.Credit_cons = Constraint(m.A, m.I_Q45, m.Y, rule=Credit_rule,
                               doc='Calculates tax credit recieved through 45Q for each process (i)')

    # #TOTAL ANNUAL TAX CREDIT
    def Credit_Total_rule(m, a, y):
        return m.Credit_total[a, y] == sum(m.Credit[a, i, y] for i in m.I_Q45)
    m.Credit_Total_cons = Constraint(
        m.A, m.Y, rule=Credit_Total_rule, doc='Calculates tax credit recieved through 45Q')

    # GWP POTENTIAL OF FACILITIES
    def GWP_rule(m, a, i, y):
        return m.GWP[a, i, y] == next((i_.gwp for i_ in I if i_.name == i))*m.Cap_P[a, i, y]
    m.GWP_cons = Constraint(m.A, m.I, m.Y, rule=GWP_rule,
                            doc='calculates the GWP of each facility')

    # TOTAL GWP OF SYSTESM
    def GWP_total_rule(m, a, y):
        return m.GWP_total[a, y] == sum(m.GWP[a, i, y] for i in m.I)
    m.GWP_total_cons = Constraint(
        m.A, m.Y, rule=GWP_total_rule, doc='calculates the GWP of system')

    # =============================
    # OBJECTIVES
    # =============================

    # MINIMIZE COST OF PRODUCTION AND MEET ANNUAL DEMAND - m.Revenue_total[a, y]
    if opt_ == 'tx_miles':

        def Mile_total_rule(m, a, j, y):
            return next((j_.mile for j_ in J if j_.name == j))*m.S_annual[a, j, y] == demand_
        m.Mile_total_cons = Constraint(
            m.A, m.J_mile, m.Y, rule=Mile_total_rule, doc='Ensures that miles demand is met')
        # + m.Revenue_total[a, y]
        print('Meeting a mileage demand of ' + str(demand_) +
              ' miles in the year ' + str(2022 + year_))

        def Mile_total_rule2(m, a, y):
            return m.Mile_total[a, y] == sum(next((j_.mile for j_ in J if j_.name == j))*m.S_annual[a, j, y] for j in J_mile)
        m.Mile_total_cons2 = Constraint(
            m.A, m.Y, rule=Mile_total_rule2, doc='Calculates total mileage from fuels production')

        def Cost_Total_obj_rule(m):
            return sum(sum(m.Opex_total[a, y] + m.Capex_total[a, y] + sum(m.B_total[a, j, y] for j in m.J) - m.Credit_total[a, y] for a in m.A) for y in m.Y)
        m.Obj = Objective(rule=Cost_Total_obj_rule, sense=minimize,
                          doc='Objective to minimize total annualized cost')

        # def Cost_Total_obj_rule(m):
        #     return sum(sum(m.Opex_total[a, y]  + m.Capex_total[a, y]  for a in m.A) for y in m.Y)
        # m.Obj = Objective(rule = Cost_Total_obj_rule, sense = minimize, doc = 'Objective to minimize total annualized cost')

        # def Mile_max_obj_rule(m):
        #     return sum(sum(sum(next((j_.mile for j_ in J if j_.name == j))*m.S_annual[a, j, y] for j in m.J_mile) for a in m.A) for y in m.Y)
        # m.Obj = Objective(rule = Mile_max_obj_rule, sense = maximize, doc = 'maximizes total miles produced')
        # m.Obj.pprint()

    print('\n-----Processes considered-------')
    for i_ in I_labels:
        if 'discharge' not in i_:
            print(i_)

    print('\n-----Resources considered-------')
    for j_ in J_labels:
        print(j_)
    print('==========================================================================================================')

    if solver_ == 'gurobi':

        print('\nModel passed to ' + solver_ + ' solver')

        solver_ = SolverFactory('gurobi', solver_io='python')
        # results = solver_.solve(m, tee = True)
        results = solver_.solve(m)
        # D = dict.fromkeys(A, Defaults)

        if (results.solver.status == SolverStatus.ok) and\
                (results.solver.termination_condition == TerminationCondition.optimal):
            results.write()

            # m.C_annual.pprint()
            m.P_annual.pprint()
            m.S_annual.pprint()
            # m.X_P.pprint()
            # m.X_S.pprint()
            m.Cap_P.pprint()
            # m.Cap_S.pprint()
            # m.Opex_fix.pprint()
            # m.Opex_var.pprint()
            # m.Opex_var_total.pprint()
            # m.Opex_fix_total.pprint()
            # m.Opex_total.pprint()
            # m.Capex.pprint()
            # m.Capex_total.pprint()
            # # m.Revenue_total.pprint()
            # m.Credit.pprint()
            # m.Credit_total.pprint()
            # m.B_total.pprint()
            # m.GHG_total.pprint()
            # m.Mile_total.pprint()
            m.GWP.pprint()

            miles = m.Mile_total['HO', year_].value

            # land = {
            #     'wind' : 1200/239,
            #     'solar': 19000/120,
            #     'nuclear': 192000/1000,
            #     'ng_plant': 0.343
            # }

            land = {
                'wind': 8100*2.47105/400,  # Lone Star Phase I
                'solar': 124.2/16.1,  # Blue Wing Solar
                # https://www.nei.org/news/2015/land-needs-for-wind-solar-dwarf-nuclear-plants
                'nuclear': 832/1000,
                'ng_plant': 0.343  # https://docs.wind-watch.org/US-footprints-Strata-2017.pdf
            }

            # installed capacities

            if case_ in ['wind_ev', 'solar_ev', 'nuclear_ev', 'grid_ev']:
                # https://www.bcg.com/publications/2019/costs-revving-up-the-grid-for-electric-vehicles
                cost = m.Obj() + 2600*22*10**6
            else:
                cost = m.Obj()
            # cost_per_mile = cost/miles

            if 'CO2_Vent' in J_:
                co2 = m.S_annual['HO', 'CO2_Vent',
                                 year_].value + m.GWP_total['HO', year_].value
            else:
                co2 = m.GWP_total['HO', year_].value
            # 8 kg of lithium, 35 kg of nickel, 20 kg of manganese and 14 kg of cobalt
            # https://www.researchgate.net/publication/263708668_Life_Cycle_Assessment_of_Metals_A_Scientific_Synthesis

            if case_ in ['wind_ev', 'nuclear_ev', 'solar_ev', 'grid_ev']:
                co2 = co2 + (8*7.1 + 35*6.5 + 20*1 + 14*8.3)*22*10**6
            else:
                co2 = co2 + (5390)*22*10**6

            if case_ in ['wind_ev', 'wind_green', 'wind_blue', 'wind_blueish']:
                cap = m.Cap_P['HO', 'WF', year_].value
                if case_ not in ['wind_ev']:
                    prod = m.S_annual['HO', 'H2_C', year_].value
                else:
                    prod = m.S_annual['HO', 'Power', year_].value
                land = land['wind']*cap

            if case_ in ['solar_ev', 'solar_green', 'solar_blue', 'solar_blueish']:
                cap = m.Cap_P['HO', 'PV', year_].value
                if case_ not in ['solar_ev']:
                    prod = m.S_annual['HO', 'H2_C', year_].value
                else:
                    prod = m.S_annual['HO', 'Power', year_].value
                land = land['solar']*cap

            if case_ in ['grid_ev', 'grid_green', 'grid_blue', 'grid_blueish']:
                cap = m.Cap_P['HO', 'Grid', year_].value
                if case_ not in ['grid_ev']:
                    prod = m.S_annual['HO', 'H2_C', year_].value
                else:
                    prod = m.S_annual['HO', 'Power', year_].value
                land = land['ng_plant']*cap

            if case_ in ['nuclear_ev', 'nuclear_green', 'nuclear_blue', 'nuclear_blueish']:
                cap = m.Cap_P['HO', 'ASMR', year_].value
                if case_ not in ['nuclear_ev']:
                    prod = m.S_annual['HO', 'H2_C', year_].value
                else:
                    prod = m.S_annual['HO', 'Power', year_].value
                land = land['nuclear']*cap

            if 'H2O' in J_:
                water = m.C_annual['HO', 'H2O', year_].value
            else:
                water = 0

            if ('CH4' in J_) and ('Power_Gr' in J_):
                ng = m.C_annual['HO', 'CH4', year_].value + \
                    m.C_annual['HO', 'Power_Gr', year_].value * \
                    7.43*0.0283168*0.68
            elif ('CH4' in J_) and ('Power_Gr' not in J_):
                ng = m.C_annual['HO', 'CH4', year_].value
            elif ('CH4' not in J_) and ('Power_Gr' in J_):
                ng = m.C_annual['HO', 'Power_Gr',
                                year_].value*7.43*0.0283168*0.68
            else:
                ng = 0
            # co2_per_mile = co2/miles

            if 'Uranium' in J_:
                ur = m.C_annual['HO', 'Uranium', year_].value
            else:
                ur = 0

    # fig = go.Figure(data=[go.Sankey(
    #     node = dict(
    #     pad = 15,
    #     thickness = 20,
    #     line = dict(color = "black", width = 0.5),
    #     label = ["Water",\
    #         "Natural gas",\
    #         "Hydrogen (Blue)",\
    #         "Carbon dioxide (sequestered)",\
    #         "Carbon dioxide (vented)",\
    #         'Enhanced Oil Recovery',\
    #         'Crude oil'\
    #             ],
    #     color = [
    #         'aquamarine',\
    #         'slategrey',\
    #         'cornflowerblue',\
    #         'salmon', \
    #         'maroon',\
    #         'sienna',\
    #         'darkorange',\
    #             ]
    #     # #        'seagreen',\
    #     #     'darkorange',\
    #     #     'dimgray'\
    #         ),
    #     link = dict(
    #     source = [0,1,1,3,3,5,5], # indices correspond to labels, eg A1, A2, A1, B1, ...
    #     target = [2,2,3,4,5,4,6],
    #     color = ['mediumaquamarine',\
    #         'lightsteelblue',\
    #         'powderblue',\
    #         'peachpuff',\
    #         'red',\
    #         'darksalmon',\
    #         'orange',\
    #         'lightgray',\
    #         'red',\
    #         'powderblue'],
    #     value =  [-1*m.P_annual['HO', 'SMRH', year_].value*dict_conversion['SMRH']['H2O'],\
    #         m.P_annual['HO', 'SMRH', year_].value*dict_conversion['SMRH']['H2_B'],\
    #         m.P_annual['HO', 'SMRH', year_].value*dict_conversion['SMRH']['CO2_Vent'] + m.P_annual['HO', 'SMRH', year_].value*dict_conversion['SMRH']['CO2'],\
    #         m.P_annual['HO', 'SMRH', year_].value*dict_conversion['SMRH']['CO2_Vent'],\
    #         m.P_annual['HO', 'SMRH', year_].value*dict_conversion['SMRH']['CO2'],\
    #         m.P_annual['HO', 'EOR', year_].value*dict_conversion['EOR']['CO2_Vent'],\
    #         m.P_annual['HO', 'EOR', year_].value*dict_conversion['EOR']['CO2_EOR']*136]

    #     ))])

    # fig.show()

            # print(co2_per_mile, cost_per_mile)

    for comp_ in m.component_objects():
        m.del_component(comp_)
    return cost, co2, cap, prod, water, ng, ur, land


case_studies = ['wind_blue', 'solar_blue', 'grid_blue', 'nuclear_blue',
                'wind_green', 'solar_green', 'grid_green', 'nuclear_green',
                'wind_blueish', 'solar_blueish', 'grid_blueish',  'nuclear_blueish',
                'wind_ev', 'solar_ev', 'grid_ev', 'nuclear_ev']

# case_studies = ['wind_blue', 'solar_blue', 'grid_blue', 'nuclear_blue']
# case_studies = [ 'wind_green', 'solar_green', 'grid_green', 'nuclear_green']
# case_studies = [ 'wind_blueish', 'solar_blueish', 'grid_blueish',  'nuclear_blueish']
# case_studies = [ 'wind_ev', 'solar_ev', 'grid_ev', 'nuclear_ev']
# case_studies = ['wind_blue']


dict_results = {}
for case_ in case_studies:
    dict_results[case_] = {
        'cost': {},
        'co2': {},
        'cap': {},
        'prod': {},
        'water': {},
        'ng': {},
        'ur': {},
        'land': {},
    }

for case_ in case_studies:
    print('for the case study: ' + case_ + '\n\n')

    if case_ in ['wind_ev', 'solar_ev', 'nuclear_ev', 'grid_ev']:
        Power = resource('Power', True, True, True, True, False, 0, 0, 0, 0, 0, {
                         'near': 0, 'mid': 0, 'far': 0}, 0, (10**3)/(0.2167432**1.60934), 0, 'Renewable power generated (MW)')

    else:
        Power = resource('Power', True, True, True, False, False, 0, 0, 0, 0, 0, {
                         'near': 0, 'mid': 0, 'far': 0}, 0, 0, 0, 'Renewable power generated (MW)')

    # Blue Pathway
    if case_ == 'wind_blue':
        # Wind + Blue pathway
        I = [WF, SMRH, EOR, H2_Sink1, H2_C_c, H2_C_d]
        J = [Wind, H2O, H2_B, H2, Power, CO2, CO2_EOR, CO2_Vent, CH4, H2_C]

    elif case_ == 'solar_blue':

        # Solar + Blue pathway
        I = [PV, SMRH, EOR, H2_Sink1, H2_C_c, H2_C_d]
        J = [Solar, H2O, H2_B, H2, Power, CO2, CO2_EOR, CO2_Vent, CH4, H2_C]

    elif case_ == 'grid_blue':

        # #Grid + Blue pathway
        I = [Grid, SMRH, EOR, H2_Sink1, H2_C_c, H2_C_d]
        J = [Power_Gr, H2O, H2_B, H2, Power, CO2, CO2_EOR, CO2_Vent, CH4, H2_C]

    elif case_ == 'nuclear_blue':
        # Nuclear + Blue pathway
        I = [ASMR, SMRH, EOR, H2_Sink1, H2_C_c, H2_C_d]
        J = [Uranium, H2O, H2_B, H2, Power, CO2, CO2_EOR, CO2_Vent, CH4, H2_C]
    # #Green Pathway

    elif case_ == 'wind_green':

        # Wind + Green pathway
        I = [WF, AKE,  H2_Sink2, H2_C_c, H2_C_d]
        J = [Wind, H2O, H2_G, H2, Power, O2, H2_C]

    elif case_ == 'solar_green':

        # Solar + Green pathway
        I = [PV, AKE, H2_Sink2, H2_C_c, H2_C_d]
        J = [Solar, H2O, H2_G, H2, Power, O2,  H2_C]

    elif case_ == 'grid_green':

        #     #Grid + Green pathway
        I = [Grid, AKE, H2_Sink2, H2_C_c, H2_C_d]
        J = [Power_Gr, H2O, H2_G, H2, Power, O2,  H2_C, CO2_Vent]

    elif case_ == 'nuclear_green':

        # Nuclear + Green pathway
        I = [ASMR, AKE, H2_Sink2, H2_C_c, H2_C_d]
        J = [Uranium, H2O, H2_G, H2, Power, O2, H2_C]

    # #EV pathway
    elif case_ == 'wind_ev':

        #     #Wind + EV pathway
        I = [WF]
        J = [Wind, Power, H2O]

    elif case_ == 'solar_ev':
        # Solar + EV pathway
        I = [PV]
        J = [Solar, Power, H2O]

    elif case_ == 'grid_ev':

        # Grid + EV pathway
        I = [Grid]
        J = [Power_Gr, Power, CO2_Vent, H2O]

    elif case_ == 'nuclear_ev':

        # Grid + EV pathway
        I = [ASMR]
        J = [Uranium, Power, H2O]

        # Grey pathway
    elif case_ == 'wind_blueish':
        # Wind + Blue pathway
        I = [WF, SMR, EOR, H2_Sink1, H2_C_c, H2_C_d]
        J = [Wind, H2O, H2_B, H2, Power, CO2, CO2_EOR, CO2_Vent, CH4, H2_C]

    elif case_ == 'solar_blueish':
        # Solar + Blue pathway
        I = [PV, SMR, EOR, H2_Sink1, H2_C_c, H2_C_d]
        J = [Solar, H2O, H2_B, H2, Power, CO2, CO2_EOR, CO2_Vent, CH4, H2_C]

    elif case_ == 'grid_blueish':
        # #Grid + Blue pathway
        I = [Grid, SMR, EOR, H2_Sink1, H2_C_c, H2_C_d]
        J = [Power_Gr, H2O, H2_B, H2, Power, CO2, CO2_EOR, CO2_Vent, CH4, H2_C]

    elif case_ == 'nuclear_blueish':
        # Nuclear + Blue pathway
        I = [ASMR, SMR, EOR, H2_Sink1, H2_C_c, H2_C_d]
        J = [Uranium, H2O, H2_B, H2, Power, CO2, CO2_EOR, CO2_Vent, CH4, H2_C]

    # fig.update_layout(title_text='Material flow for ' + str(2022+ year_) + ' under a ' + scenario_.lower() + ' cost scenario', font_size=14)
    # fig.savefig(, dpi = 300)
    # pio.write_image(fig, 'MF_' + str(2022+year_) + '_' + scenario_.lower() + '.png',  scale=1)

    for scenario_ in SCENARIO:
        for year_ in YEAR:
            dict_results[case_]['cost'], dict_results[case_]['co2'], dict_results[case_]['cap'], dict_results[case_]['prod'], \
                dict_results[case_]['water'],  dict_results[case_]['ng'], dict_results[case_]['ur'], dict_results[case_]['land'], = hccus(
                    m, scenario_, year_, tx_miles.name, 'gurobi')

# %%

# case_studies = ['wind_ev', 'solar_ev', 'grid_ev', 'nuclear_ev']

X_, Y_ = [], []


labels_ = {
    'wind_blue': {'name': 'Wind + SMR + CC', 'marker': "^", 'color': 'royalblue', 'short': 'SMR + CC', 'short2': 'Wind'},
    'solar_blue': {'name': 'Solar + SMR + CC', 'marker': "v", 'color': 'royalblue', 'short': 'SMR + CC', 'short2': 'Solar'},
    'grid_blue': {'name': 'NG + SMR + CC', 'marker': ">", 'color': 'royalblue', 'short': 'SMR + CC', 'short2': 'NG'},
    'nuclear_blue': {'name': 'Nuclear + SMR + CC', 'marker': "<", 'color': 'royalblue', 'short': 'SMR + CC', 'short2': 'Nuclear'},

    'wind_green': {'name': 'Wind + AWE', 'marker': "+", 'color': 'seagreen', 'short': 'AWE', 'short2': 'Wind'},
    'solar_green': {'name': 'Solar + AWE', 'marker': "x", 'color': 'seagreen', 'short': 'AWE', 'short2': 'Solar'},
    'grid_green': {'name': 'NG + AWE', 'marker': "d", 'color': 'seagreen', 'short': 'AWE', 'short2': 'NG'},
    'nuclear_green': {'name': 'Nuclear + AWE', 'marker': "o", 'color': 'seagreen', 'short': 'AWE', 'short2': 'Nuclear'},

    'wind_blueish': {'name': 'Wind + SMR', 'marker': "s", 'color': 'slategray', 'short': 'SMR', 'short2': 'Wind'},
    'solar_blueish': {'name': 'Solar + SMR', 'marker': "p", 'color': 'slategray', 'short': 'SMR', 'short2': 'Solar'},
    'grid_blueish': {'name': 'NG + SMR', 'marker': "H", 'color': 'slategray', 'short': 'SMR', 'short2': 'NG'},
    'nuclear_blueish': {'name': 'Nuclear + SMR', 'marker': "D", 'color': 'slategray', 'short': 'SMR', 'short2': 'Nuclear'},

    'wind_ev': {'name': 'Wind + EV', 'marker': "8", 'color': 'orange', 'short': 'EV', 'short2': 'Wind'},
    'solar_ev': {'name': 'Solar + EV', 'marker': "X", 'color': 'orange', 'short': 'EV', 'short2': 'Solar'},
    'grid_ev': {'name': 'NG + EV', 'marker': "s", 'color': 'orange', 'short': 'EV', 'short2': 'NG'},
    'nuclear_ev': {'name': 'Nuclear + EV', 'marker': "P", 'color': 'orange', 'short': 'EV', 'short2': 'Nuclear'},
}

s_max = max([dict_results[case_]['cap'] for case_ in case_studies])
c_max = max([dict_results[case_]['co2'] for case_ in case_studies])


fig, ax = plt.subplots(figsize=(10, 8))
for case_ in case_studies:
    # a = [pow(10, i) for i in range(10)]

    # X_ = dict_results[case_]['cost']
    # Y_ = dict_results[case_]['co2']
    S_ = dict_results[case_]['cap']*10000/s_max

    X_ = dict_results[case_]['cost']
    # Y_ = dict_results[case_]['cap']
    Y_ = dict_results[case_]['co2']/10**9

    print(case_, X_, Y_)
    # ax.scatter(X_, Y_,s = S_, label = labels_[case_]['name'], \
    #     color = labels_[case_]['color'], alpha = 0.6, lw = 2, marker = labels_[case_]['marker'])
    ax.scatter(X_, Y_, label=labels_[case_]['name'], marker=labels_[case_]['marker'],
               color=labels_[case_]['color'], alpha=1, lw=2, s=100)
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.tick_params(labelsize=14)
    # ax.set_yscale('log')
    # ax.set_xscale('log')

    # ax.annotate(labels_[case_], (X_,Y_), verticalalignment = 'top', horizontalalignment = 'center')
pos_list_x = [6*10**10, 10**11, 2*10**11, 3*10**11]
name_list_x = ['60', '100', '200', '300']
# ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list_x)))
# ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list_x)))

pos_list_y = [10, 10**2, 10**3]
name_list_y = ['10', '100', '1000']
# ax.yaxis.set_major_locator(ticker.FixedLocator((pos_list_y)))
# ax.yaxis.set_major_formatter(ticker.FixedFormatter((name_list_y)))

plt.xlabel('Cost [billion $]', fontsize=14)
plt.ylabel('Emissions $CO_{2}$ [million mt]', fontsize=14)
plt.title('Cost v/s Emission comparison for different pathways', fontsize=16)
# plt.legend(fontsize = 14, )

# patches = []
# for i in range(len(colors)):
#     patches.append(mpatches.Patch(color=colors[i], label=labels[i]))

# plt.legend(handles= patches, bbox_to_anchor=(1.03, 1))
# plt.xlim(0, 3*10**11)
# plt.ylim(0, 10**7)
plt.legend(loc='upper center', ncol=4, fancybox=True,
           shadow=True, bbox_to_anchor=(0.5, -0.10))
lgnd = plt.legend(loc="upper center", scatterpoints=1, ncol=4,
                  fancybox=True, shadow=True, bbox_to_anchor=(0.5, -0.10))
for i in range(16):
    lgnd.legendHandles[i]._sizes = [90]
# lgnd.legendHandles[7]._sizes = [1000]


plt.grid(alpha=0.2)
plt.show()

# %%
# Land requirements - https://www.michigan.gov/documents/climateandenergy/CE_MI_4_Solar_Wind_688630_7.pdf,
# https://www.nei.org/news/2015/land-needs-for-wind-solar-dwarf-nuclear-plants#:~:text=A%20nuclear%20energy%20facility%20has,sites%20in%20the%20United%20States.
# https://docs.wind-watch.org/US-footprints-Strata-2017.pdf
land = {
    'wind': 8100*2.47105/400,  # Lone Star Phase I
    'solar': 124.2/16.1,  # Blue Wing Solar
    # https://www.nei.org/news/2015/land-needs-for-wind-solar-dwarf-nuclear-plants
    'nuclear': 832/1000,
    'ng_plant': 0.343  # https://docs.wind-watch.org/US-footprints-Strata-2017.pdf
}


# installed capacities
current_cap = {
    'wind': 32000,
    'solar': 7800,
    'nuclear': 125117*0.086,
    'ng_plant': 125117*0.535
}

fig, ax = plt.subplots(figsize=(10, 10))


for case_ in case_studies:

    if case_ in ['wind_blue', 'wind_green', 'wind_blueish', 'wind_ev']:
        X_ = ['Land used', 'Water consumed', 'Capacity added']
        Y_ = [dict_results[case_]['land'], dict_results[case_]
              ['water'], dict_results[case_]['cap'] - current_cap['wind']]

    if case_ in ['grid_blue', 'grid_green', 'grid_blueish', 'grid_ev']:
        X_ = ['Land used', 'Capacity added', 'Natural gas cons.']
        Y_ = [dict_results[case_]['land'], dict_results[case_]
              ['cap'] - current_cap['ng_plant'], dict_results[case_]['ng']]

    if case_ in ['solar_blue', 'solar_green', 'solar_blueish', 'solar_ev']:
        X_ = ['Land used', 'Water cons.', 'Capacity added']
        Y_ = [dict_results[case_]['land'], dict_results[case_]['water'],
              dict_results[case_]['cap'] - current_cap['solar']]

    if case_ in ['nuclear_blue', 'nuclear_green', 'nuclear_blueish', 'nuclear_ev']:
        X_ = ['Land used', 'Water cons.', 'Capacity added', 'Uranium cons.']
        Y_ = [dict_results[case_]['land'], dict_results[case_]['water'],
              dict_results[case_]['cap'] - current_cap['nuclear'], dict_results[case_]['ur']]

    print(case_, X_, Y_)
    # plt.bar(X_, Y_)
    # plt.title(case_)
    # plt.show()

# dict_ = dict_con_source
names = [i + ' (' + str(dict_[i]) + ')' for i in dict_.keys()]
size = [dict_[i] for i in dict_.keys()]

# # Create a circle at the center of the plot
# my_circle = plt.Circle( (0,0), 0.7, color='white')
# # Give color names
plt.pie(size, labels=names, colors=inner_colors, textprops={'fontsize': 14}, wedgeprops={
        "edgecolor": 'white', 'linewidth': 0, 'antialiased': True}, radius=1)
p = plt.gcf()
p.gca().add_artist(my_circle)
p.set_size_inches(10, 10)
# Show the graph
plt.title('Texas power consumption by source (Trillion Btu)', fontsize=16)
# plt.legend(bbox_to_anchor=(1, 1), fontsize = 14)
# %%
cases = ['wind_blue', 'wind_green', 'wind_blueish', 'wind_ev']

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['land']/10**6 for case_ in cases]
ax.bar(X_, Y_, color='brown')
plt.title('Additional land required (million acres)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['water']/10**12 for case_ in cases]
ax.bar(X_, Y_, color='blue')
plt.title('Water required (million mt)')
plt.show()
print(X_, Y_)

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['cap']/10**6 for case_ in cases]
ax.bar(X_, Y_, color='green')
plt.title('Additional capacity required (TW)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['cost']/10**9 for case_ in cases]
ax.bar(X_, Y_, color='gold')
plt.title('Cost (billion $)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['co2']/10**9 for case_ in cases]
ax.bar(X_, Y_, color='gray')
plt.title('Emissions (billion mt.$CO_{2}$)')
plt.show()
print(X_, Y_)


# %%
cases = ['grid_blue', 'grid_green', 'grid_blueish', 'grid_ev']


fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['land']/10**6 for case_ in cases]
ax.bar(X_, Y_, color='brown')
plt.title('Additional land required (million acres)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['water']/10**12 for case_ in cases]
ax.bar(X_, Y_, color='blue')
plt.title('Water required (million mt)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['cap']/10**6 for case_ in cases]
ax.bar(X_, Y_, color='green')
plt.title('Additional capacity required (TW)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['ng'] for case_ in cases]
ax.bar(X_, Y_, color='lightblue')
plt.title('Natural gas consumed (kgs)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['cost']/10**9 for case_ in cases]
ax.bar(X_, Y_, color='gold')
plt.title('Cost (billion $)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['co2']/10**9 for case_ in cases]
ax.bar(X_, Y_, color='gray')
plt.title('Emissions (billion mt.$CO_{2}$)')
plt.show()
print(X_, Y_)

# %%
cases = ['solar_blue', 'solar_green', 'solar_blueish', 'solar_ev']

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['land']/10**6 for case_ in cases]
ax.bar(X_, Y_, color='brown')
plt.title('Additional land required (million acres)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['water']/10**12 for case_ in cases]
ax.bar(X_, Y_, color='blue')
plt.title('Water required (million mt)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['cap']/10**6 for case_ in cases]
ax.bar(X_, Y_, color='green')
plt.title('Additional capacity required (TW)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['cost']/10**9 for case_ in cases]
ax.bar(X_, Y_, color='gold')
plt.title('Cost (billion $)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['co2']/10**9 for case_ in cases]
ax.bar(X_, Y_, color='gray')
plt.title('Emissions (billion mt.$CO_{2}$)')
plt.show()
print(X_, Y_)


# %%

cases = ['nuclear_blue', 'nuclear_green', 'nuclear_blueish', 'nuclear_ev']

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['land']/10**6 for case_ in cases]
ax.bar(X_, Y_, color='brown')
plt.title('Additional land required (million acres)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['water']/10**12 for case_ in cases]
ax.bar(X_, Y_, color='blue')
plt.title('Water required (million mt)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['cap']/10**6 for case_ in cases]
ax.bar(X_, Y_, color='green')
plt.title('Additional capacity required (TW)')
plt.show()


fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['ur'] for case_ in cases]
ax.bar(X_, Y_, color='yellow')
plt.title('Uranium consumed (kgs)')
plt.show()


fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['cost']/10**9 for case_ in cases]
ax.bar(X_, Y_, color='gold')
plt.title('Cost (billion $)')
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
X_ = [labels_[case_]['name'] for case_ in cases]
Y_ = [dict_results[case_]['co2']/10**9 for case_ in cases]
ax.bar(X_, Y_, color='gray')
plt.title('Emissions (billion mt.$CO_{2}$)')
plt.show()
print(X_, Y_)
# %%

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=[
            "Water",
            "Natural gas",
            "Hydrogen (Blue)",
            "Carbon dioxide (sequestered)",
            "Carbon dioxide (vented)",
            'Enhanced Oil Recovery',
            'Crude oil'
        ],
        color=[
            'turquoise',
            'darksalmon',
            'darkslategrey',
            'forestgreen',
            'cadetblue',
            'sandybrown',
            'darkred',
        ]
        # #        'seagreen',
        #     'darkorange',
        #     'dimgray'
    ),
    link=dict(
        # indices correspond to labels, eg A1, A2, A1, B1, ...
        source=[0, 1, 1, 3, 3, 5, 5],
        target=[2, 2, 3, 4, 5, 4, 6],
        color=['mediumaquamarine', 'salmon', 'powderblue', 'peachpuff', 'red',
               'mediumseagreen', 'orange', 'lightgray', 'red', 'powderblue'],
        value=[-1*m.P_annual['HO', 'SMRH', year_].value*dict_conversion['SMRH']['H2O'],
               m.P_annual['HO', 'SMRH', year_].value * \
               dict_conversion['SMRH']['H2_B'],
               m.P_annual['HO', 'SMRH', year_].value*dict_conversion['SMRH']['CO2_Vent'] + \
               m.P_annual['HO', 'SMRH', year_].value * \
               dict_conversion['SMRH']['CO2'],
               m.P_annual['HO', 'SMRH', year_].value * \
               dict_conversion['SMRH']['CO2_Vent'],
               m.P_annual['HO', 'EOR', year_].value * \
               dict_conversion['EOR']['CO2_EOR'],
               m.P_annual['HO', 'EOR', year_].value*dict_conversion['EOR']['CO2_EOR']*136,]
        # value = [10]*9
    ))])
# fig.update_layout(title_text='Material flow for ' + str(2022+ year_) + ' under a ' + scenario_.lower() + ' cost scenario', font_size=14)
# fig.savefig(, dpi = 300)
pio.write_image(fig, 'MF_' + str(2022+year_) + '_' +
                scenario_.lower() + '.png',  scale=1)

fig.show()

# %%

# tag_ = 'short'
# cases = ['grid_blue', 'grid_green', 'grid_blueish', 'grid_ev']
# str_ = ' - NG'

# cases = ['solar_blue', 'solar_green', 'solar_blueish', 'solar_ev']
# str_ = ' - Solar'

# cases = ['wind_blue', 'wind_green', 'wind_blueish', 'wind_ev']
# str_ = ' - Wind'

# cases = ['nuclear_blue', 'nuclear_green', 'nuclear_blueish', 'nuclear_ev']
# str_ = ' - Nuclear'


tag_ = 'short2'

# cases = ['wind_blue', 'solar_blue', 'grid_blue', 'nuclear_blue']
# str_ = ' - SMR + CC'

# cases = [ 'wind_green', 'solar_green', 'grid_green', 'nuclear_green']
# str_ = ' - AWE'

# cases= [ 'wind_blueish', 'solar_blueish', 'grid_blueish',  'nuclear_blueish']
# str_ = ' - SMR'

cases = ['wind_ev', 'solar_ev', 'grid_ev', 'nuclear_ev']
str_ = ' - EV'


base = {
    'grid_ev': 67000,
    'wind_ev': 32000,
    'solar_ev': 7800,
    'nuclear_ev': 11000,
    'grid_green': 67000,
    'wind_green': 32000,
    'solar_green': 7800,
    'nuclear_green': 11000,
    'grid_blue': 67000,
    'wind_blue': 32000,
    'solar_blue': 7800,
    'nuclear_blue': 11000,
    'grid_blueish': 67000,
    'wind_blueish': 32000,
    'solar_blueish': 7800,
    'nuclear_blueish': 11000
}
# str_ = ' w 45Q'

fig, ax = plt.subplots(figsize=(7, 5))
X_ = [labels_[case_][tag_] for case_ in cases]
Y_ = [dict_results[case_]['land']/10**6 for case_ in cases]
Y2_ = [0.4256]*5  # size of houston
X2_ = [i for i in np.arange(5)]

ax.bar(X_, Y_, color='indianred', width=0.6)
ax.plot(X2_, Y2_, '--', alpha=0.5, color='slateblue')
plt.annotate('Area of Houston', (0, 0.4256), verticalalignment='top',
             horizontalalignment='center', fontsize=13, color='slateblue')
plt.grid(axis='y', alpha=0.5)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.title('Additional land required (million acres)' + str_, fontsize=16)
# plt.ylim(0,350)
plt.show()

fig, ax = plt.subplots(figsize=(7, 5))
X_ = [labels_[case_][tag_] for case_ in cases]
Y_ = [dict_results[case_]['water']/10**12 for case_ in cases]
Y2_ = [0.0530437]*5  # water in lake conroe
X2_ = [i for i in np.arange(5)]
ax.bar(X_, Y_, color='powderblue', width=0.6)
ax.plot(X2_, Y2_, '--', alpha=0.5, color='seagreen')
plt.annotate('10$\%$ Lake Conroe\'s capacity', (0, 0.0530), verticalalignment='top',
             horizontalalignment='left', fontsize=13, color='seagreen')
plt.grid(axis='y', alpha=0.5)
plt.grid(axis='y', alpha=0.5)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.title('Water required (billion mt)' + str_, fontsize=16)
# plt.ylim(0,9)
plt.show()

# fig, ax = plt.subplots(figsize = (8,6))
# X_ = [labels_[case_][tag_] for case_ in cases]
# Y_ = [dict_results[case_]['cap']/10**3 for case_ in cases]
# ax.bar(X_, Y_, color = 'green')
# plt.title('Additional capacity required (GW)')
# plt.show()


# fig, ax = plt.subplots(figsize = (8,6))
# X_ = [labels_[case_][tag_] for case_ in cases]
# Y_ = [dict_results[case_]['ur'] for case_ in cases]
# ax.bar(X_, Y_, color = 'yellow')
# plt.title('Uranium consumed (kgs)')
# plt.show()


fig, ax = plt.subplots(figsize=(7, 5))
X_ = [labels_[case_][tag_] for case_ in cases]
Y_ = [dict_results[case_]['cost']/10**9 for case_ in cases]
ax.bar(X_, Y_, color='gold', width=0.6)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid(axis='y', alpha=0.5)
plt.title('Cost (billion $)' + str_, fontsize=16)
# plt.ylim(0,260)
plt.show()

fig, ax = plt.subplots(figsize=(7, 5))
X_ = [labels_[case_][tag_] for case_ in cases]
Y_ = [dict_results[case_]['co2']/10**12 for case_ in cases]
ax.bar(X_, Y_, color='gray', width=0.6)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid(axis='y', alpha=0.5)
plt.title('Emissions (billion mt.$CO_{2}$)' + str_, fontsize=16)
# plt.ylim(0,1.5)
plt.show()


fig, ax = plt.subplots(figsize=(7, 5))
X_ = [labels_[case_][tag_] for case_ in cases]
Y_ = [dict_results[case_]['cap']/base[case_] for case_ in cases]
ax.bar(X_, Y_, color='mediumaquamarine', width=0.6)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid(axis='y', alpha=0.5)
plt.title('# times the current generation capacity ' + str_, fontsize=16)
# plt.ylim(0,270)
plt.show()
# %%

metric_ = 'land'
# metric_ = 'cost'
# metric_ = 'water'
# metric_ = 'cap'
# metric_ = 'cost'


Y_ = [dict_results[case_][metric_] for case_ in cases]
y_max = max(Y_)
circle1 = plt.Circle(
    (0, 0), dict_results['grid_ev'][metric_]/y_max, color='indianred', alpha=0.7)
circle2 = plt.Circle(
    (0, 0), dict_results['wind_ev'][metric_]/y_max, color='powderblue', alpha=0.7)
circle3 = plt.Circle(
    (0, 0), dict_results['solar_ev'][metric_]/y_max, color='seagreen', alpha=0.7)
circle4 = plt.Circle(
    (0, 0), dict_results['nuclear_ev'][metric_]/y_max, color='slategrey', alpha=0.7)


fig, ax = plt.subplots()  # note we must use plt.subplots, not plt.subplot
# (or if you have an existing figure)
# fig = plt.gcf()
# ax = fig.gca()

ax.add_patch(circle1)
ax.add_patch(circle2)
ax.add_patch(circle3)
ax.add_patch(circle4)

# %%

# %%


dict_elec = {'Biomass': 427,
             'Coal': 74825,
             'Gas-CC': 138314,
             'Gas': 26106,
             'Hydro': 504,
             'Nuclear': 40270,
             'Other': 8,
             'Solar': 15711,
             'Wind': 95403,
             }

fig, ax = plt.subplots(figsize=(12, 8))
X_ = [i for i in dict_elec.keys()]
Y_ = [dict_elec[i]/1000 for i in dict_elec.keys()]
total_ = sum(i for i in Y_)
perc_ = [i*100/total_ for i in Y_]
ax.bar(X_, Y_, color='limegreen', width=0.6)
for i in np.arange(9):
    ax.annotate("{:#.2g}".format(perc_[i]) + '%', (X_[i], Y_[i] + 10),
                verticalalignment='top', horizontalalignment='center', fontsize=16)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid(axis='y', alpha=0.5)
plt.title('Contributions to the ERCOT Grid (TWh) in 2019', fontsize=16)
plt.ylim(0, 155)
plt.show()


# %%
# https://www.energy.ca.gov/data-reports/energy-almanac/california-electricity-data/2020-total-system-electric-generation#:~:text=Total%20generation%20for%20California%20was,to%2057%20percent%20in%202019.
dict_elec = {'Biomass': 5680,
             'Coal': 317,
             'Gas': 92298,
             'Geo': 11345,
             # 'Gas-CC': 138314,
             'Hydro': 17938 + 3476,
             'Nuclear': 16280,
             'Other': 384,
             'Solar': 29456,
             'Wind': 13708,
             }

fig, ax = plt.subplots(figsize=(12, 8))
X_ = [i for i in dict_elec.keys()]
Y_ = [dict_elec[i]/1000 for i in dict_elec.keys()]

total_ = sum(i for i in Y_)
perc_ = [i*100/total_ for i in Y_]

ax.bar(X_, Y_, color='limegreen', width=0.6, label='generated')

for i in np.arange(9):
    ax.annotate("{:#.2g}".format(perc_[i]) + '%', (X_[i], Y_[i] + 5),
                verticalalignment='top', horizontalalignment='center', fontsize=16)

plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid(axis='y', alpha=0.5)
plt.legend(fontsize=16)
plt.title('Contributions to the California Grid (TWh) in 2020', fontsize=16)
plt.ylim(0, 155)
plt.show()

# %%

# https://www.energy.ca.gov/data-reports/energy-almanac/california-electricity-data/2020-total-system-electric-generation#:~:text=Total%20generation%20for%20California%20was,to%2057%20percent%20in%202019.
dict_elec = {'Biomass': 5680,
             'Coal': 317,
             'Gas': 92298,
             'Geo': 11345,
             # 'Gas-CC': 138314,
             'Hydro': 17938 + 3476,
             'Nuclear': 16280,
             'Other': 384,
             'Solar': 29456,
             'Wind': 13708,
             }

dict_elec_imp = {'Biomass': 1000,
                 'Coal': 7157,
                 'Gas': 8724,
                 'Geo': 1991,
                 # 'Gas-CC': 138314,
                 'Hydro': 15337 + 322,
                 'Nuclear': 9154,
                 'Other': 134,
                 'Solar': 6596,
                 'Wind': 16635,
                 }

fig, ax = plt.subplots(figsize=(12, 8))
X_ = [i for i in dict_elec.keys()]
Y_ = [dict_elec[i]/1000 for i in dict_elec.keys()]
Y2_ = [dict_elec_imp[i]/1000 for i in dict_elec_imp.keys()]

total_ = sum(i for i in Y_) + sum(j for j in Y2_)
Ytot = np.add(Y_, Y2_)

perc_ = [i*100/total_ for i in Ytot]

ax.bar(X_, Y_, color='limegreen', width=0.6, label='generated')
ax.bar(X_, Y2_, bottom=Y_, color='blue', width=0.6, label='imported')

for i in np.arange(9):
    ax.annotate("{:#.2g}".format(perc_[i]) + '%', (X_[i], Y_[i] + Y2_[i] + 5),
                verticalalignment='top', horizontalalignment='center', fontsize=16)

plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid(axis='y', alpha=0.5)
plt.legend(fontsize=16)
plt.title('Contributions to the California Grid (TWh) in 2020', fontsize=16)
plt.ylim(0, 155)
plt.show()
# %%
