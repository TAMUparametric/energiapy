
# %%
#!/usr/bin/env python3

"""Energia's graphing module 
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"


import pandas as pd
import numpy as np
from datetime import datetime, date
import time
import random
import pickle as pkl
import json as json
import csv
import logging
import os
import requests
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rc 
import seaborn as sns
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import normalize

from sklearn.linear_model import LinearRegression
from sklearn.neighbors import NearestCentroid
from sklearn.cluster import KMeans
from pyomo.environ import *
from pyomo.opt import SolverStatus, TerminationCondition
from itertools import product
from functools import reduce
from collections import defaultdict
from subprocess import call
import energia


def graph_cost_metric(cost_dict: dict, location: energia.location, cost_scenario_list: list, process: energia.process, cost_metric: str, year_list: list):
    """plots the trjaectory of a cost metric across all cost scenarios
    Cost metrics can be 'CAPEX', 'Variable O&M', 'Fixed O&M'
    If cost metric is 'All' then plots all three as subplots
    Args:
        cost_dict (dict): dictionary with costing data
        location (energia.location): energia location object
        cost_scenario_list (list): list of energia cost_scenario objects 
        process (energia.process): energia process object
        cost_metric (str): cost metric to be considered from 'CAPEX', 'Variable O&M', 'Fixed O&M' or 'All' 
        year_list (list): list of years for the plot
    """
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': 16})
    rc('text', usetex=True)

    if cost_metric == 'All':  # TBF
        cost_metric_list = ['CAPEX', 'Fixed O&M', 'Variable O&M']
        fig, ax = plt.subplots(1, 3, figsize=(26, 8))
        x_cost = [int(year_ + 2021) for year_ in year_list]
        ls = ['--', '-.', '-']
        iter_ = 0
        # scale_factor = (10**-6) #trying to reduce clutering by giving the y-axis a scale, can be done with y_lim TBF
        for cost_metric_ in cost_metric_list:
            for cost_scenario_ in cost_scenario_list:
                y_cost = []
                for year_ in year_list:
                    y_cost.append(
                        cost_dict[location.name][cost_scenario_.name][process.name][year_][cost_metric_])
                ax[iter_].plot(
                    x_cost, y_cost, label=cost_scenario_.name, linestyle=ls[iter_])
            ax[iter_].set_title(cost_metric_)
            ax[iter_].set_xlabel('Year')
            ax[iter_].set_ylabel(
                cost_dict[location.name][cost_scenario_.name][process.name][year_]['units'])
            # ax[iter_].set_xticklabels(fontsize = 16)
            # y_cost = ['{:.2e}'.format(y_) for y_ in y_cost]
            ax[iter_].set_yticklabels(y_cost)
            iter_ += 1
        fig.suptitle('Cost trajectories for ' + process.label)
        fig.show()

    else:
        fig, ax = plt.subplots(figsize=(12, 8))
        x_cost = [int(year_ + 2021) for year_ in year_list]
        iter_ = 0
        ls = ['--', '-.', '-']

        for cost_scenario_ in cost_scenario_list:
            y_cost = []
            for year_ in year_list:
                y_cost.append(
                    cost_dict[location.name][cost_scenario_.name][process.name][year_][cost_metric])
            ax.plot(x_cost, y_cost, label=cost_scenario_.name,
                    linestyle=ls[iter_])
            ax.annotate('-' + str('{:.2f}'.format((y_cost[0] - y_cost[-1])*100/y_cost[0])) + '%', (x_cost[-1], y_cost[-1]),
                        verticalalignment='top', horizontalalignment='center', color='red')
            iter_ += 1
        plt.title(cost_metric + ' trajectory for ' + process.label)
        plt.legend(loc='best')
        plt.xlabel('Year')
        plt.ylabel('[' + cost_dict[location.name]
                   [cost_scenario_.name][process.name][year_]['units'] + ']')
        plt.grid(alpha=0.3)
        fig.show()
    plt.rcdefaults()
    return


def graph_power_efficiency(conversion_dict: dict, year_list: list, process: energia.process, resource: energia.resource):
    """plots the trajectory for power efficiency over the planning horizon

    Args:
        conversion_dict (dict): dictionary with conversion parameters
        year_list (list): list of years
        process (energia.process): process object
        resource (energia.resource): resource object
    """
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': 16})
    rc('text', usetex=True)
    fig, ax = plt.subplots(figsize=(12, 8))
    x_conv = [int(year_ + 2021) for year_ in year_list]
    y_conv = [-1*conversion_dict[year][process.name][resource.name] /
              conversion_dict[year][process.name]['Power'] for year in year_list]
    ax.plot(x_conv, y_conv)
    ax.annotate(str('{:.2f}'.format((y_conv[-1] - y_conv[0])*100/y_conv[0])) + '%', (x_conv[-1], y_conv[-1]),
                verticalalignment='top', horizontalalignment='center', color='red')
    plt.title('Conversion trajectory for ' + process.label)
    plt.xlabel('Year')
    plt.ylabel(resource.label + '/MW')
    plt.grid(alpha=0.3)
    fig.show()
    plt.rcdefaults()
    return


def graph_f_conv(varying_conversion_df: pd.DataFrame, process: energia.process, color='black'):
    """plots the varying conversion factor for process

    Args:
        varying_conversion_df (pd.DataFrame): df with varying conversion factors
        process (energia.process): energia process object
        color (str): defaults to black
    """

    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': 16})
    rc('text', usetex=True)
    pos_list = [0, 744, 1344, 2160, 2800, 3624, 4344, 5088, 5832,
                6552, 7296, 8016]  # hours of the year corresponding to month
    name_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    fig, ax = plt.subplots(figsize=(12, 6))
    x_ = varying_conversion_df.index.values.tolist()
    y_ = [value for value in varying_conversion_df[process.name]]
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
    ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
    plt.title('Conversion factor for ' + process.label)
    plt.ylabel('Normalized conversion factors')
    plt.grid(alpha=0.3)
    fig.show()
    plt.rcdefaults()
    return


def graph_f_cost(varying_price_df: pd.DataFrame, resource: energia.resource, unit: str, color='black'):
    """plots varying cost of resource

    Args:
        varying_price_df (pd.DataFrame): df with varying prices
        resource (energia.resource): energia resource object
        unit (str): cost units
                color (str): defaults to black
    """
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': 16})
    rc('text', usetex=True)
    pos_list = [0, 744, 1344, 2160, 2800, 3624, 4344, 5088, 5832,
                6552, 7296, 8016]  # hours of the year corresponding to month
    name_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    fig, ax = plt.subplots(figsize=(12, 6))
    x_ = varying_price_df.index.values.tolist()
    y_ = [value for value in varying_price_df[resource.name]]
    ax.plot(x_, y_, linewidth=0.8, color=color)
    ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
    ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
    plt.title('Purchase cost for ' + resource.label)
    plt.ylabel(unit)
    plt.grid(alpha=0.3)
    fig.show()
    plt.rcdefaults()
    return

def h_cost_contr(data: dict, process_list: list, resource_list: list):
    """plots the contribution to LCOH 

    Args:
        data (dict): results 
        process_list (list): list of process objects
        resource_list (list): list of resource objects
    """

    scenario = list(data.keys())[0]
    year_list = list(data[scenario].keys())
    location = list(data[scenario][0]['Net_P'].keys())[0]
    metric_list = ['Capex', 'Opex_var', 'Opex_fix']
    prod_total = [sum(data[scenario][year]['Net_P'][location][process]['P_annual']
                      for process in ['H2_Blue', 'H2_Green']) for year in year_list]
    energy_str = [
        process.name for process in process_list if process.block == 'power_storage']
    power_gen = [
        process.name for process in process_list if process.block == 'power_generation']
    material_prd = [
        process.name for process in process_list if process.block == 'material_production']
    material_str = [
        process.name for process in process_list if process.block == 'material_storage']
    ccus = [process.name for process in process_list if process.block == 'CCUS']
    purchase = [
        resource.name for resource in resource_list if resource.price > 0]

    columns = [process.name for process in process_list]

    df = pd.DataFrame(
        columns=['Year', 'Energy Storage', 'Power Generation', 'DEC Production', 'DEC Storage', 'CCUS', 'Purchase'])
    df['Year'] = year_list
    df['Energy Storage'] = [sum(sum(data[scenario][year]['Net_P'][location][process][metric]
                                for metric in metric_list) for process in energy_str)/prod_total[year] for year in year_list]
    df['Power Generation'] = [sum(sum(data[scenario][year]['Net_P'][location][process][metric]
                                  for metric in metric_list) for process in power_gen)/prod_total[year] for year in year_list]
    df['DEC Production'] = [sum(sum(data[scenario][year]['Net_P'][location][process][metric]
                                for metric in metric_list) for process in material_prd)/prod_total[year] for year in year_list]
    df['DEC Storage'] = [sum(sum(data[scenario][year]['Net_P'][location][process][metric]
                             for metric in metric_list) for process in material_str)/prod_total[year] for year in year_list]
    df['CCUS'] = [sum(sum(data[scenario][year]['Net_P'][location][process][metric]
                      for metric in metric_list) for process in ccus)/prod_total[year] for year in year_list]
    df['Purchase'] = [sum(data[scenario][year]['Net_S'][location][resource]['B_annual']
                          for resource in purchase)/prod_total[year] for year in year_list]
    lcoh = [data[scenario][year]['Total'][location]['LCOH']
            for year in year_list]

    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': 16})
    rc('text', usetex=True)
    width = 0.5
    fig, ax = plt.subplots(figsize=(10, 5))
    bar1 = ax.bar(df['Year'], df['Power Generation'], width,
                  color='darkorange', label='Power Generation')
    bar2 = ax.bar(df['Year'], df['Energy Storage'], width,
                  bottom=df['Power Generation'], color='indianred', label='Energy Storage')
    bar3 = ax.bar(df['Year'], df['DEC Production'], width, bottom=df['Power Generation'] +
                  df['Energy Storage'], color='royalblue', label='DEC Production')
    bar4 = ax.bar(df['Year'], df['DEC Storage'], width, bottom=df['Power Generation'] +
                  df['Energy Storage'] + df['DEC Production'], color='cornflowerblue', label='DEC Storage')
    bar5 = ax.bar(df['Year'], df['CCUS'], width, bottom=df['Power Generation'] +
                  df['Energy Storage'] + df['DEC Production'] + df['DEC Storage'] + df['CCUS'], color='forestgreen', label='CCUS')
    bar6 = ax.bar(df['Year'], df['Purchase'], width, bottom=df['Power Generation'] +
                  df['Energy Storage'] + df['DEC Production'] + df['DEC Storage'], color='slategrey', label='Purchase')

    scatter1 = ax.scatter(year_list, lcoh, color='black')
    line1 = ax.plot(year_list, lcoh, color='black', alpha=0.7)
    for iter_ in year_list:
        ax.annotate('{:.3}'.format(lcoh[iter_]), (iter_, max(lcoh)*1.1), horizontalalignment= 'center')
    plt.xlabel('Year')
    plt.xticks(year_list)
    plt.ylabel('\$/kg.$H_{2}$')
    plt.title('Contribution to LCOH under a ' +
              scenario.lower() + ' cost scenario')
    plt.ylim(0, max(lcoh)*1.25)
    plt.grid(axis='y', alpha=0.4)
    
    colors = ['darkorange', 'indianred', 'royalblue', 'cornflowerblue', 'forestgreen', 'slategrey']
    labels = [ 'Power Generation', 'Energy Storage', 'DEC Production', 'DEC Storage', 'CCUS', 'Purchase']
    patches = []
    for i in range(len(colors)):
        patches.append(mpatches.Patch(color=colors[i], label=labels[i]))

    plt.legend(handles= patches, bbox_to_anchor=(1, -0.2), ncol =3)
    # lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--') for c in colors]
    # plt.legend(lines, labels)
    plt.show()
    plt.rcdefaults()

    return


def inventory(data: dict, resource: energia.resource, year:int):
    """plots the inventory level for a chosen year

    Args:
        data (dict): results
        resource (energia.resource): resource
        year (int): year for plotting
        
    """
    
    scenario = list(data.keys())[0]
    location = list(data[scenario][0]['Sch_S'].keys())[0]
    day_list = list(data[scenario][0]['Sch_S'][location][resource.name].keys())
    hour_list = list(data[scenario][0]['Sch_S'][location][resource.name][day_list[0]].keys())
    inventory = [data[scenario][year]['Sch_S'][location][resource.name][day][hour]['Inv'] for day, hour in product(day_list, hour_list)]
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': 16})
    rc('text', usetex=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    pos_list = [(day-1)*len(hour_list) for day in day_list]  # hours of the year corresponding to month
    name_list = [str(day) for day in day_list]

#     fig, ax = plt.subplots(figsize=(12, 6))
#     x_ = day_list
#     y_ = [sum(DATA[0]['moderate'][0]['Sch_P'][HO.name]
#               [H2_Blue.name][day][hour]['P'] for hour in hour_list)]
#     ax.plot(x_, y_, linewidth=0.8, color=color)
    ax.plot(inventory)
    ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
    ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
    plt.xlabel('Representative day')
    plt.ylabel(resource.basis)
    plt.title('Inventory levels for ' +
              resource.label + ' in year ' + str(year))
    plt.grid(axis='y', alpha=0.4)
    plt.rcdefaults()
    return



def consumption(data: dict, resource: energia.resource, year:int):
    """plots the consumption of resource for a chosen year

    Args:
        data (dict): results
        resource (energia.resource): resource
        year (int): year for plotting
    """
    scenario = list(data.keys())[0]
    location = list(data[scenario][0]['Sch_S'].keys())[0]
    day_list = list(data[scenario][0]['Sch_S'][location][resource.name].keys())
    hour_list = list(data[scenario][0]['Sch_S'][location][resource.name][day_list[0]].keys())
    consumption = [data[scenario][year]['Sch_S'][location][resource.name][day][hour]['C'] for day, hour in product(day_list, hour_list)]
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': 16})
    rc('text', usetex=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    pos_list = [(day-1)*len(hour_list) for day in day_list]  # hours of the year corresponding to month
    name_list = [str(day) for day in day_list]

#     fig, ax = plt.subplots(figsize=(12, 6))
#     x_ = day_list
#     y_ = [sum(DATA[0]['moderate'][0]['Sch_P'][HO.name]
#               [H2_Blue.name][day][hour]['P'] for hour in hour_list)]
#     ax.plot(x_, y_, linewidth=0.8, color=color)
    ax.plot(consumption)
    ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
    ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
    plt.xlabel('Representative day')
    plt.ylabel(resource.basis)
    plt.title('Consumption of ' +
              resource.label + ' in year ' + str(year))
    plt.grid(axis='y', alpha=0.4)
    plt.rcdefaults()
    return

def sale(data: dict, resource: energia.resource, year:int):
    """plots the sale of resource for a chosen year

    Args:
        data (dict): results
        resource (energia.resource): resource
        year (int): year for plotting
    """
    scenario = list(data.keys())[0]
    location = list(data[scenario][0]['Sch_S'].keys())[0]
    day_list = list(data[scenario][0]['Sch_S'][location][resource.name].keys())
    hour_list = list(data[scenario][0]['Sch_S'][location][resource.name][day_list[0]].keys())
    sale = [data[scenario][year]['Sch_S'][location][resource.name][day][hour]['S'] for day, hour in product(day_list, hour_list)]
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': 16})
    rc('text', usetex=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    pos_list = [(day-1)*len(hour_list) for day in day_list]  # hours of the year corresponding to month
    name_list = [str(day) for day in day_list]

#     fig, ax = plt.subplots(figsize=(12, 6))
#     x_ = day_list
#     y_ = [sum(DATA[0]['moderate'][0]['Sch_P'][HO.name]
#               [H2_Blue.name][day][hour]['P'] for hour in hour_list)]
#     ax.plot(x_, y_, linewidth=0.8, color=color)
    ax.plot(sale)
    ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
    ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
    plt.xlabel('Representative day')
    plt.ylabel(resource.basis)
    plt.title('Sale of ' +
              resource.label + ' in year ' + str(year))
    plt.grid(axis='y', alpha=0.4)
    plt.rcdefaults()
    return

def purchase(data: dict, resource: energia.resource, year:int):
    """plots the purchase expenditure of resource for a chosen year

    Args:
        data (dict): results
        resource (energia.resource): resource
        year (int): year for plotting
    """
    scenario = list(data.keys())[0]
    location = list(data[scenario][0]['Sch_S'].keys())[0]
    day_list = list(data[scenario][0]['Sch_S'][location][resource.name].keys())
    hour_list = list(data[scenario][0]['Sch_S'][location][resource.name][day_list[0]].keys())
    purchase = [data[scenario][year]['Sch_S'][location][resource.name][day][hour]['B'] for day, hour in product(day_list, hour_list)]
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': 16})
    rc('text', usetex=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    pos_list = [(day-1)*len(hour_list) for day in day_list]  # hours of the year corresponding to month
    name_list = [str(day) for day in day_list]

#     fig, ax = plt.subplots(figsize=(12, 6))
#     x_ = day_list
#     y_ = [sum(DATA[0]['moderate'][0]['Sch_P'][HO.name]
#               [H2_Blue.name][day][hour]['P'] for hour in hour_list)]
#     ax.plot(x_, y_, linewidth=0.8, color=color)
    ax.plot(purchase)
    ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
    ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
    plt.xlabel('Representative day')
    plt.ylabel('\$')
    plt.title('Purchase expenditure for ' +
              resource.label + ' in year ' + str(year))
    plt.grid(axis='y', alpha=0.4)
    # plt.ylim(0,)
    plt.rcdefaults()
    return


# %%


# for scenario in cost_scenario_list:
#     i = 0
#     while i < 5:
#         print(results_dict[scenario.name][i]['Total'][HO.name]['LCOH'])
#         i += 1
# # %%

# # %%

# process_enesto_list = [
#     process.name for process in all_process_list if process.block == 'power_storage']
# process_powgen_list = [
#     process.name for process in all_process_list if process.block == 'power_generation']
# process_matpro_list = [
#     process.name for process in all_process_list if process.block == 'material_production']
# process_matsto_list = [
#     process.name for process in all_process_list if process.block == 'material_storage']
# process_ccus_list = [
#     process.name for process in all_process_list if process.block == 'CCUS']


# # %%

# files = ['base_case']


# DATA = []
# for data_ in files:
#     with open(data_ + '.pkl', 'rb') as f_:
#         locals()[data_] = pkl.load(f_)
#     DATA.append(locals()[data_])

# # %%
# day_list = [int(i) for i in range(1, 20)]  # list of days/seasons

# J = ['Charge', 'H2_C']


# def inventory(DATA_: list):
#     """Plots inventory levels of all storage facilities

#     Args:
#         DATA_ (list): list containing dictionaiers with data 
#         year_ (int): year being plotted
#     """
#     inventory_level = []
#     cost_scenario_list = [scenario_ for scenario_ in DATA_.keys()]
#     scenario_ = cost_scenario_list[0]
#     for y, d, h in product(range(0), day_list, hour_list):
#         inventory_level.append(
#             DATA_[scenario_][y]['Sch_S']['HO'][j][d][h]['Inv'])
#         # inventory_level.append(DATA_[scenario_][year_]['Sch_P']['HO'][j][h][d]['P'])
#         # inventory_level.append(DATA_[scenario_][year_]['Sch_S']['HO'][j][h][d]['S'])
#     # hours of the year corresponding to month]
#     pos_list = [8760*y for y in range(5)]
#     name_list = [y + 2022 for y in range(5)]

#     fig, ax = plt.subplots(figsize=(12, 6))
#     # X_ = np.arange(1,87601)
#     ax.plot(inventory_level, color='dodgerblue', label='Blue pathway')
#     # ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
#     # ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
#     ax.tick_params(axis='x', labelsize=13)
#     plt.grid(alpha=0.40)
#     plt.title(str(j))
#     plt.show()

#     return


# for DATA_ in DATA:
#     for j in J:
#         plot = inventory(DATA_)

# # %%


# # files = ['esh_bc_nocc_m_cd0o5']

# # files = ['esh_cc_m']
# files = ['esh_cc_q_m']


# DATA = []
# for data_ in files:
#     with open(data_ + '.pkl', 'rb') as f_:
#         locals()[data_] = pkl.load(f_)
#     DATA.append(locals()[data_])


# def h_cost_contr(DATA_: dict, year_list: list):
#     """Provides a breakdown of the cost contribution
#     in $/kg.H2

#     Args:
#         DATA_ (dict): contains results 
#     """
#     I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'AKE', 'SMR', 'H2_C_c',
#          'H2_L_c', 'DAC', 'MEFC', 'EOR', 'AQoff_SMR']  # 'AQoff_DAC',
#     # power_process = []
#     I2 = ['H2_C_c', 'H2_L_c', 'DAC', 'MEFC', 'EOR', 'AQoff_SMR']

#     h2_list = ['H2_Blue', 'H2_Green']
#     # h2_list = ['H2_Blue']

#     df = pd.DataFrame(columns=I)
#     df2 = pd.DataFrame(
#         columns=['Power System', 'Electrolysis', 'SMR + CC', 'Rest'])

#     # cost_scenario_list = [conservative.name]
#     cost_scenario_list = [moderate.name]
#     # cost_scneario_list = [advanced.name]

#     for scenario_ in cost_scenario_list:
#         for year_ in year_list:
#             div_ = sum(DATA_[scenario_][year_]['Net_P']['HO']
#                        [k]['P_annual'] for k in h2_list)
#             list_ = []
#             for i in I:
#                 list_.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i][j] for j in [
#                              'Capex', 'Opex_fix', 'Opex_var'])/div_)
#             # print(list_)

#             df.loc[year_] = list_
#         # view data
#         df['Year'] = df.index
#         df['AQoff'] = df['AQoff_SMR']  # + df['AQoff_DAC']
#         df['Rest'] = sum(df[i] for i in I2)
#         df2['Power System'] = sum(
#             df[i] for i in ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c'])
#         # df2['Power System'] = df2['Power System']/max(df2['Power System'])
#         df2['Electrolysis'] = df['AKE']  # /max(df['AKE'])
#         df2['SMR + CC'] = df['SMR']  # /max(df['SMR'])
#         df2['Rest'] = df['Rest']

#         list2_, list3_, list4_, list5_ = ([] for _ in range(4))
#         for year_ in year_list:
#             div_ = sum(DATA_[scenario_][year_]['Net_P']['HO']
#                        [k]['P_annual'] for k in h2_list)
#             list2_.append(-1*DATA_[scenario_][year_]
#                           ['Net_P']['HO']['EOR']['Credit']/div_)
#             list3_.append(-1*sum(DATA_[scenario_][year_]['Net_P']['HO']
#                           [i]['Credit'] for i in ['AQoff_SMR'])/div_)  # 'AQoff_DAC',
#             list4_.append(-1*DATA_[scenario_][year_]
#                           ['Net_P']['HO']['MEFC']['Credit']/div_)
#             list5_.append(DATA_[scenario_][year_]['Net_S']
#                           ['HO']['CH4']['B_annual']/div_)

#         df2['45Q-EOR'] = list2_
#         df2['45Q-Aquifer'] = list3_
#         df2['45Q-Methanol'] = list4_
#         df2['NG Purchase'] = list5_

#         cols = ['Power System', 'Electrolysis', 'SMR + CC',
#                 'Rest', '45Q-EOR', '45Q-Aquifer', '45Q-Methanol']
#         # df2[cols] = df2[cols].div(df2[cols].sum(axis=1), axis=0).multiply(100)
#         df2['Year'] = df2.index + 2022
#     # plot data in stack manner of bar type
#         width = 0.8
#         space = 0.9
#         fig, ax = plt.subplots(figsize=(10, 5))
#         bar1 = ax.bar(df2['Year'], df2['Power System'], width,
#                       color='darkorange', label='Power System')
#         bar2 = ax.bar(df2['Year'], df2['Electrolysis'], width,
#                       bottom=df2['Power System'], color='forestgreen', label='Electrolysis')
#         bar3 = ax.bar(df2['Year'], df2['SMR + CC'], width, bottom=df2['Power System'] +
#                       df2['Electrolysis'], color='cadetblue', label='SMR + CC')
#         bar4 = ax.bar(df2['Year'], df2['Rest'], width, bottom=df2['Power System'] +
#                       df2['Electrolysis'] + df2['SMR + CC'], color='indianred', label='H2 Storage ')

#         bar5 = ax.bar(df2['Year'], df2['NG Purchase'], width, bottom=df2['Power System'] + df2['Electrolysis'] + df2['SMR + CC']
#                       + df2['Rest'], color='slategrey', label='NG Purchase')

#         bar6 = ax.bar(df2['Year'], df2['45Q-EOR'], width, bottom=df2['45Q-Aquifer'] +
#                       df2['45Q-Methanol'], color='slateblue',  label='45Q-EOR')
#         bar7 = ax.bar(df2['Year'], df2['45Q-Aquifer'],   width,
#                       bottom=df2['45Q-Methanol'], color='saddlebrown', label='45Q-Aquifer')
#         bar8 = ax.bar(df2['Year'], df2['45Q-Methanol'],
#                       width, color='teal', label='45Q-Methanol')

#         bar5 = ax.bar(df2['Year'], df2['45Q-EOR'], width)

#         plt.title('Contribution to total hydrogen cost [\$/kg.$H_{2}$] \n under a ' + scenario_.lower(
#         ) + ' cost scenario', fontsize=16, color='midnightblue', y=1)
#         # plt.subtitle(, fontsize=14, y = 0.98)
#         plt.xlabel('Year', fontsize=14)
#         plt.ylabel('$', fontsize=14)
#         plt.legend(fontsize=14)
#         plt.xticks(fontsize=14)
#         plt.yticks(fontsize=14)
#         ax.set_xticks(df2['Year'])

#         ax.xaxis.set_ticks_position('both')
#         ax.yaxis.set_ticks_position('both')

#         # x_ = list(range(2022,2032))
#         x_ = [i + 2022 for i in year_list]
#         y_ = [1.0]*len(x_)
#         ax.scatter(x_, y_, alpha=0.0001, color='black', marker='*')

#         ax.yaxis.set_minor_locator(AutoMinorLocator())
#         annot, Y_ = [], []
#         for year_ in year_list:

#             value = DATA_[scenario_][year_]['Total']['HO']['LCOH']

#             annot.append(str(round(value, 2)))
#             Y_.append(value)

#         for i, txt in enumerate(annot):
#             ax.annotate(txt, (x_[i], y_[i]), verticalalignment='top',
#                         horizontalalignment='center', fontsize=14, color='midnightblue')

#         ax.scatter(x_, Y_,  s=20, facecolors='r', edgecolors='r', zorder=2)
#         ax.plot(x_, Y_, color='r', zorder=2)
#         lgd = plt.legend(bbox_to_anchor=(1.005, 1), fontsize=13)
#         # plt.ylim([-0.5,2])
#         plt.grid(alpha=0.25)
#         plt.tight_layout()
#         plt.savefig('h2_contr_' + scenario_.lower() + '.png', dpi=1200)
#         plt.show()

#     return


# for DATA_ in DATA:
#     plot_ = h_cost_contr(DATA_, year_list)
# # %%

# for data in DATA:
#     cost_scenario_list = [scenario_ for scenario_ in data.keys()]
#     for scenario in cost_scenario_list:
#         y = [data[scenario][year]['Total']['HO']['LCOH'] for year in range(5)]
#         # y = [data[scenario][year]['Total']['HO']['CO2_total'] for year in range(5)]
#         # y = [data[scenario][year]['Total']['HO']['CO2_int'] for year in range(5)]
#         print(y)

#         year = [2022 + i for i in range(5)]
#     fig, ax = plt.subplots(figsize=(10, 8))
#     ax.bar(year, y)
#     # ax.set_ylim([0,3])
#     plt.show()
# # %%

# # %%
# y_ = []
# for d, h, in product(day_list, hour_list):
#     y_.append(results_dict[moderate.name][0]['Sch_S']
#               [HO.name][Solar.name][d][h]['C'])
# # %%
# plt.plot(y_)

# # %%


# # %%
# df = pd.DataFrame(columns=['process', 'CAPEX',
#                   'Fixed O&M', 'Variable O&M', 'Units', 'Source'])
# for process in process_list:
#     df = df.append({'process': process.label,
#                     'CAPEX': cost_dict[HO.name][conservative.name][process.name][0]['CAPEX'], 'Fixed O&M': cost_dict[HO.name][conservative.name][process.name][0]['Fixed O&M'],
#                     'Variable O&M': cost_dict[HO.name][conservative.name][process.name][0]['Variable O&M'],
#                     'units': cost_dict[HO.name][conservative.name][process.name][0]['units'],
#                     'Source': cost_dict[HO.name][conservative.name][process.name][0]['source']}, ignore_index=True)
#     # print(process.label)
#     # print(cost_dict[HO.name][conservative.name][process.name][0]['CAPEX'])
#     # print(cost_dict[HO.name][conservative.name][process.name][0]['source'])
#     # print(cost_dict[HO.name][conservative.name][process.name][0]['units'])

# # %%
# df.to_csv('costing.csv', index=False)
# # %%
# # files = ['esh_cc_m']
# # H2 cost contribution for the base case
# files = ['esh_bc_nocc_m']
# DATA = []
# for data_ in files:
#     with open(data_ + '.pkl', 'rb') as f_:
#         locals()[data_] = pkl.load(f_)
#     DATA.append(locals()[data_])


# def h_cost_contr_base(DATA_: dict, year_list: list):
#     """Provides a breakdown of the cost contribution
#     in $/kg.H2

#     Args:
#         DATA_ (dict): contains results 
#     """
#     I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'ASMR', 'AKE', 'SMR',
#          'H2_C_c', 'H2_L_c', 'DAC', 'MEFC', 'EOR', 'AQoff_SMR']  # 'AQoff_DAC',
#     # power_process = []
#     I2 = ['H2_C_c', 'H2_L_c', 'DAC', 'MEFC', 'EOR', 'AQoff_SMR']

#     h2_list = ['H2_Blue', 'H2_Green']
#     # h2_list = ['H2_Blue']

#     df = pd.DataFrame(columns=I)
#     df2 = pd.DataFrame(
#         columns=['Power Gen.', 'Energy Stor.' 'Electrolysis', 'SMR', 'Rest'])

#     # cost_scenario_list = [conservative.name]
#     cost_scenario_list = [moderate.name]
#     # cost_scneario_list = [advanced.name]

#     for scenario_ in cost_scenario_list:
#         for year_ in year_list:
#             div_ = sum(DATA_[scenario_][year_]['Net_P']['HO']
#                        [k]['P_annual'] for k in h2_list)
#             list_ = []
#             for i in I:
#                 list_.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i][j] for j in [
#                              'Capex', 'Opex_fix', 'Opex_var'])/div_)
#             # print(list_)

#             df.loc[year_] = list_
#         # view data
#         df['Year'] = df.index
#         df['AQoff'] = df['AQoff_SMR']  # + df['AQoff_DAC']
#         df['Rest'] = sum(df[i] for i in I2)
#         df2['Power Gen.'] = sum(df[i] for i in ['PV', 'WF',  'ASMR'])
#         df2['Energy Stor.'] = sum(df[i] for i in ['LiI_c', 'PSH_c', 'CAES_c'])
#         # df2['Power System'] = df2['Power System']/max(df2['Power System'])
#         df2['Electrolysis'] = df['AKE']  # /max(df['AKE'])
#         df2['SMR'] = df['SMR']  # /max(df['SMR'])
#         df2['Rest'] = df['Rest']

#         list2_, list3_, list4_, list5_ = ([] for _ in range(4))
#         for year_ in year_list:
#             div_ = sum(DATA_[scenario_][year_]['Net_P']['HO']
#                        [k]['P_annual'] for k in h2_list)
#             list2_.append(-1*DATA_[scenario_][year_]
#                           ['Net_P']['HO']['EOR']['Credit']/div_)
#             list3_.append(-1*sum(DATA_[scenario_][year_]['Net_P']['HO']
#                           [i]['Credit'] for i in ['AQoff_SMR'])/div_)  # 'AQoff_DAC',
#             list4_.append(-1*DATA_[scenario_][year_]
#                           ['Net_P']['HO']['MEFC']['Credit']/div_)
#             list5_.append(DATA_[scenario_][year_]['Net_S']
#                           ['HO']['CH4']['B_annual']/div_)

#         df2['45Q-EOR'] = list2_
#         df2['45Q-Aquifer'] = list3_
#         df2['45Q-Methanol'] = list4_
#         df2['NG Purchase'] = list5_

#         cols = ['Power System', 'Electrolysis', 'SMR ', 'Rest']
#         # df2[cols] = df2[cols].div(df2[cols].sum(axis=1), axis=0).multiply(100)
#         df2['Year'] = df2.index + 2022
#     # plot data in stack manner of bar type
#         width = 0.8
#         space = 0.9
#         fig, ax = plt.subplots(figsize=(10, 5))
#         # bar1 = ax.bar(df2['Year'], df2['Power System'], width, color= 'darkorange', label= 'Power System')
#         # bar2 = ax.bar(df2['Year'], df2['Electrolysis'], width, bottom= df2['Power System'], color='forestgreen', label='Electrolysis')
#         # bar3 = ax.bar(df2['Year'], df2['SMR'], width, bottom= df2['Power System'] + df2['Electrolysis'], color='cadetblue', label='SMR')
#         # bar4 = ax.bar(df2['Year'], df2['Rest'], width, bottom= df2['Power System'] + df2['Electrolysis'] + df2['SMR'], color='indianred', label='H2 Storage ')

#         # bar5 = ax.bar(df2['Year'], df2['NG Purchase'], width, bottom= df2['Power System'] + df2['Electrolysis'] + df2['SMR'] \
#         #     + df2['Rest'], color='slategrey', label='NG Purchase')

#         # power systems cost
#         bar1 = ax.bar(df2['Year'], df2['Power Gen.'], width,
#                       color='darkorange', label='Power Gen.')
#         bar2 = ax.bar(df2['Year'], df2['Energy Stor.'], width,
#                       bottom=df2['Power Gen.'], color='royalblue', label='Energy Stor.')

#         bar3 = ax.bar(df2['Year'], df2['NG Purchase'], width, bottom=df2['Power Gen.'] +
#                       df2['Energy Stor.'], color='slategrey', label='NG Purchase')
#         bar4 = ax.bar(df2['Year'], df2['SMR'], width, bottom=df2['Power Gen.'] +
#                       df2['NG Purchase'] + df2['Energy Stor.'], color='cadetblue', label='SMR')
#         bar5 = ax.bar(df2['Year'], df2['Electrolysis'], width, bottom=df2['Power Gen.'] +
#                       df2['NG Purchase'] + df2['SMR'] + df2['Energy Stor.'], color='forestgreen', label='Electrolysis')
#         bar6 = ax.bar(df2['Year'], df2['Rest'], width, bottom=df2['Power Gen.'] + df2['Electrolysis'] +
#                       df2['NG Purchase'] + df2['SMR'] + df2['Energy Stor.'], color='indianred', label='H2 Storage')

#         # bar6 = ax.bar(df2['Year'], df2['45Q-EOR'], width, bottom = df2['45Q-Aquifer']+ df2['45Q-Methanol'], color = 'slateblue',  label = '45Q-EOR')
#         # bar7 = ax.bar(df2['Year'], df2['45Q-Aquifer'],   width, bottom = df2['45Q-Methanol'], color = 'saddlebrown', label = '45Q-Aquifer')
#         # bar8 = ax.bar(df2['Year'], df2['45Q-Methanol'], width, color = 'teal', label = '45Q-Methanol')

#         # bar5 = ax.bar(df2['Year'], df2['45Q-EOR'], width)

#         plt.title('Contribution to total hydrogen cost [\$/kg.$H_{2}$] \n under a ' + scenario_.lower(
#         ) + ' cost scenario', fontsize=16, color='midnightblue', y=1)
#         # plt.subtitle(, fontsize=14, y = 0.98)
#         plt.xlabel('Year', fontsize=14)
#         plt.ylabel('$', fontsize=14)
#         plt.legend(fontsize=14)
#         plt.xticks(fontsize=14)
#         plt.yticks(fontsize=14)
#         ax.set_xticks(df2['Year'])

#         ax.xaxis.set_ticks_position('both')
#         ax.yaxis.set_ticks_position('both')

#         # x_ = list(range(2022,2032))
#         x_ = [i + 2022 for i in year_list]
#         y_ = [1.1]*len(x_)
#         ax.scatter(x_, y_, alpha=0.0001, color='black', marker='*')

#         ax.yaxis.set_minor_locator(AutoMinorLocator())
#         annot, Y_ = [], []
#         for year_ in year_list:

#             value = DATA_[scenario_][year_]['Total']['HO']['LCOH']

#             annot.append(str(round(value, 2)))
#             Y_.append(value)

#         for i, txt in enumerate(annot):
#             ax.annotate(txt, (x_[i], y_[i]), verticalalignment='top',
#                         horizontalalignment='center', fontsize=14, color='midnightblue')

#         ax.scatter(x_, Y_,  s=20, facecolors='r', edgecolors='r', zorder=2)
#         ax.plot(x_, Y_, color='r', zorder=2)
#         lgd = plt.legend(bbox_to_anchor=(1.005, 1), fontsize=13)
#         # plt.ylim([-0.5,2])
#         plt.grid(alpha=0.25)
#         # plt.tight_layout()
#         plt.savefig('h2_contr_' + scenario_.lower() + '.png', dpi=2400)
#         plt.show()

#     return


# for DATA_ in DATA:
#     plot_ = h_cost_contr_base(DATA_, year_list)


# def schedule_bg(day_list: list, year: int):
#     """plots varying cost of resource

#     Args:
#         varying_price_df (pd.DataFrame): df with varying prices
#         resource (energia.resource): energia resource object
#         unit (str): cost units
#                 color (str): defaults to black
#     """
#     plt.rcParams.update({'font.size': 20})
#     pos_list = [0, 744, 1344, 2160, 2800, 3624, 4344, 5088, 5832,
#                 6552, 7296, 8016]  # hours of the year corresponding to month
#     name_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
#                  'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

#     fig, ax = plt.subplots(figsize=(12, 6))
#     x_ = day_list
#     y_ = [sum(DATA[0]['moderate'][0]['Sch_P'][HO.name]
#               [H2_Blue.name][day][hour]['P'] for hour in hour_list)]
#     ax.plot(x_, y_, linewidth=0.8, color=color)
#     ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
#     ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
#     plt.title('Purchase cost for ' + resource.label)
#     plt.ylabel(unit)
#     plt.grid(alpha=0.3)
#     fig.show()
#     plt.rcdefaults()
#     return


# # %%\
# #
# # H2 cost contribution for the base case
# # files = ['esh_bc_nocc_m']
# files = ['esh_cc_m']
# DATA = []
# for data_ in files:
#     with open(data_ + '.pkl', 'rb') as f_:
#         locals()[data_] = pkl.load(f_)
#     DATA.append(locals()[data_])


# ng_price_df = energia.make_henry_price_df(
#     file_name='Henry_Hub_Natural_Gas_Spot_Price_Daily.csv', year=2019, stretch=True)

# rep_days_dict = energia.reduce_scenario(varying_process_df=power_output_df, varying_resource_df=ng_price_df,
#                                         red_scn_method='AHC', rep_days_no=20)

# rep_day_list = [int(i) + 1 for i in range(20)]
# blue_, green_, ng_, h2l_, h2c_, pv_, wf_, nu_ = ([] for _ in range(8))

# ng_price_df = energia.make_henry_price_df(
#     file_name='Henry_Hub_Natural_Gas_Spot_Price_Daily.csv', year=2019, stretch=False)

# for day in rep_day_list:
#     blue_.append(sum(DATA[0]['moderate'][8]['Sch_P'][HO.name]
#                  [H2_Blue.name][day][hour]['P'] for hour in hour_list))
#     green_.append(sum(DATA[0]['moderate'][8]['Sch_P'][HO.name]
#                   [H2_Green.name][day][hour]['P'] for hour in hour_list))
#     ng_.append(ng_price_df['CH4'][ng_price_df['day'] == day].values)
#     h2l_.append(sum(DATA[0]['moderate'][8]['Sch_S'][HO.name]
#                 [H2_L.name][day][hour]['Inv'] for hour in hour_list))
#     h2c_.append(sum(DATA[0]['moderate'][8]['Sch_S'][HO.name]
#                 [H2_C.name][day][hour]['Inv'] for hour in hour_list))
#     pv_.append(sum(DATA[0]['moderate'][8]['Sch_P'][HO.name]
#                [PV.name][day][hour]['P'] for hour in hour_list))
#     wf_.append(sum(DATA[0]['moderate'][8]['Sch_P'][HO.name]
#                [WF.name][day][hour]['P'] for hour in hour_list))
#     nu_.append(sum(DATA[0]['moderate'][8]['Sch_P'][HO.name]
#                [ASMR.name][day][hour]['P'] for hour in hour_list))
# # blue_ = [float(i)/max(blue_) for i in blue_]

# # green_ = [float(i)/max(green_) for i in green_]


# total_ = [sum(value) for value in zip(blue_, green_)]

# # blue_ = [i / j for i, j in zip(blue_, total_)]

# # green_ = [i / j for i, j in zip(green_, total_)]

# h2_ = [i + j for i, j in zip(h2l_, h2c_)]

# h2_ = [float(i)/max(h2_) for i in h2_]

# pow_ = [sum(value) for value in zip(pv_, wf_, nu_)]

# # pv_ = [i / j for i, j in zip(pv_, pow_)]
# # wf_ = [i / j for i, j in zip(wf_, pow_)]
# # nu_ = [i / j for i, j in zip(nu_, pow_)]


# plt.rcParams.update({'font.size': 13})
# fig, ax = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
# # ax2 = ax[2].twinx()
# ax[0].bar(rep_day_list, blue_,  color='blue', alpha=0.8, label='blue')
# ax[0].bar(rep_day_list, green_, bottom=blue_,
#           color='green', alpha=0.8, label='green')
# ax[0].set_ylabel('')
# # ax2.plot(rep_day_list, ng_, linewidth = 1.3, color = 'black', alpha = 0.8, label = 'natural has price')

# ax[1].bar(rep_day_list, wf_, color='forestgreen', alpha=0.8, label='wind')
# ax[1].bar(rep_day_list, pv_, bottom=wf_,
#           color='orange', alpha=0.8, label='solar')
# ax[1].bar(rep_day_list, nu_, bottom=[i + j for i, j in zip(wf_, pv_)],
#           color='royalblue', alpha=0.8, label='nuclear')

# ax[2].bar(rep_day_list, h2l_,  color='red', alpha=0.8, label='Geo. Storage')
# ax[2].bar(rep_day_list, h2c_, bottom=h2l_,
#           color='orange', alpha=0.8, label='Local Cryo')

# ax[2].set_xlabel('Representative days', fontsize=16)


# # ax2.set_ylabel('Natural gas cost ($/kg)')
# ax[0].legend(fontsize=13)
# ax[1].legend(fontsize=13)
# ax[2].legend(fontsize=13)

# ax[0].set_title('Hydrogen production by pathway')
# ax[1].set_title('Power from source')
# ax[2].set_title('Inventory Level')

# ax[0].set_ylabel('kg')
# ax[1].set_ylabel('MW')
# ax[2].set_ylabel('kg')


# ax[1].set_ylim(0, 70000)

# plt.xticks(rep_day_list)
# # plt.suptitle('', fontsize = 19)
# for i in range(3):
#     ax[i].grid(alpha=0.3)
# fig.show()
# plt.rcdefaults()

# %%


# %%

# %%

# H2 cost contribution for the base case


# files = ['esh_bc_nocc']
# files = ['esh_cc_m']

# DATA = []
# for data_ in files:
#     with open(data_ + '.pkl', 'rb') as f_:
#         locals()[data_] = pkl.load(f_)
#     DATA.append(locals()[data_])


# def h_cost_contr_cc(DATA_: dict, year_list: list):
#     """Provides a breakdown of the cost contribution
#     in $/kg.H2

#     Args:
#         DATA_ (dict): contains results 
#     """
#     I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'ASMR', 'AKE', 'SMRH',
#          'H2_C_c', 'H2_L_c', 'DAC', 'MEFC', 'EOR', 'AQoff_SMR']  # 'AQoff_DAC',
#     # power_process = []
#     I2 = ['H2_C_c', 'H2_L_c']
#     I3 = ['DAC', 'MEFC', 'EOR', 'AQoff_SMR']

#     h2_list = ['H2_Blue', 'H2_Green']
#     # h2_list = ['H2_Blue']

#     df = pd.DataFrame(columns=I)
#     df2 = pd.DataFrame(columns=[
#                        'Power Gen.', 'Energy Stor.' 'Electrolysis', 'SMR+CC', 'H2 Storage', 'CCUS'])

#     # cost_scenario_list = [conservative.name]
#     cost_scenario_list = [moderate.name]
#     # cost_scneario_list = [advanced.name]

#     for scenario_ in cost_scenario_list:
#         for year_ in year_list:
#             div_ = sum(DATA_[scenario_][year_]['Net_P']['HO']
#                        [k]['P_annual'] for k in h2_list)
#             list_ = []
#             for i in I:
#                 list_.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i][j] for j in [
#                              'Capex', 'Opex_fix', 'Opex_var'])/div_)
#             # print(list_)

#             df.loc[year_] = list_
#         # view data
#         df['Year'] = df.index
#         df['AQoff'] = df['AQoff_SMR']  # + df['AQoff_DAC']
#         df['H2 Storage'] = sum(df[i] for i in I2)
#         df['CCUS'] = sum(df[i] for i in I3)
#         df2['Power Gen.'] = sum(df[i] for i in ['PV', 'WF',  'ASMR'])
#         df2['Energy Stor.'] = sum(df[i] for i in ['LiI_c', 'PSH_c', 'CAES_c'])

#         # df2['Power System'] = df2['Power System']/max(df2['Power System'])
#         df2['Electrolysis'] = df['AKE']  # /max(df['AKE'])
#         df2['SMR+CC'] = df['SMRH']  # /max(df['SMRH'])
#         df2['H2 Storage'] = df['H2 Storage']
#         df2['CCUS'] = df['CCUS']

#         list2_, list3_, list4_, list5_ = ([] for _ in range(4))
#         for year_ in year_list:
#             div_ = sum(DATA_[scenario_][year_]['Net_P']['HO']
#                        [k]['P_annual'] for k in h2_list)
#             list2_.append(-1*DATA_[scenario_][year_]
#                           ['Net_P']['HO']['EOR']['Credit']/div_)
#             list3_.append(-1*sum(DATA_[scenario_][year_]['Net_P']['HO']
#                           [i]['Credit'] for i in ['AQoff_SMR'])/div_)  # 'AQoff_DAC',
#             list4_.append(-1*DATA_[scenario_][year_]
#                           ['Net_P']['HO']['MEFC']['Credit']/div_)
#             list5_.append(DATA_[scenario_][year_]['Net_S']
#                           ['HO']['CH4']['B_annual']/div_)

#         df2['45Q-EOR'] = list2_
#         df2['45Q-Aquifer'] = list3_
#         df2['45Q-Methanol'] = list4_
#         df2['NG Purchase'] = list5_

#         cols = ['Power Gen.', 'Energy Stor.' 'Electrolysis', 'SMRH ', 'Rest']
#         # df2[cols] = df2[cols].div(df2[cols].sum(axis=1), axis=0).multiply(100)
#         df2['Year'] = df2.index + 2022
#     # plot data in stack manner of bar type
#         width = 0.8
#         space = 0.9
#         fig, ax = plt.subplots(figsize=(10, 5))

#         bar1 = ax.bar(df2['Year'], df2['Power Gen.'], width,
#                       color='darkorange', label='Power Gen.')
#         bar2 = ax.bar(df2['Year'], df2['Energy Stor.'], width,
#                       bottom=df2['Power Gen.'], color='royalblue', label='Energy Sto.')
#         bar3 = ax.bar(df2['Year'], df2['NG Purchase'], width, bottom=df2['Energy Stor.'] +
#                       df2['Power Gen.'], color='slategrey', label='NG Purchase')
#         bar4 = ax.bar(df2['Year'], df2['SMR+CC'], width, bottom=df2['Energy Stor.'] +
#                       df2['Power Gen.'] + df2['NG Purchase'], color='cadetblue', label='SMR+CC')
#         bar5 = ax.bar(df2['Year'], df2['Electrolysis'], width, bottom=df2['Energy Stor.'] +
#                       df2['Power Gen.'] + df2['NG Purchase'] + df2['SMR+CC'], color='forestgreen', label='Electrolysis')
#         bar6 = ax.bar(df2['Year'], df2['H2 Storage'], width, bottom=df2['Energy Stor.'] + df2['Power Gen.'] +
#                       df2['Electrolysis'] + df2['NG Purchase'] + df2['SMR+CC'], color='indianred', label='H2 Storage')
#         bar7 = ax.bar(df2['Year'], df2['CCUS'], width, bottom=df2['Energy Stor.'] + df2['Power Gen.'] +
#                       df2['Electrolysis'] + df2['NG Purchase'] + df2['SMR+CC'] + df2['H2 Storage'], color='purple', label='CCUS')

#         # bar7 = ax.bar(df2['Year'], df2['45Q-EOR'], width, bottom = df2['45Q-Aquifer']+ df2['45Q-Methanol'], color = 'slateblue',  label = '45Q-EOR')
#         # bar8 = ax.bar(df2['Year'], df2['45Q-Aquifer'],   width, bottom = df2['45Q-Methanol'], color = 'saddlebrown', label = '45Q-Aquifer')
#         # bar9 = ax.bar(df2['Year'], df2['45Q-Methanol'], width, color = 'teal', label = '45Q-Methanol')

#         # bar5 = ax.bar(df2['Year'], df2['45Q-EOR'], width)

#         plt.title('Contribution to total hydrogen cost [\$/kg.$H_{2}$] \n under a ' + scenario_.lower(
#         ) + ' cost scenario', fontsize=16, color='midnightblue', y=1)
#         # plt.subtitle(, fontsize=14, y = 0.98)
#         plt.xlabel('Year', fontsize=14)
#         plt.ylabel('$', fontsize=14)
#         plt.legend(fontsize=14)
#         plt.xticks(fontsize=14)
#         plt.yticks(fontsize=14)
#         ax.set_xticks(df2['Year'])

#         ax.xaxis.set_ticks_position('both')
#         ax.yaxis.set_ticks_position('both')

#         # x_ = list(range(2022,2032))
#         x_ = [i + 2022 for i in year_list]
#         y_ = [1]*len(x_)
#         ax.scatter(x_, y_, alpha=0.0001, color='black', marker='*')

#         ax.yaxis.set_minor_locator(AutoMinorLocator())
#         annot, Y_ = [], []
#         for year_ in year_list:

#             value = DATA_[scenario_][year_]['Total']['HO']['LCOH']

#             annot.append(str(round(value, 2)))
#             Y_.append(value)

#         for i, txt in enumerate(annot):
#             ax.annotate(txt, (x_[i], y_[i]), verticalalignment='top',
#                         horizontalalignment='center', fontsize=14, color='midnightblue')

#         ax.scatter(x_, Y_,  s=20, facecolors='r', edgecolors='r', zorder=2)
#         ax.plot(x_, Y_, color='r', zorder=2)
#         lgd = plt.legend(bbox_to_anchor=(1.005, 1), fontsize=13)
#         # plt.ylim([-0.5,2])
#         plt.grid(alpha=0.25)
#         plt.tight_layout()
#         plt.savefig('h2_contr_' + scenario_.lower() + '.png', dpi=1200)
#         plt.show()

#     return


# for DATA_ in DATA:
#     plot_ = h_cost_contr_cc(DATA_, year_list)

# # %%
# for year in year_list:
#     print(DATA[0]['moderate'][year]['Total'][HO.name]['CO2_total'])
# # %%
# # files = ['esh_cc_m', 'esh_cc_q_m', 'esh_bc__m']
# files = ['esh_wcc_m', 'esh_wccq_m', 'esh_base_m']

# DATA = []
# for data_ in files:
#     with open(data_ + '.pkl', 'rb') as f_:
#         locals()[data_] = pkl.load(f_)
#     DATA.append(locals()[data_])
# plt.rcParams.update({'font.size': 13})
# x_ = [i + 2022 for i in year_list]
# iter_ = 0
# label = ['carbon capture w.o. credits',
#          'carbon capture w. credits', 'no carbon capture']
# scenario = ['advanced', 'moderate', 'conservative']
# colors = ['b', 'g', 'r']
# ls = ['--', '-.', '-']
# for DATA_ in DATA:
#     y_ = []

#     for year in year_list:
#         y_.append(DATA_[moderate.name][year]['Total'][HO.name]['LCOH'])
#     plt.plot(x_, y_, label=label[iter_],
#              linestyle=ls[iter_], color=colors[iter_])
#     plt.legend(loc='lower left', fontsize=13)
#     plt.ylim(0, 3.6)
#     iter_ += 1
# plt.title('Levelized cost of hydrogen (LCOH)', fontsize=13)
# plt.xlabel('Year')
# plt.ylabel('$')
# plt.show()
# plt.rcdefaults()
# # %%


# # files = ['esh_cc_m', 'esh_cc_q_m', 'esh_bc__m']
# files = ['esh_cc_m']
# # files = ['esh_cc_q_m']
# # files = ['esh_bc__m']
# plt.rcParams.update({'font.size': 13})
# DATA = []
# for data_ in files:
#     with open(data_ + '.pkl', 'rb') as f_:
#         locals()[data_] = pkl.load(f_)
#     DATA.append(locals()[data_])
# y0_, y1_, y2_, y3_, y4_,  = ([] for _ in range(5))
# for year in year_list:
#     # print(DATA[0]['moderate'][year]['Net_P'][HO.name][AKE.name]['Cap_P'])
#     # print(DATA[0]['moderate'][year]['Net_P'][HO.name][WF.name]['Cap_P'])
#     # print(DATA[0]['moderate'][year]['Net_P'][HO.name][PV.name]['Cap_P'])
#     y1_.append(DATA[0]['moderate'][year]['Net_P']
#                [HO.name][AQoff_SMR.name]['Cap_P']/907.185)
#     y2_.append(DATA[0]['moderate'][year]['Net_P'][HO.name][ASMR.name]['Cap_P'])
#     y3_.append(DATA[0]['moderate'][year]['Net_P'][HO.name][AKE.name]['Cap_P'])
#     y4_.append(DATA[0]['moderate'][year]['Net_P']
#                [HO.name][SMRH.name]['Cap_P']/907.185)

#     # print(DATA[0]['moderate'][year]['Net_P'][HO.name][EOR.name]['Cap_P'])
# x_ = [i + 2022 for i in year_list]
# y0_ = [demand_dict[i] for i in year_list]
# fig, ax = plt.subplots(5, 1, figsize=(10, 10), sharex=True)
# # , color = 'seagreen', alpha = 0.8)
# ax[0].bar(x_, y0_, label='Hydrogen Demand')
# # , color = 'royalblue', alpha = 0.8)
# ax[1].bar(x_, y1_, label='Saline aquifer capacity')
# # , color = 'royalblue', alpha = 0.8)
# ax[2].bar(x_, y2_, label='Modular Nuclear')
# # , color = 'royalblue', alpha = 0.8)
# ax[3].bar(x_, y3_, label='Alkaline water electrolysis')
# # , color = 'royalblue', alpha = 0.8)
# ax[4].bar(x_, y4_, label='SMR + carbon capture')

# # ax[0].set_title('Hydrogen Demand', fontsize = 13)
# # ax[1].set_title('Saline aquifer capacity', fontsize = 13)
# # ax[2].set_title('Modular Nuclear', fontsize = 13)
# # ax[3].set_title('Alkaline water electrolysis', fontsize = 13)
# # ax[4].set_title('Steam methane reforming + carbon capture', fontsize = 13)


# ax[0].set_ylabel('ton/day', fontsize=13)
# ax[1].set_ylabel('ton/hour', fontsize=13)
# ax[2].set_ylabel('MW', fontsize=13)
# ax[3].set_ylabel('MW', fontsize=13)
# ax[4].set_ylabel('ton/hour', fontsize=13)

# ax[4].set_xlabel('Year', fontsize=14)

# for i in range(5):
#     ax[i].legend()
# plt.show()
# plt.rcdefaults()


# # %%

# files = ['esh_cc_m']
# # files = ['esh_cc_q_m']
# # files = ['esh_bc__m']
# plt.rcParams.update({'font.size': 13})
# DATA = []
# for data_ in files:
#     with open(data_ + '.pkl', 'rb') as f_:
#         locals()[data_] = pkl.load(f_)
#     DATA.append(locals()[data_])
# y0_, y1_, y2_, y3_, y4_,  = ([] for _ in range(5))
# for year in year_list:
#     # print(DATA[0]['moderate'][year]['Net_P'][HO.name][AKE.name]['Cap_P'])
#     # print(DATA[0]['moderate'][year]['Net_P'][HO.name][WF.name]['Cap_P'])
#     # print(DATA[0]['moderate'][year]['Net_P'][HO.name][PV.name]['Cap_P'])
#     y1_.append(DATA[0]['moderate'][year]['Net_P']
#                [HO.name][AQoff_SMR.name]['Cap_P']/907.185)
#     y2_.append(DATA[0]['moderate'][year]['Net_P'][HO.name][ASMR.name]['Cap_P'])
#     y3_.append(DATA[0]['moderate'][year]['Net_P'][HO.name][AKE.name]['Cap_P'])
#     y4_.append(DATA[0]['moderate'][year]['Net_P']
#                [HO.name][SMRH.name]['Cap_P']/907.185)

#     # print(DATA[0]['moderate'][year]['Net_P'][HO.name][EOR.name]['Cap_P'])
# x_ = [i + 2022 for i in year_list]
# y0_ = [demand_dict[i] for i in year_list]

# y00_ = [0] + y0_
# y11_ = [0] + y1_
# y22_ = [0] + y2_
# y33_ = [0] + y3_
# y44_ = [0] + y4_

# y00_ = y00_[:-1]
# y11_ = y11_[:-1]
# y22_ = y22_[:-1]
# y33_ = y33_[:-1]
# y44_ = y44_[:-1]

# y0_ = [i - j for i, j in zip(y0_, y00_)]
# y1_ = [i - j for i, j in zip(y1_, y11_)]
# y2_ = [i - j for i, j in zip(y2_, y22_)]
# y3_ = [i - j for i, j in zip(y3_, y33_)]
# y4_ = [i - j for i, j in zip(y4_, y44_)]

# fig, ax = plt.subplots(5, 1, figsize=(10, 10), sharex=True)
# ax[0].bar(x_, y0_, label='Hydrogen Demand', color='indianred', alpha=0.8)
# ax[1].bar(x_, y1_, label='Saline aquifer capacity',
#           color='slategrey', alpha=0.8)
# ax[2].bar(x_, y2_, label='Modular Nuclear', color='royalblue', alpha=0.8)
# ax[3].bar(x_, y3_, label='Alkaline water electrolysis',
#           color='seagreen', alpha=0.8)
# ax[4].bar(x_, y4_, label='SMR + carbon capture',
#           color='cornflowerblue', alpha=0.8)

# # ax[0].set_title('Hydrogen Demand', fontsize = 13)
# # ax[1].set_title('Saline aquifer capacity', fontsize = 13)
# # ax[2].set_title('Modular Nuclear', fontsize = 13)
# # ax[3].set_title('Alkaline water electrolysis', fontsize = 13)
# # ax[4].set_title('Steam methane reforming + carbon capture', fontsize = 13)


# ax[0].set_ylabel('+ton/day', fontsize=13)
# ax[1].set_ylabel('+ton/hour', fontsize=13)
# ax[2].set_ylabel('+MW', fontsize=13)
# ax[3].set_ylabel('+MW', fontsize=13)
# ax[4].set_ylabel('+ton/hour', fontsize=13)

# ax[4].set_xlabel('Year', fontsize=14)
# ax[4].set_xticks(x_, fontsize=14)

# for i in range(5):
#     ax[i].legend(loc='upper left')
# ax[0].set_title('Capacity expanded to meet additional hydrogen demand')
# plt.show()
# plt.rcdefaults()

# # %%

# files = ['esh_bc__a', 'esh_bc__m', 'esh_bc__c']

# DATA = []
# for data_ in files:
#     with open(data_ + '.pkl', 'rb') as f_:
#         locals()[data_] = pkl.load(f_)
#     DATA.append(locals()[data_])
# plt.rcParams.update({'font.size': 13})
# x_ = [i + 2022 for i in year_list]
# iter_ = 0

# ls = ['--', '-.', '-']
# for DATA_ in DATA:
#     y_ = []

#     for year in year_list:
#         y_.append(DATA_[scenario[iter_]][year]['Total'][HO.name]['LCOH'])
#     plt.plot(x_, y_, label=scenario[iter_], linestyle=ls[iter_])
#     plt.legend(loc='lower left', fontsize=13)
#     plt.ylim(0, 3.6)
#     iter_ += 1
# plt.title('Levelized cost of hydrogen (LCOH) by scenario', fontsize=13)
# plt.xlabel('Year')
# plt.ylabel('\$/kg.$H_2$')
# plt.grid(alpha=0.3)
# plt.show()
# plt.rcdefaults()

# # %%

# # files = ['esh_bc__a', 'esh_bc__m', 'esh_bc__c']
# # files = ['esh_cc_m', 'esh_cc_q_m', 'esh_bc__m']
# files = ['esh_base_m', 'esh_wcc_m', 'esh_wccq_m']

# DATA = []
# for data_ in files:
#     with open(data_ + '.pkl', 'rb') as f_:
#         locals()[data_] = pkl.load(f_)
#     DATA.append(locals()[data_])
# plt.rcParams.update({'font.size': 13})
# x_ = [i + 2022 for i in year_list]
# iter_ = 0
# scenario = ['base', 'cc', 'ccq']
# # ls = ['--', '-.', '-']
# for DATA_ in DATA:
#     y_ = []

#     for year in year_list:
#         # y_.append(DATA_[moderate.name][year]['Total'][HO.name]['CO2_int'])
#         y_.append(DATA_[moderate.name][year]['Total'][HO.name]['LCOH'])

#     plt.plot(x_, y_, label=scenario[iter_])
#     plt.legend(loc='lower left', fontsize=13)
#     plt.ylim(0, 10)
#     iter_ += 1
# plt.title('Carbon intensity', fontsize=13)
# plt.xlabel('Year')
# plt.ylabel('$')
# plt.grid(alpha=0.3)
# plt.show()
# plt.rcdefaults()


# # %%

# # files = ['esh_bc__a', 'esh_bc__m', 'esh_bc__c']
# # files = ['esh_cc_m', 'esh_cc_q_m', 'esh_bc__m']
# files = ['esh_base_m', 'esh_wcc_m', 'esh_wccq_m']
# DATA = []
# for data_ in files:
#     with open(data_ + '.pkl', 'rb') as f_:
#         locals()[data_] = pkl.load(f_)
#     DATA.append(locals()[data_])
# plt.rcParams.update({'font.size': 13})

# y1_, y2_ = [], []
# for DATA_ in DATA:
#     y1_.append(DATA_[moderate.name][8]['Total'][HO.name]['CO2_int'])
#     y2_.append(DATA_[moderate.name][8]['Total'][HO.name]['LCOH'])


# classes = ['no carbon capture', 'carbon capture w.o. credits',
#            'carbon capture w. credits']
# values = [0, 1, 2]
# colors = ListedColormap(['r', 'b', 'g'])
# scatter = plt.scatter(y2_, y1_, c=values, cmap=colors)
# plt.legend(handles=scatter.legend_elements()[0], labels=classes)
# plt.title('LCOH v/s carbon intensity trade-off', fontsize=13)
# plt.xlabel('\$/kg.$H_2$')
# plt.ylabel('kg.$CO_2$-eq/kg.$H_2$')
# plt.ylim(0, 10)
# # plt.xlim(0,2.6)

# plt.grid(alpha=0.3)
# plt.legend(handles=scatter.legend_elements()[0], labels=classes)
# plt.show()
# plt.rcdefaults()

# %%


# %%

# def fetch_geo_data():

#     df_ = pd.DataFrame()
#     df_1= pd.read_csv('Bagasse_By_County.csv')
#     df_2= pd.read_csv('Barley_Straw_By_County.csv')
#     df_3= pd.read_csv('bio_prime_mills.csv')
#     df_4= pd.read_csv('bioforests.csv')
#     df_5= pd.read_csv('biogas_methane_from_landfills.csv')
#     df_6= pd.read_csv('biogas_methane_pot_animal_manure.csv')
#     df_7= pd.read_csv('biogas_methane_pot_industrial.csv')
#     df_8= pd.read_csv('biogas_methane_pot_wastewater.csv')
#     df_9= pd.read_csv('Corn_Stover_By_County.csv')
#     df_10= pd.read_csv('cropres_grain_sorgh_stub_by_county.csv')
#     df_11= pd.read_csv('Rice_Straw_By_County.csv')
#     df_14= pd.read_csv('Wheat_Straw_by_County.csv')
#     df_15= pd.read_csv('us_counties_reatlas.csv')


#     #rng = range(0, 24)
#     #col_ = [df_str(i) for i in rng]
#     #for i in rng_:
#     df_1 = df_1.sort_values(by=['gid'])
#     df_2 = df_2.sort_values(by=['gid'])
#     #df_3 = df_3.sort_values(by=['gid'])
#     #df_4 = df_4.sort_values(by=['gid'])
#     df_5 = df_5.sort_values(by=['gid'])
#     df_6 = df_6.sort_values(by=['gid'])
#     df_7 = df_7.sort_values(by=['gid'])
#     df_8 = df_8.sort_values(by=['gid'])
#     df_9 = df_9.sort_values(by=['gid'])
#     df_10 = df_10.sort_values(by=['gid'])
#     df_11 = df_11.sort_values(by=['gid'])
#     df_14 = df_14.sort_values(by=['gid'])
#     df_15= df_15.sort_values(by=['gid'])

#     df_['gid']= df_1['gid']
#     df_['fips']= df_15['fips']
#     df_['area']= df_15['area']
#     df_['state']= df_1['state_name']
#     df_['county']= df_1['name']
#     df_['bagasse']= df_1.iloc[:,-1:]
#     df_['barley_straw']= df_2.iloc[:,-1:]
#     df_['mill_residues']= df_3.iloc[:,-1:]
#     df_['forest_residues']= df_4.iloc[:,-1:]
#     df_['landfill_methane']= df_5.iloc[:,-1:]
#     df_['manure_methane']= df_6.iloc[:,-1:]
#     df_['industrial_methane']= df_7.iloc[:,-1:]
#     df_['wastewater_methane']= df_8.iloc[:,-1:]
#     df_['corn_stover']= df_9.iloc[:,-1:]
#     df_['grain_sorghum_stubble']= df_10.iloc[:,-1:]
#     df_['rice_straw']= df_11.iloc[:,-1:]
#     df_['wheat_straw']= df_14.iloc[:,-1:]

#     df_.index = df_['gid']
#     df_ = df_.drop(columns = ['gid'])

#     return df_


# def get_geo_info(y_, state_, county_):
#     df_ = AMERICA()
#     k_ = df_[y_][(df_['state']==state_) & (df_['county']== county_)]
#     #print(k_)
#     return k_
# """
#     example:get_geo_info('area', 'California', 'Riverside')
#     #=====================================
#     # List of attributes:
#     # gid
#     # fips
#     # area
#     # state
#     # county
#     # bagasse
#     # barley_straw
#     # mill_residues
#     # forest_residues
#     # landfill_methane
#     # manure_methane
#     # industrial_methane
#     # wastewater_methane
#     # corn_stover
#     # grain_sorghum_stubble
#     # rice_straw
#     # wheat_straw
#     =======================================
# """
# def biomass_profile(state_, county_, type_):
#     df_ = AMERICA()
#     if type_ == 'crop':
#         k_1 = df_['bagasse'][(df_['state']==state_) & (df_['county']== county_)]
#         k_2 = df_['barley_straw'][(df_['state']==state_) & (df_['county']== county_)]
#         k_3 = df_['corn_stover'][(df_['state']==state_) & (df_['county']== county_)]
#         k_4 = df_['grain_sorghum_stubble'][(df_['state']==state_) & (df_['county']== county_)]
#         k_5 = df_['rice_straw'][(df_['state']==state_) & (df_['county']== county_)]
#         k_6 = df_['wheat_straw'][(df_['state']==state_) & (df_['county']== county_)]
#         k_ = k_1 + k_2 + k_3 + k_4 + k_5 + k_6
#         #print('bagasse: ' + str(k_1) + ' barley straw: ' + str(k_2) + ' corn stover: ' + str(k_3) + ' grain sorghum stubble: ' + str(k_4) + ' rice straw: ' + str(k_5) + ' wheat straw: ' + str(k_6) + 'total: ' + str(k_))
#         print(str(k_1) + str(k_2) +  str(k_3) + str(k_4) + str(k_5) + str(k_6) + 'total: ' + str(k_))
#     if type_ == 'forest':
#         k_ = df_['forest_residues'][(df_['state']==state_) & (df_['county']== county_)]
#         print('forest residues:' + str(k_))

#     return
# """
#     example:biomass_profile('Texas', 'Harris', 'crop')
#     types: 'forest' and 'crop'
# """
# #CAUTION: # geopandas incompatible with matplot; run on conda:geo_env; strictly do not run on conda:NRGAEA
# def geo_plot(y_, focus_):
#     df_  = AMERICA()
#     if focus_ == 'USA':
#         fig = ff.create_choropleth(fips=df_['fips'], values=df_[y_], scope = focus_)
#         fig.layout.template = None
#         fig.show()

#     #else:
#         fig = ff.create_choropleth(fips=df_['fips'], values=df_[y_], scope = focus_)
#         fig.layout.template = None
#         fig.show()
# """
#     geo_plot('population', 'USA')
# """
# def only_renewable(df_):
#     df_ = df_[['Solar', 'Wind']]
#     df_['h'] = df_.index.strftime('%j').astype(int)
#     df_['h'] = df_['h']
#     df_['t'] = df_.index.strftime('%H')
#     df_['t'] = pd.to_numeric(df_['t'])
#     df_ = df_.reset_index(drop = True)
#     return df_

# def split_solar_wind(df_):
#     df_ = df_.reset_index(drop=True)
#     df1_ = pd.DataFrame()
#     df2_ = pd.DataFrame()
#     df1_ = pd.concat([df_['h'], df_['t'], df_['Solar']], axis=1)
#     df2_ = pd.concat([df_['h'], df_['t'], df_['Wind']], axis=1)
#     return df1_ , df2_

# def make_B_max(df1_, loc1_, df2_, loc2_):
#     dict_keys=[]

#     for i in range(1,366):
#         for j in range(1,25):
#             #dict_keys.append(("s"+str(i), j))
#             dict_keys.append((i, j))

#     dict1_solar = {}
#     dict2_solar = {}
#     dict1_wind = {}
#     dict2_wind = {}
#     dict_temp = {}
#     dict_H20 = {}

#     for i in dict_keys:
#         keys = [i[0],i[1]]
#         value = 0

#         sub_dict1_solar = dict1_solar
#         sub_dict2_solar = dict2_solar
#         sub_dict1_wind = dict1_wind
#         sub_dict2_wind = dict2_wind
#         sub_dict_temp = dict_temp
#         sub_dict_H20 = dict_H20

#         for key_ind, key in enumerate(keys[:-1]):
#             if not key_ind:
#                 sub_dict1_solar = dict1_solar.setdefault(key, {})
#                 sub_dict2_solar = dict2_solar.setdefault(key, {})
#                 sub_dict1_wind = dict1_wind.setdefault(key, {})
#                 sub_dict2_wind = dict2_wind.setdefault(key, {})
#                 sub_dict_temp = dict_temp.setdefault(key, {})
#                 sub_dict_H20 = dict_H20.setdefault(key, {})
#             else:
#                 sub_dict1_solar = sub_dict1_solar.setdefault(key, {})
#                 sub_dict2_solar = sub_dict2_solar.setdefault(key, {})
#                 sub_dict1_wind = sub_dict1_wind.setdefault(key, {})
#                 sub_dict2_wind = sub_dict2_wind.setdefault(key, {})
#                 sub_dict_temp = dict_temp.setdefault(key, {})
#                 sub_dict_H20 = dict_H20.setdefault(key, {})
#         sub_dict1_solar[keys[-1]] = float(value)
#         sub_dict2_solar[keys[-1]] = float(value)
#         sub_dict1_wind[keys[-1]] = float(value)
#         sub_dict2_wind[keys[-1]] = float(value)
#         sub_dict_temp[keys[-1]] = float(value)
#         sub_dict_H20[keys[-1]] = 100


# # %%

# %%

# def full_pie_grid(results_dict:dict, location:energia.location, conv_dict:dict):
#     """Plot a pie grid with three levels:
#     1. power contribution over the year
#     2. Carbon dioxide contribution

#     3. hydrogen contribution
#     OR
#     3. miles contribution
#     """


#     scenario_list = [scenario for scenario in results_dict.keys()]
#     for scenario in scenario_list:
#         year_list = [year for year in results_dict[scenario.name].keys()]

#         wind = get_annual_results(results_dict = results_dict, for_what = WF, result_metric = 'P_annual', location = location.name, scenario = scenario, year_list = year_list)
#         solar = get_annual_results(results_dict = results_dict, for_what = PV, result_metric = 'P_annual', location = location.name, scenario = scenario, year_list = year_list)

#         h2_green = get_annual_results(results_dict = results_dict, for_what = H2_Green, result_metric = 'P_annual', location = location.name, scenario = scenario, year_list = year_list)
#         h2_blue = get_annual_results(results_dict = results_dict, for_what = H2_Blue, result_metric = 'P_annual', location = location.name, scenario = scenario, year_list = year_list)

#         h2_local = get_annual_results(results_dict = results_dict, for_what = H2_C, result_metric = 'S_annual', location = location.name, scenario = scenario, year_list = year_list)
#         h2_geol = get_annual_results(results_dict = results_dict, for_what = H2_L, result_metric = 'S_annual', location = location.name, scenario = scenario, year_list = year_list)

#         smrh_co2 = get_annual_results(results_dict = results_dict, for_what = SMRH, result_metric = 'P_annual', location = location.name, scenario = scenario, year_list = year_list)
#         eor_co2 = get_annual_results(results_dict = results_dict, for_what = EOR, result_metric = 'P_annual', location = location.name, scenario = scenario, year_list = year_list)

#         smrh_co2 = [i*conv_dict['SMRH']['CO2_Vent'] for i in smrh_co2]
#         eor_co2 = [i*conv_dict['SMRH']['CO2_Vent'] for i in eor_co2]

#         Miles_MEOH.append(results_dict[scenario.name][year]['Net_S']['HO']['CH3OH']['Mile_annual'])
#         Miles_H2.append(sum(results_dict[scenario.name][year]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L']))
#         Miles_Pow.append(results_dict[scenario.name][year]['Net_S']['HO']['Power']['Mile_annual'])

#         Total_CO2.append(results_dict[scenario.name][year]['Net_S']['HO']['CO2_Vent']['S_annual'])
#         Total_H2_d.append(sum(results_dict[scenario.name][year]['Net_S']['HO'][i_]['S_annual'] for i_ in ['H2_C', 'H2_L']))
#         Total_H2_p.append(sum(results_dict[scenario.name][year]['Net_P']['HO'][i_]['P_annual'] for i_ in ['H2_Sink1', 'H2_Sink2']))

#         Total_miles.append(sum(results_dict[scenario.name][year]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L', 'Power', 'CH3OH']))
#         Total_Pow.append(sum(results_dict[scenario.name][year]['Net_P']['HO'][i_]['P_annual'] for i_ in ['PV', 'WF']))

#         X_.append(int(year + 2022))


#         Y1_ = [1]*len(X_)
#         Y2_ = [2]*len(X_)
#         Y3_ = [3]*len(X_)
#         Y4_ = [4]*len(X_)
#         Y5_ = [5]*len(X_)

#         fig, ax = plt.subplots(figsize = (12, 8))

#         for year in year_list:

#             r1 = Wind[year]/Total_Pow[year]
#             r2 = r1 + Solar[year]/Total_Pow[year]
#             x1 = np.cos(2 * np.pi * np.linspace(0, r1))
#             y1 = np.sin(2 * np.pi * np.linspace(0, r1))
#             xy1 = np.row_stack([[0, 0], np.column_stack([x1, y1])])

#             x2 = np.cos(2 * np.pi * np.linspace(r1, r2))
#             y2 = np.sin(2 * np.pi * np.linspace(r1, r2))
#             xy2 = np.row_stack([[0, 0], np.column_stack([x2, y2])])

#             plt.scatter(X_[year], Y1_[year], s  = 3000*Total_Pow[year]/max(Total_Pow), marker = xy1, color = 'royalblue')
#             plt.scatter(X_[year], Y1_[year], s = 3000*Total_Pow[year]/max(Total_Pow), marker = xy2, color = 'gold')

#             if Total_CO2[year] ==0:
#                 r3 = 0
#                 r4 = r3 + 0
#             else:
#                 r3 = SMRH[year]/Total_CO2[year]
#                 r4 = r3 + EOR[year]/Total_CO2[year]

#             x3 = np.cos(2 * np.pi * np.linspace(0, r3))
#             y3 = np.sin(2 * np.pi * np.linspace(0, r3))
#             xy3 = np.row_stack([[0, 0], np.column_stack([x3, y3])])

#             x4 = np.cos(2 * np.pi * np.linspace(r3, r4))
#             y4 = np.sin(2 * np.pi * np.linspace(r3, r4))
#             xy4 = np.row_stack([[0, 0], np.column_stack([x4, y4])])

#             plt.scatter(X_[year], Y2_[year], s  = 3000*Total_CO2[year]/max(Total_CO2), marker = xy3, color = 'cadetblue')
#             plt.scatter(X_[year], Y2_[year], s = 3000*Total_CO2[year]/max(Total_CO2), marker = xy4, color = 'slategrey')

#             r5 = Blue_H2[year]/Total_H2_p[year]
#             r6 = r5 + Green_H2[year]/Total_H2_p[year]
#             x5 = np.cos(2 * np.pi * np.linspace(0, r5))
#             y5 = np.sin(2 * np.pi * np.linspace(0, r5))
#             xy5 = np.row_stack([[0, 0], np.column_stack([x5, y5])])

#             x6 = np.cos(2 * np.pi * np.linspace(r5, r6))
#             y6 = np.sin(2 * np.pi * np.linspace(r5, r6))
#             xy6 = np.row_stack([[0, 0], np.column_stack([x6, y6])])

#             plt.scatter(X_[year], Y3_[year], s  = 3000*Total_H2_p[year]/max(Total_H2_p), marker = xy5, color = 'blue')
#             plt.scatter(X_[year], Y3_[year], s = 3000*Total_H2_p[year]/max(Total_H2_p), marker = xy6, color = 'green')

#             r7 = Loc_H2[year]/Total_H2_d[year]
#             r8 = r7 + Geo_H2[year]/Total_H2_d[year]
#             x7 = np.cos(2 * np.pi * np.linspace(0, r7))
#             y7 = np.sin(2 * np.pi * np.linspace(0, r7))
#             xy7 = np.row_stack([[0, 0], np.column_stack([x7, y7])])

#             x8 = np.cos(2 * np.pi * np.linspace(r7, r8))
#             y8 = np.sin(2 * np.pi * np.linspace(r7, r8))
#             xy8 = np.row_stack([[0, 0], np.column_stack([x8, y8])])

#             plt.scatter(X_[year], Y4_[year], s  = 3000*Total_H2_d[year]/max(Total_H2_d), marker = xy7, color = 'yellow')
#             plt.scatter(X_[year], Y4_[year], s = 3000*Total_H2_d[year]/max(Total_H2_d), marker = xy8, color = 'orange')


#             r9 = Miles_MEOH[year]/Total_miles[year]
#             r10 = r9 + Miles_H2[year]/Total_miles[year]
#             r11 = r9 + r10 + Miles_Pow[year]/Total_miles[year]

#             x9 = np.cos(2 * np.pi * np.linspace(0, r9))
#             y9 = np.sin(2 * np.pi * np.linspace(0, r9))
#             xy9 = np.row_stack([[0, 0], np.column_stack([x9, y9])])

#             x10 = np.cos(2 * np.pi * np.linspace(r9, r10))
#             y10 = np.sin(2 * np.pi * np.linspace(r9, r10))
#             xy10 = np.row_stack([[0, 0], np.column_stack([x10, y10])])

#             x11 = np.cos(2 * np.pi * np.linspace(r10, r11))
#             y11 = np.sin(2 * np.pi * np.linspace(r10, r11))
#             xy11 = np.row_stack([[0, 0], np.column_stack([x11, y11])])

#             plt.scatter(X_[year], Y5_[year], s  = 3000*Total_miles[year]/max(Total_miles), marker = xy9, color = 'firebrick')
#             plt.scatter(X_[year], Y5_[year], s = 3000*Total_miles[year]/max(Total_miles), marker = xy10, color = 'mediumseagreen')
#             plt.scatter(X_[year], Y5_[year], s = 3000*Total_miles[year]/max(Total_miles), marker = xy11, color = 'mediumturquoise')

#         # colors = ['royalblue', 'gold', 'cadetblue', 'slategrey', 'blue', 'green', 'yellow', 'orange', 'firebrick', 'olive', 'mediumturquoise']

#         # labels = ['Wind', 'Solar', 'SMR+CC', 'EOR',  'Blue $H_{2}$', 'Green $H_{2}$', 'Local', 'Geological',  'Methanol(90%)', 'HFCV', 'EV']

#         colors = ['firebrick', 'mediumseagreen', 'mediumturquoise', 'yellow', 'orange', 'blue', 'green', 'cadetblue', 'slategrey',  'royalblue', 'gold' ]

#         labels = ['Methanol(90%)', 'HFCV', 'EV', 'Local', 'Geological', 'Blue $H_{2}$', 'Green $H_{2}$',   'SMR+CC', 'EOR', 'Wind', 'Solar',   ]


#         patches = []
#         for i in range(len(colors)):
#             patches.append(mpatches.Patch(color=colors[i], label=labels[i]))

#         plt.legend(handles= patches, bbox_to_anchor=(1.03, 1))
#             # lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--') for c in colors]
#             # plt.legend(lines, labels)

#         # plt.scatter(X_, Y1_, s = Total_CO2, marker = xy2)

#         #plt.scatter(X_, Y3_, s = Total_H2)#, marker = xy3)

#         #plt.scatter(X_, Y4_, s= Total_H2)#, marker = xy4)
#         plt.grid(alpha = 0.4)
#         plt.xticks(X_, fontsize = 14)
#         bars = ('Power', '$CO_{2}$ emission', '$H_{2}$ production', '$H_{2}$ dispense', 'Total miles')
#         y_pos = [1, 2, 3, 4, 5, 0, 6]
#         plt.yticks(y_pos, bars,  fontsize='14', horizontalalignment='right')
#         plt.xlabel('year_list', fontsize = 14)
#         plt.title('Trajectories for ' + scenario.name.lower() +' cost scenario', fontsize = 14)
#         x_line = [2027]*61
#         y_line = np.arange(0,6.1,0.1)
#         plt.plot(x_line, y_line , '--', alpha = 0.4, color = 'slateblue')
#         plt.ylim([0.5,5.5])

#         plt.annotate('End of term 1', (2027, 5.45), verticalalignment = 'top', horizontalalignment = 'center'\
#                 , fontsize = 14, color = 'slateblue')

#         plt.show()
#     return
# plot_ = full_pie_grid()
# #%%
# def full_pie_grid():
#     """Plot a pie grid with three levels:
#     1. power contribution over the year
#     2. Carbon dioxide contribution

#     3. hydrogen contribution
#     OR
#     3. miles contribution
#     """


#     for DATA_ in DATA:
#         SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#         for scenario_ in SCENARIO:
#             Wind, Solar, Green_H2, Blue_H2, Loc_H2, Geo_H2, SMRH, EOR, \
#                 Miles_MEOH, Miles_H2, Miles_Pow, X_,\
#                     Total_miles, Total_CO2, Total_H2_p, Total_H2_d, Total_Pow,\
#                         temp_Total_miles, temp_Total_CO2, temp_Total_H2, temp_Total_Pow, \
#                             temp_Wind, temp_Solar = ([] for _ in range(23))
#             for year_ in YEAR:

#                 Wind.append(DATA_[scenario_][year_]['Net_P']['HO']['WF']['P_annual'])
#                 Solar.append(DATA_[scenario_][year_]['Net_P']['HO']['PV']['P_annual'])

#                 Green_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual'])
#                 Blue_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual'])

#                 Loc_H2.append(DATA_[scenario_][year_]['Net_S']['HO']['H2_C']['S_annual'])
#                 Geo_H2.append(DATA_[scenario_][year_]['Net_S']['HO']['H2_L']['S_annual'])

#                 SMRH.append(DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']*dict_conversion['SMRH']['CO2_Vent'])
#                 EOR.append(DATA_[scenario_][year_]['Net_P']['HO']['EOR']['P_annual']*dict_conversion['EOR']['CO2_Vent'])

#                 Miles_MEOH.append(DATA_[scenario_][year_]['Net_S']['HO']['CH3OH']['Mile_annual'])
#                 Miles_H2.append(sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L']))
#                 Miles_Pow.append(DATA_[scenario_][year_]['Net_S']['HO']['Power']['Mile_annual'])

#                 Total_CO2.append(DATA_[scenario_][year_]['Net_S']['HO']['CO2_Vent']['S_annual'])
#                 Total_H2_d.append(sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['S_annual'] for i_ in ['H2_C', 'H2_L']))
#                 Total_H2_p.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i_]['P_annual'] for i_ in ['H2_Sink1', 'H2_Sink2']))

#                 Total_miles.append(sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L', 'Power', 'CH3OH']))
#                 Total_Pow.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i_]['P_annual'] for i_ in ['PV', 'WF']))

#                 X_.append(int(year_ + 2022))


#             Y1_ = [1]*len(X_)
#             Y2_ = [2]*len(X_)
#             Y3_ = [3]*len(X_)
#             Y4_ = [4]*len(X_)
#             Y5_ = [5]*len(X_)

#             fig, ax = plt.subplots(figsize = (12, 8))

#             for year_ in YEAR:

#                 r1 = Wind[year_]/Total_Pow[year_]
#                 r2 = r1 + Solar[year_]/Total_Pow[year_]
#                 x1 = np.cos(2 * np.pi * np.linspace(0, r1))
#                 y1 = np.sin(2 * np.pi * np.linspace(0, r1))
#                 xy1 = np.row_stack([[0, 0], np.column_stack([x1, y1])])

#                 x2 = np.cos(2 * np.pi * np.linspace(r1, r2))
#                 y2 = np.sin(2 * np.pi * np.linspace(r1, r2))
#                 xy2 = np.row_stack([[0, 0], np.column_stack([x2, y2])])

#                 plt.scatter(X_[year_], Y1_[year_], s  = 3000*Total_Pow[year_]/max(Total_Pow), marker = xy1, color = 'royalblue')
#                 plt.scatter(X_[year_], Y1_[year_], s = 3000*Total_Pow[year_]/max(Total_Pow), marker = xy2, color = 'gold')

#                 if Total_CO2[year_] ==0:
#                     r3 = 0
#                     r4 = r3 + 0
#                 else:
#                     r3 = SMRH[year_]/Total_CO2[year_]
#                     r4 = r3 + EOR[year_]/Total_CO2[year_]

#                 x3 = np.cos(2 * np.pi * np.linspace(0, r3))
#                 y3 = np.sin(2 * np.pi * np.linspace(0, r3))
#                 xy3 = np.row_stack([[0, 0], np.column_stack([x3, y3])])

#                 x4 = np.cos(2 * np.pi * np.linspace(r3, r4))
#                 y4 = np.sin(2 * np.pi * np.linspace(r3, r4))
#                 xy4 = np.row_stack([[0, 0], np.column_stack([x4, y4])])

#                 plt.scatter(X_[year_], Y2_[year_], s  = 3000*Total_CO2[year_]/max(Total_CO2), marker = xy3, color = 'cadetblue')
#                 plt.scatter(X_[year_], Y2_[year_], s = 3000*Total_CO2[year_]/max(Total_CO2), marker = xy4, color = 'slategrey')

#                 r5 = Blue_H2[year_]/Total_H2_p[year_]
#                 r6 = r5 + Green_H2[year_]/Total_H2_p[year_]
#                 x5 = np.cos(2 * np.pi * np.linspace(0, r5))
#                 y5 = np.sin(2 * np.pi * np.linspace(0, r5))
#                 xy5 = np.row_stack([[0, 0], np.column_stack([x5, y5])])

#                 x6 = np.cos(2 * np.pi * np.linspace(r5, r6))
#                 y6 = np.sin(2 * np.pi * np.linspace(r5, r6))
#                 xy6 = np.row_stack([[0, 0], np.column_stack([x6, y6])])

#                 plt.scatter(X_[year_], Y3_[year_], s  = 3000*Total_H2_p[year_]/max(Total_H2_p), marker = xy5, color = 'blue')
#                 plt.scatter(X_[year_], Y3_[year_], s = 3000*Total_H2_p[year_]/max(Total_H2_p), marker = xy6, color = 'green')

#                 r7 = Loc_H2[year_]/Total_H2_d[year_]
#                 r8 = r7 + Geo_H2[year_]/Total_H2_d[year_]
#                 x7 = np.cos(2 * np.pi * np.linspace(0, r7))
#                 y7 = np.sin(2 * np.pi * np.linspace(0, r7))
#                 xy7 = np.row_stack([[0, 0], np.column_stack([x7, y7])])

#                 x8 = np.cos(2 * np.pi * np.linspace(r7, r8))
#                 y8 = np.sin(2 * np.pi * np.linspace(r7, r8))
#                 xy8 = np.row_stack([[0, 0], np.column_stack([x8, y8])])

#                 plt.scatter(X_[year_], Y4_[year_], s  = 3000*Total_H2_d[year_]/max(Total_H2_d), marker = xy7, color = 'yellow')
#                 plt.scatter(X_[year_], Y4_[year_], s = 3000*Total_H2_d[year_]/max(Total_H2_d), marker = xy8, color = 'orange')


#                 r9 = Miles_MEOH[year_]/Total_miles[year_]
#                 r10 = r9 + Miles_H2[year_]/Total_miles[year_]
#                 r11 = r9 + r10 + Miles_Pow[year_]/Total_miles[year_]

#                 x9 = np.cos(2 * np.pi * np.linspace(0, r9))
#                 y9 = np.sin(2 * np.pi * np.linspace(0, r9))
#                 xy9 = np.row_stack([[0, 0], np.column_stack([x9, y9])])

#                 x10 = np.cos(2 * np.pi * np.linspace(r9, r10))
#                 y10 = np.sin(2 * np.pi * np.linspace(r9, r10))
#                 xy10 = np.row_stack([[0, 0], np.column_stack([x10, y10])])

#                 x11 = np.cos(2 * np.pi * np.linspace(r10, r11))
#                 y11 = np.sin(2 * np.pi * np.linspace(r10, r11))
#                 xy11 = np.row_stack([[0, 0], np.column_stack([x11, y11])])

#                 plt.scatter(X_[year_], Y5_[year_], s  = 3000*Total_miles[year_]/max(Total_miles), marker = xy9, color = 'firebrick')
#                 plt.scatter(X_[year_], Y5_[year_], s = 3000*Total_miles[year_]/max(Total_miles), marker = xy10, color = 'mediumseagreen')
#                 plt.scatter(X_[year_], Y5_[year_], s = 3000*Total_miles[year_]/max(Total_miles), marker = xy11, color = 'mediumturquoise')

#             # colors = ['royalblue', 'gold', 'cadetblue', 'slategrey', 'blue', 'green', 'yellow', 'orange', 'firebrick', 'olive', 'mediumturquoise']

#             # labels = ['Wind', 'Solar', 'SMR+CC', 'EOR',  'Blue $H_{2}$', 'Green $H_{2}$', 'Local', 'Geological',  'Methanol(90%)', 'HFCV', 'EV']

#             colors = ['firebrick', 'mediumseagreen', 'mediumturquoise', 'yellow', 'orange', 'blue', 'green', 'cadetblue', 'slategrey',  'royalblue', 'gold' ]

#             labels = ['Methanol(90%)', 'HFCV', 'EV', 'Local', 'Geological', 'Blue $H_{2}$', 'Green $H_{2}$',   'SMR+CC', 'EOR', 'Wind', 'Solar',   ]


#             patches = []
#             for i in range(len(colors)):
#                 patches.append(mpatches.Patch(color=colors[i], label=labels[i]))

#             plt.legend(handles= patches, bbox_to_anchor=(1.03, 1))
#                 # lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--') for c in colors]
#                 # plt.legend(lines, labels)

#             # plt.scatter(X_, Y1_, s = Total_CO2, marker = xy2)

#             #plt.scatter(X_, Y3_, s = Total_H2)#, marker = xy3)

#             #plt.scatter(X_, Y4_, s= Total_H2)#, marker = xy4)
#             plt.grid(alpha = 0.4)
#             plt.xticks(X_, fontsize = 14)
#             bars = ('Power', '$CO_{2}$ emission', '$H_{2}$ production', '$H_{2}$ dispense', 'Total miles')
#             y_pos = [1, 2, 3, 4, 5, 0, 6]
#             plt.yticks(y_pos, bars,  fontsize='14', horizontalalignment='right')
#             plt.xlabel('Year', fontsize = 14)
#             plt.title('Trajectories for ' + scenario_.lower() +' cost scenario', fontsize = 14)
#             x_line = [2027]*61
#             y_line = np.arange(0,6.1,0.1)
#             plt.plot(x_line, y_line , '--', alpha = 0.4, color = 'slateblue')
#             plt.ylim([0.5,5.5])

#             plt.annotate('End of term 1', (2027, 5.45), verticalalignment = 'top', horizontalalignment = 'center'\
#                     , fontsize = 14, color = 'slateblue')

#             plt.show()
#     return
# plot_ = full_pie_grid()


# def error(DATA:list):
#     iter_ = 0
#     x, y , z= [], [], []
#     fig, ax = plt.subplots(figsize = (10,6))
#     ax1 = ax.twinx()
#     for DATA_ in DATA:
#         y_ = 100*(full['Conservative'][0]['Total']['HO']['Objective'] - DATA_['Conservative'][0]['Total']['HO']['Objective'])\
#             / full['Conservative'][0]['Total']['HO']['Objective']
#         z_ = -100*(full['Conservative'][0]['Total']['HO']['comp_time'] - DATA_['Conservative'][0]['Total']['HO']['comp_time'])\
#             / full['Conservative'][0]['Total']['HO']['comp_time']
#         # z_ = 100*DATA_['Conservative'][0]['Total']['HO']['comp_time']/full['Conservative'][0]['Total']['HO']['comp_time']

#         ax.scatter(red_list[iter_], y_, color = 'red', marker = '*')
#         # ax.set_ylim(0, 10)

#         # ax.xaxis.set_ticks_position('both')
#         # ax.yaxis.set_ticks_position('both')

#         x.append(red_list[iter_])
#         y.append(y_)


#         ax1.scatter(red_list[iter_], z_, color = 'blue', marker = 'x')
#         # ax1.xaxis.set_ticks_position('both')
#         # ax1.yaxis.set_ticks_position('both')
#         # ax1.set_ylim(-100, -85)
#         z.append(z_)
#         iter_ +=1
#         # if iter_ == 10:
#         #     z_annot = -100*(full['Conservative'][0]['Total']['HO']['comp_time'] - DATA_['Conservative'][0]['Total']['HO']['comp_time'])\
#         #     / full['Conservative'][0]['Total']['HO']['comp_time']
#         #     y_annot = 100*(full['Conservative'][0]['Total']['HO']['Objective'] - DATA_['Conservative'][0]['Total']['HO']['Objective'])\
#         #     / full['Conservative'][0]['Total']['HO']['Objective']


#     ax.plot(x,y, color = 'red', linestyle = 'dashed', alpha = 0.4)
#     ax1.plot(x,z, color = 'blue', alpha = 0.4)

#     ax.set_xlabel('Number of representative days', fontsize = 16)
#     ax.set_ylabel('Objective error [%] (*)', fontsize = 16)
#     ax1.set_ylabel('Computation time [%] (x)', fontsize = 16)

#     ax.tick_params(axis = 'y', labelsize = 16, colors = 'red')
#     ax1.tick_params(axis = 'y', labelsize = 16, colors = 'blue')
#     ax.tick_params(axis = 'x', labelsize = 16)

#     ax1.spines['left'].set_color('red')
#     ax1.spines['right'].set_color('blue')


#     # plt.grid(alpha = 0.5)
#     plt.title('Comparison to full scale model', fontsize = 18)
#     # ax.plot([20], [8], marker='o', color = 'blue')
#     # ax.annotate('(' + str('{:.2f}'.format(y_annot)) + '%,' + str('{:.2f}'.format(z_annot)) + '%)',
#     #             xy=(20, 8.1), xycoords='data',
#     #             xytext=(-15, 25), textcoords='offset points',
#     #             arrowprops=dict(facecolor='blue', shrink=0.05),
#     #             horizontalalignment='left', verticalalignment='bottom', fontsize = 15)

#     plt.show()
#     return
# error(DATA)


# #%%

# def comp_time(DATA:list):
#     iter_ = 0
#     x, y = [], []
#     fig, ax = plt.subplots(figsize = (10,6))
#     for DATA_ in DATA:
#         y_ = -100*(full['Conservative'][0]['Total']['HO']['comp_time'] - DATA_['Conservative'][0]['Total']['HO']['comp_time'])/ full['Conservative'][0]['Total']['HO']['comp_time']
#         ax.scatter(red_list[iter_], y_)
#         x.append(red_list[iter_])
#         y.append(y_)
#         iter_ +=1

#     plt.plot(x,y)
#     # ticks = np.arange(50,0,-5)
#     # ticks = [si) for i in ticks]
#     plt.xticks(x, fontsize = 16)
#     plt.yticks(fontsize = 16)
#     plt.xlabel('Number of representative days', fontsize = 16)
#     plt.ylabel('Reduction in computation time [%]', fontsize = 16)

#     plt.show()
#     return
# comp_time(DATA)


# #%%

# def long_graph(DATA_:dict):
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     fig, ax = plt.subplots(figsize = (10,8))
#     for scenario_ in SCENARIO:
#         for i_ in ['WF']:
#             input_, year = [], []
#             for year_ in YEAR:
#                 # input_.append(DATA_[scenario_][year_]['Net_P']['HO'][i_]['Cap_P'])
#                 # input_.append(DATA_[scenario_][year_]['Net_P']['HO'][i_]['Land'])

#                 input_.append(DATA_[scenario_][year_]['Material']['HO'][i_]['Lithium']/500)
#                 year.append(year_+ 2022)
#             ax.tick_params(axis = 'both', labelsize = 16)
#             ax.set_xlabel('Year', fontsize = 16)
#             ax.set_ylabel('Lithium consumed (MMT) by year', fontsize = 16)
#             print(input_)
#             ax.bar(year, input_)
#             ax.set_xticks(year)
#             plt.title('System wide Lithium use (illustrative)', fontsize = 16)
#             # plt.title(I_labels_['short'][i_])

#             plt.show()

# for DATA_ in DATA:
#     p = long_graph(DATA_)


# #%%
# # years = [0, 1, 2, 3, 4]
# # years = np.arange(0,2)

# # colors = ['teal', 'lightseagreen', 'blue', 'green', ]

# def ng_sensitivity(DATA:list, years:list):
#     """illustrates the sensitivity of hydrogen cost to
#     natural gas prices

#     Args:
#         DATA (list): List with dictionaries with case study data
#         years (list): list of years for subplot1,
#         limited because model doesnot converge for extreme cases
#     """
#     fig, ax = plt.subplots(1,2,figsize = (12,6))
#     # .title('Sensitivity of hydrogen cost to natural gas price', fontsize = 14)

#     iter2_ = 0
#     for year_ in years:
#         if year_ <5:
#             ng_price = [2,4,6,8,10]
#             iter_ = 0
#             line = []
#             for DATA_ in DATA:

#                 Cost = []
#                 SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#                 for scenario_ in SCENARIO:
#                     div_ = sum(DATA_[scenario_][year_]['Net_P']['HO'][k]['P_annual'] for k in ['H2_Sink1', 'H2_Sink2'])
#                     Cost.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/div_)
#                 line.append(Cost[0])
#                 ax[0].scatter(ng_price[iter_], Cost, color = 'teal', marker = '.')
#                 iter_+= 1
#                 # ax.xaxis.set_ticks_position('both')
#                 # ax.yaxis.set_ticks_position('both')
#             ax[0].plot(ng_price, line, color =  (0,0.5+iter2_*0.05,0.5-iter2_*0.05))

#             ax[0].annotate(str(year_ + 2022), (ng_price[-1]+ 0.05, line[-1]+ 0.06), verticalalignment = 'top', horizontalalignment = 'center'\
#                         , fontsize = 10, color =  (0,0.5+iter2_*0.05,0.5-iter2_*0.05))
#             iter2_ += 1
#         else:
#             iter_ = 0
#             line = []
#             ng_price = [4,6,8]
#             for DATA_ in DATA[1:4]:
#                 Cost = []
#                 SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#                 for scenario_ in SCENARIO:
#                     div_ = sum(DATA_[scenario_][year_]['Net_P']['HO'][k]['P_annual'] for k in ['H2_Sink1', 'H2_Sink2'])
#                     Cost.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/div_)
#                 line.append(Cost[0])
#                 ax[0].scatter(ng_price[iter_], Cost, color = 'teal', marker = '.')
#                 iter_+= 1
#                 # ax.xaxis.set_ticks_position('both')
#                 # ax.yaxis.set_ticks_position('both')
#             ax[0].plot(ng_price, line, color =  (0,0.5+iter2_*0.05,0.5-iter2_*0.05))

#             ax[0].annotate(str(year_ + 2022), (ng_price[-1]+ 0.05, line[-1]+ 0.06), verticalalignment = 'top', horizontalalignment = 'center'\
#                         , fontsize = 10, color =  (0,0.5+iter2_*0.05,0.5-iter2_*0.05))
#             iter2_ += 1

#     ng_price = [2,4,6,8,10]
#     iter3_ = 0
#     iter4_ = 0
#     for DATA_ in DATA:
#         # if iter4_ == 0:
#         Cost, X_ = [], []
#         years = np.arange(0,5)
#         for year_ in years:
#             div_ = sum(DATA_[scenario_][year_]['Net_P']['HO'][k]['P_annual'] for k in ['H2_Sink1', 'H2_Sink2'])
#             Cost.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/div_)
#             X_.append(int(year_ + 2022))
#         ax[1].scatter(X_, Cost, color = 'teal', marker = '.')
#         ax[1].plot(X_, Cost, color =  (0,0.5+iter4_*0.1,0.5-iter4_*0.1))
#         ax[1].annotate(ng_price[iter4_], (2022 - 0.14, Cost[0]+ 0.04), verticalalignment = 'top', horizontalalignment = 'center'\
#                     , fontsize = 12, color =  (0,0.5+iter4_*0.1,0.5-iter4_*0.1))
#         # elif iter4_ ==4:
#         #     Cost, X_ = [], []
#         #     years = np.arange(0,5)
#         #     for year_ in years:
#         #         div_ = sum(DATA_[scenario_][year_]['Net_P']['HO'][k]['P_annual'] for k in ['H2_Sink1', 'H2_Sink2'])
#         #         Cost.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/div_)
#         #         X_.append(int(year_ + 2022))
#         #     ax[1].scatter(X_, Cost, color = 'teal', marker = '.')
#         #     ax[1].plot(X_, Cost, color =  (0,0.5+iter4_*0.1,0.5-iter4_*0.1))
#         #     ax[1].annotate(ng_price[iter4_], (2022 - 0.12, Cost[0]+ 0.02), verticalalignment = 'top', horizontalalignment = 'center'\
#         #                 , fontsize = 12, color =  (0,0.5+iter4_*0.1,0.5-iter4_*0.1))

#         # else:
#         #     Cost, X_ = [], []
#         #     years = np.arange(0,10)
#         #     for year_ in years:
#         #         div_ = sum(DATA_[scenario_][year_]['Net_P']['HO'][k]['P_annual'] for k in ['H2_Sink1', 'H2_Sink2'])
#         #         Cost.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/div_)
#         #         X_.append(int(year_ + 2022))
#         #     ax[1].scatter(X_, Cost, color = 'teal', marker = '.')
#         #     ax[1].plot(X_, Cost, color =  (0,0.5+iter4_*0.1,0.5-iter4_*0.1))
#         #     ax[1].annotate(ng_price[iter4_], (2022 - 0.12, Cost[0]+ 0.02), verticalalignment = 'top', horizontalalignment = 'center'\
#         #                 , fontsize = 12, color =  (0,0.5+iter4_*0.1,0.5-iter4_*0.1))
#         iter4_ += 1

#     ax[0].set_xticks(ng_price)
#     ax[1].set_xticks(np.arange(2022,2027))


#     x_line = [4]*16
#     y_line = np.arange(2,3.6,0.1)
#     ax[0].plot(x_line, y_line , '--', alpha = 0.8)
#     ax[0].set_xlabel('Natural gas price [$/MMBtu]', fontsize = 14)
#     ax[0].set_ylabel('LCOH [$\$/kg.H_{2}$]', fontsize = 14)
#     ax[1].set_xlabel('Year', fontsize = 14)
#     ax[1].set_ylabel('LCOH [$\$/kg.H_{2}$]', fontsize = 14)

#     ax[0].set_ylim([2.0,3.5])
#     ax[1].set_ylim([2.0,3.5])
#     plt.suptitle('Sensitivity of LCOH to Natural gas prices', fontsize = 14)
#     plt.savefig('natural_gas.jpeg', dpi = 200)
#     plt.show()

# ng_sensitivity(DATA,years)

# #%%

# def ng_var_fix(DATA_:dict, year_:float):
#     """Compares capacity utilization for varying vs fixed natural gas prices

#     Args:
#         DATA_ (dict): containts output data for each year in the scenario
#         year_ (float): year of choice to plot
#     """
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     for scenario_ in SCENARIO:
#         Green_H2, Blue_H2, X_ = ([] for _ in range(3))
#         for h, d in product(H,D):
#             green_ = DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink2'][h][d]['P']/(907.185)
#             blue_ = DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink1'][h][d]['P']/(907.185)
#             Green_H2.append(green_/(green_ + blue_))

#             Blue_H2.append(blue_/(green_ + blue_))
#         X_ = np.arange(0,len(Green_H2))
#         print(len(X_))
#         print(len(Green_H2))
#         print(len(Blue_H2))

#         width = 0.8
#         space = 0.2
#         fig, ax = plt.subplots(figsize=(10, 10))
#         ax.bar(X_, Blue_H2, color= 'blue', label= 'Blue H2')
#         ax.bar(X_, Green_H2, bottom= Blue_H2, color='green', label='Green H2')
#         plt.title('Total hydrogen production under a ' + scenario_ + ' cost scenario', fontsize=20)
#         plt.xlabel('Year', fontsize=20)
#         plt.ylabel('US tonnes', fontsize=20)
#         plt.legend(fontsize=20)
#         plt.xticks(fontsize= 16)
#         plt.yticks(fontsize= 16)
#         # ax.set_xticks(X_)
#         plt.show()
#     return

# for DATA_ in DATA:
#     ng_var_fix(DATA_, 4)


# #%%

# def h2_pie_grid():
#     """Plot a pie grid with three levels:
#     1. power contribution over the year
#     2. Carbon dioxide contribution
#     3. hydrogen contribution
#     OR
#     3. miles contribution
#     """


#     for DATA_ in DATA:
#         SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#         for scenario_ in SCENARIO:
#             Wind, Solar, Green_H2, Blue_H2, Loc_H2, Geo_H2, SMRH, EOR, \
#                 Miles_MEOH, Miles_H2, Miles_Pow, X_,\
#                     Total_miles, Total_CO2, Total_H2_p, Total_H2_d, Total_Pow,\
#                         temp_Total_miles, temp_Total_CO2, temp_Total_H2, temp_Total_Pow, \
#                             temp_Wind, temp_Solar = ([] for _ in range(23))
#             for year_ in YEAR:

#                 Wind.append(DATA_[scenario_][year_]['Net_P']['HO']['WF']['P_annual'])
#                 Solar.append(DATA_[scenario_][year_]['Net_P']['HO']['PV']['P_annual'])

#                 Green_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual'])
#                 Blue_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual'])

#                 Loc_H2.append(DATA_[scenario_][year_]['Net_S']['HO']['H2_C']['S_annual'])
#                 Geo_H2.append(DATA_[scenario_][year_]['Net_S']['HO']['H2_L']['S_annual'])

#                 SMRH.append(DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']*dict_conversion['SMRH']['CO2_Vent'])
#                 EOR.append(DATA_[scenario_][year_]['Net_P']['HO']['EOR']['P_annual']*dict_conversion['EOR']['CO2_Vent'])

#                 Miles_MEOH.append(DATA_[scenario_][year_]['Net_S']['HO']['CH3OH']['Mile_annual'])
#                 Miles_H2.append(sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L']))
#                 Miles_Pow.append(DATA_[scenario_][year_]['Net_S']['HO']['Power']['Mile_annual'])

#                 Total_CO2.append(DATA_[scenario_][year_]['Net_S']['HO']['CO2_Vent']['S_annual'])
#                 Total_H2_p.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i_]['P_annual'] for i_ in ['H2_Sink1', 'H2_Sink2']))
#                 Total_H2_d.append(sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['S_annual'] for i_ in ['H2_C', 'H2_L']))
#                 Total_miles.append(sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L', 'Power', 'CH3OH']))
#                 Total_Pow.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i_]['P_annual'] for i_ in ['PV', 'WF']))

#                 X_.append(int(year_ + 2022))


#             Y1_ = [1]*len(X_)
#             Y2_ = [2]*len(X_)
#             Y3_ = [3]*len(X_)
#             Y4_ = [4]*len(X_)
#             Y5_ = [5]*len(X_)

#             fig, ax = plt.subplots(figsize = (12, 8))

#             for year_ in YEAR:

#                 r1 = Wind[year_]/Total_Pow[year_]
#                 r2 = r1 + Solar[year_]/Total_Pow[year_]
#                 x1 = np.cos(2 * np.pi * np.linspace(0, r1))
#                 y1 = np.sin(2 * np.pi * np.linspace(0, r1))
#                 xy1 = np.row_stack([[0, 0], np.column_stack([x1, y1])])

#                 x2 = np.cos(2 * np.pi * np.linspace(r1, r2))
#                 y2 = np.sin(2 * np.pi * np.linspace(r1, r2))
#                 xy2 = np.row_stack([[0, 0], np.column_stack([x2, y2])])

#                 plt.scatter(X_[year_], Y1_[year_], s  = 3000*Total_Pow[year_]/max(Total_Pow), marker = xy1, color = 'royalblue')
#                 plt.scatter(X_[year_], Y1_[year_], s = 3000*Total_Pow[year_]/max(Total_Pow), marker = xy2, color = 'gold')

#                 if Total_CO2[year_] ==0:
#                     r3 = 0
#                     r4 = r3 + 0
#                 else:
#                     r3 = SMRH[year_]/Total_CO2[year_]
#                     r4 = r3 + EOR[year_]/Total_CO2[year_]

#                 x3 = np.cos(2 * np.pi * np.linspace(0, r3))
#                 y3 = np.sin(2 * np.pi * np.linspace(0, r3))
#                 xy3 = np.row_stack([[0, 0], np.column_stack([x3, y3])])

#                 x4 = np.cos(2 * np.pi * np.linspace(r3, r4))
#                 y4 = np.sin(2 * np.pi * np.linspace(r3, r4))
#                 xy4 = np.row_stack([[0, 0], np.column_stack([x4, y4])])

#                 plt.scatter(X_[year_], Y2_[year_], s  = 3000*Total_CO2[year_]/max(Total_CO2), marker = xy3, color = 'cadetblue')
#                 plt.scatter(X_[year_], Y2_[year_], s = 3000*Total_CO2[year_]/max(Total_CO2), marker = xy4, color = 'slategrey')

#                 r5 = Blue_H2[year_]/Total_H2_p[year_]
#                 r6 = r5 + Green_H2[year_]/Total_H2_p[year_]
#                 x5 = np.cos(2 * np.pi * np.linspace(0, r5))
#                 y5 = np.sin(2 * np.pi * np.linspace(0, r5))
#                 xy5 = np.row_stack([[0, 0], np.column_stack([x5, y5])])

#                 x6 = np.cos(2 * np.pi * np.linspace(r5, r6))
#                 y6 = np.sin(2 * np.pi * np.linspace(r5, r6))
#                 xy6 = np.row_stack([[0, 0], np.column_stack([x6, y6])])

#                 plt.scatter(X_[year_], Y3_[year_], s  = 3000*Total_H2_p[year_]/max(Total_H2_p), marker = xy5, color = 'blue')
#                 plt.scatter(X_[year_], Y3_[year_], s = 3000*Total_H2_p[year_]/max(Total_H2_p), marker = xy6, color = 'green')

#                 r7 = Loc_H2[year_]/Total_H2_d[year_]
#                 r8 = r7 + Geo_H2[year_]/Total_H2_d[year_]
#                 x7 = np.cos(2 * np.pi * np.linspace(0, r7))
#                 y7 = np.sin(2 * np.pi * np.linspace(0, r7))
#                 xy7 = np.row_stack([[0, 0], np.column_stack([x7, y7])])

#                 x8 = np.cos(2 * np.pi * np.linspace(r7, r8))
#                 y8 = np.sin(2 * np.pi * np.linspace(r7, r8))
#                 xy8 = np.row_stack([[0, 0], np.column_stack([x8, y8])])

#                 plt.scatter(X_[year_], Y4_[year_], s  = 3000*Total_H2_d[year_]/max(Total_H2_d), marker = xy7, color = 'yellow')
#                 plt.scatter(X_[year_], Y4_[year_], s = 3000*Total_H2_d[year_]/max(Total_H2_d), marker = xy8, color = 'orange')


#                 # r9 = Miles_MEOH[year_]/Total_miles[year_]
#                 # r10 = r9 + Miles_H2[year_]/Total_miles[year_]
#                 # r11 = r9 + r10 + Miles_Pow[year_]/Total_miles[year_]

#                 # x9 = np.cos(2 * np.pi * np.linspace(0, r9))
#                 # y9 = np.sin(2 * np.pi * np.linspace(0, r9))
#                 # xy9 = np.row_stack([[0, 0], np.column_stack([x9, y9])])

#                 # x10 = np.cos(2 * np.pi * np.linspace(r9, r10))
#                 # y10 = np.sin(2 * np.pi * np.linspace(r9, r10))
#                 # xy10 = np.row_stack([[0, 0], np.column_stack([x10, y10])])

#                 # x11 = np.cos(2 * np.pi * np.linspace(r10, r11))
#                 # y11 = np.sin(2 * np.pi * np.linspace(r10, r11))
#                 # xy11 = np.row_stack([[0, 0], np.column_stack([x11, y11])])

#                 # plt.scatter(X_[year_], Y5_[year_], s  = 3000*Total_miles[year_]/max(Total_miles), marker = xy9, color = 'firebrick')
#                 # plt.scatter(X_[year_], Y5_[year_], s = 3000*Total_miles[year_]/max(Total_miles), marker = xy10, color = 'mediumseagreen')
#                 # plt.scatter(X_[year_], Y5_[year_], s = 3000*Total_miles[year_]/max(Total_miles), marker = xy11, color = 'mediumturquoise')

#             # colors = ['royalblue', 'gold', 'cadetblue', 'slategrey', 'blue', 'green', 'yellow', 'orange', 'firebrick', 'olive', 'mediumturquoise']

#             # labels = ['Wind', 'Solar', 'SMR+CC', 'EOR',  'Blue $H_{2}$', 'Green $H_{2}$', 'Local', 'Geological',  'Methanol(90%)', 'HFCV', 'EV']

#             colors = ['yellow', 'orange', 'blue', 'green', 'cadetblue', 'slategrey',  'royalblue', 'gold' ]

#             labels = ['Local', 'Geological', 'Blue $H_{2}$', 'Green $H_{2}$',   'SMR+CC', 'EOR', 'Wind', 'Solar',   ]


#             patches = []
#             for i in range(len(colors)):
#                 patches.append(mpatches.Patch(color=colors[i], label=labels[i]))

#             plt.legend(handles= patches, bbox_to_anchor=(1.03, 1))
#                 # lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--') for c in colors]
#                 # plt.legend(lines, labels)

#             # plt.scatter(X_, Y1_, s = Total_CO2, marker = xy2)

#             #plt.scatter(X_, Y3_, s = Total_H2)#, marker = xy3)

#             #plt.scatter(X_, Y4_, s= Total_H2)#, marker = xy4)
#             plt.grid(alpha = 0.4)
#             plt.xticks(X_, fontsize = 14)
#             bars = ('Power', '$CO_{2}$ emission', '$H_{2}$ production', '$H_{2}$ dispense')
#             y_pos = [1, 2, 3, 4, 5, 0]
#             plt.yticks(y_pos, bars,  fontsize='14', horizontalalignment='right')
#             plt.xlabel('Year', fontsize = 14)
#             plt.title('Trajectories for ' + scenario_.lower() +' cost scenario', fontsize = 14)
#             x_line = [2027]*61
#             y_line = np.arange(0,6.1,0.1)
#             plt.plot(x_line, y_line , '--', alpha = 0.4, color = 'slateblue')
#             plt.ylim([0.5,4.5])

#             plt.annotate('End of term 1', (2027, 4.45), verticalalignment = 'top', horizontalalignment = 'center'\
#                     , fontsize = 14, color = 'slateblue')

#             plt.show()
#     return
# plot_ = h2_pie_grid()
# #%%
# # YEAR = np.arange(0,10)
# def h_cost_contr(DATA_:dict):
#     """Provides a breakdown of the cost contribution
#     in $/kg.H2

#     Args:
#         DATA_ (dict): contains results
#     """
#     I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'AKE', 'SMRH', 'H2_C_c', 'H2_L_c', 'DAC', 'MEFC', 'EOR', 'AQoff_SMR']# 'AQoff_DAC',
#     I2 = [ 'H2_C_c', 'H2_L_c', 'DAC', 'MEFC', 'EOR', 'AQoff_SMR']

#     df = pd.DataFrame(columns = I)
#     df2 = pd.DataFrame(columns = ['Power System', 'Electrolysis', 'SMR + CC', 'Rest'])

#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     for scenario_ in SCENARIO:
#         for year_ in YEAR:
#             div_ = sum(DATA_[scenario_][year_]['Net_P']['HO'][k]['P_annual'] for k in ['H2_Sink1', 'H2_Sink2'])
#             list_ = []
#             for i in I:
#                 list_.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i][j] for j in ['Capex', 'Opex_fix', 'Opex_var'])/div_)
#             # print(list_)

#             df.loc[year_] = list_
#         # view data
#         df['Year'] = df.index
#         df['AQoff'] = df['AQoff_SMR'] #+ df['AQoff_DAC']
#         df['Rest'] = sum(df[i] for i in I2)
#         df2['Power System'] = sum(df[i] for i in ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c'])
#         # df2['Power System'] = df2['Power System']/max(df2['Power System'])
#         df2['Electrolysis'] = df['AKE']#/max(df['AKE'])
#         df2['SMR + CC'] = df['SMRH']#/max(df['SMRH'])
#         df2['Rest'] = df['Rest']

#         list2_, list3_, list4_, list5_ = ([] for _ in range(4))
#         for year_ in YEAR:
#             div_ = sum(DATA_[scenario_][year_]['Net_P']['HO'][k]['P_annual'] for k in ['H2_Sink1', 'H2_Sink2'])
#             list2_.append(-1*DATA_[scenario_][year_]['Net_P']['HO']['EOR']['Credit']/div_)
#             list3_.append(-1*sum(DATA_[scenario_][year_]['Net_P']['HO'][i]['Credit'] for i in ['AQoff_SMR'] )/div_)#'AQoff_DAC',
#             list4_.append(-1*DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['Credit']/div_)
#             list5_.append(DATA_[scenario_][year_]['Net_S']['HO']['CH4']['B_annual']/div_)

#         df2['45Q-EOR'] = list2_
#         df2['45Q-Aquifer'] = list3_
#         df2['45Q-Methanol'] = list4_
#         df2['NG Purchase'] = list5_

#         cols = ['Power System', 'Electrolysis', 'SMR + CC', 'Rest', '45Q-EOR', '45Q-Aquifer', '45Q-Methanol']
#         # df2[cols] = df2[cols].div(df2[cols].sum(axis=1), axis=0).multiply(100)
#         df2['Year'] = df2.index + 2022
#     # plot data in stack manner of bar type
#         width = 0.8
#         space = 0.9
#         fig, ax = plt.subplots(figsize=(10, 5))
#         bar1 = ax.bar(df2['Year'], df2['Power System'], width, color= 'darkorange', label= 'Power System')
#         bar2 = ax.bar(df2['Year'], df2['Electrolysis'], width, bottom= df2['Power System'], color='forestgreen', label='Electrolysis')
#         bar3 = ax.bar(df2['Year'], df2['SMR + CC'], width, bottom= df2['Power System'] + df2['Electrolysis'], color='cadetblue', label='SMR + CC')
#         bar4 = ax.bar(df2['Year'], df2['Rest'], width, bottom= df2['Power System'] + df2['Electrolysis'] + df2['SMR + CC'], color='indianred', label='H2 Storage ')

#         bar5 = ax.bar(df2['Year'], df2['NG Purchase'], width, bottom= df2['Power System'] + df2['Electrolysis'] + df2['SMR + CC'] \
#             + df2['Rest'], color='slategrey', label='NG Purchase')

#         bar6 = ax.bar(df2['Year'], df2['45Q-EOR'], width, bottom = df2['45Q-Aquifer']+ df2['45Q-Methanol'], color = 'slateblue',  label = '45Q-EOR')
#         bar7 = ax.bar(df2['Year'], df2['45Q-Aquifer'],   width, bottom = df2['45Q-Methanol'], color = 'saddlebrown', label = '45Q-Aquifer')
#         bar8 = ax.bar(df2['Year'], df2['45Q-Methanol'], width, color = 'teal', label = '45Q-Methanol')

#         bar5 = ax.bar(df2['Year'], df2['45Q-EOR'], width)

#         plt.title('Contribution to total hydrogen cost [\$/kg.$H_{2}$] \n under a ' + scenario_.lower() + ' cost scenario', fontsize=16, color = 'midnightblue', y = 1)
#         # plt.subtitle(, fontsize=14, y = 0.98)
#         plt.xlabel('Year', fontsize=14)
#         plt.ylabel('$', fontsize=14)
#         plt.legend(fontsize=14)
#         plt.xticks(fontsize= 14)
#         plt.yticks(fontsize= 14)
#         ax.set_xticks(df2['Year'])

#         ax.xaxis.set_ticks_position('both')
#         ax.yaxis.set_ticks_position('both')

#         # x_ = list(range(2022,2032))
#         x_ = [i + 2022 for i in YEAR]
#         y_ = [3.2]*len(x_)
#         ax.scatter(x_, y_, alpha =0.0001, color = 'black', marker = '*')

#         ax.yaxis.set_minor_locator(AutoMinorLocator())
#         annot, Y_ = [], []
#         for year_ in YEAR:

#             value = DATA_[scenario_][year_]['Total']['HO']['Objective']/(DATA_[scenario_][year_]['Net_S']['HO']['H2_C']['S_annual']\
#                 + DATA_[scenario_][year_]['Net_S']['HO']['H2_L']['S_annual'])

#             annot.append(str(round(value,2)))
#             Y_.append(value)

#         for i, txt in enumerate(annot):
#             ax.annotate(txt, (x_[i], y_[i]), verticalalignment = 'top', horizontalalignment = 'center'\
#                 , fontsize = 14, color = 'midnightblue')


#         ax.scatter(x_, Y_,  s=20, facecolors='r', edgecolors='r', zorder = 2)
#         ax.plot(x_, Y_, color = 'r', zorder = 2)
#         lgd = plt.legend( bbox_to_anchor=(1.005, 1), fontsize = 13)
#         plt.ylim([-0.75,3.5])
#         plt.grid(alpha = 0.25)
#         plt.savefig('h2_contr_' + scenario_.lower() + '.jpeg')
#         plt.show()

#     return

# for DATA_ in DATA:
#     plot_ = h_cost_contr(DATA_)

# # df2.plot(x='Year', kind='bar', stacked=True,
#     # title='Stacked Bar Graph by dataframe', colors = colors_).legend(loc='lower left')

# #%%

# def mile_cost_contr(DATA_:dict):
#     """Provides a breakdown of the cost contribution
#     in $/mile

#     Args:
#         DATA_ (dict): contains results
#     """
#     I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'AKE', 'SMRH',  'EOR',  'H2_C_c', 'H2_L_c', 'DAC', 'MEFC','AQoff_SMR'] #'AQoff_DAC',
#     I2 = [ 'DAC', 'MEFC', 'EOR','AQoff_SMR', 'H2_C_c', 'H2_L_c'] # 'AQoff_DAC',

#     df = pd.DataFrame(columns = I)
#     df2 = pd.DataFrame(columns = ['Power System', 'Electrolysis', 'SMR + CC', 'Rest'])


#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     for scenario_ in SCENARIO:
#         for year_ in YEAR:

#             div_ = sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L', 'CH3OH', 'Power'])

#             list_ = []
#             for i in I:
#                 list_.append(sum(DATA_[scenario_][year_]['Net_P']['HO'][i][j] for j in ['Capex', 'Opex_fix', 'Opex_var'])/div_)
#             # print(list_)

#             df.loc[year_] = list_
#         # view data
#         df['Year'] = df.index
#         df['AQoff'] = df['AQoff_SMR']  #+ df['AQoff_DAC']
#         df['Rest'] = sum(df[i] for i in I2)
#         df2['Power System'] = sum(df[i] for i in ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c'])
#         # df2['Power System'] = df2['Power System']/max(df2['Power System'])
#         df2['Electrolysis'] = df['AKE']#/max(df['AKE'])
#         df2['SMR + CC'] = df['SMRH']#/max(df['SMRH'])
#         df2['Rest'] = df['Rest']

#         list2_, list3_, list4_, list5_ = ([] for _ in range(4))
#         for year_ in YEAR:
#             div_ = sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L', 'CH3OH', 'Power'])
#             list2_.append(-1*DATA_[scenario_][year_]['Net_P']['HO']['EOR']['Credit']/div_)
#             list3_.append(-1*sum(DATA_[scenario_][year_]['Net_P']['HO'][i]['Credit'] for i in [ 'AQoff_SMR'] )/div_) #'AQoff_DAC',
#             list4_.append(-1*DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['Credit']/div_)
#             list5_.append(DATA_[scenario_][year_]['Net_S']['HO']['CH4']['B_annual']/div_)

#         df2['45Q-EOR'] = list2_
#         df2['45Q-Aquifer'] = list3_
#         df2['45Q-Methanol'] = list4_
#         df2['NG Purchase'] = list5_

#         cols = ['Power System', 'Electrolysis', 'SMR + CC', 'Rest', '45Q-EOR', '45Q-Aquifer', '45Q-Methanol']
#         # df2[cols] = df2[cols].div(df2[cols].sum(axis=1), axis=0).multiply(100)
#         df2['Year'] = df2.index + 2022
#     # plot data in stack manner of bar type
#         width = 0.8
#         space = 0.9
#         fig, ax = plt.subplots(figsize=(10, 5))
#         bar1 = ax.bar(df2['Year'], df2['Power System'], width, color= 'darkorange', label= 'Power System')
#         bar2 = ax.bar(df2['Year'], df2['Electrolysis'], width, bottom= df2['Power System'], color='forestgreen', label='Electrolysis')
#         bar3 = ax.bar(df2['Year'], df2['SMR + CC'], width, bottom= df2['Power System'] + df2['Electrolysis'], color='cadetblue', label='SMR + CC')
#         bar4 = ax.bar(df2['Year'], df2['Rest'], width, bottom= df2['Power System'] + df2['Electrolysis'] + df2['SMR + CC'], color='indianred', label='H2 Storage ')

#         bar5 = ax.bar(df2['Year'], df2['NG Purchase'], width, bottom= df2['Power System'] + df2['Electrolysis'] + df2['SMR + CC'] \
#             + df2['Rest'], color='slategrey', label='NG Purchase')

#         bar6 = ax.bar(df2['Year'], df2['45Q-EOR'], width, bottom = df2['45Q-Aquifer']+ df2['45Q-Methanol'], color = 'slateblue',  label = '45Q-EOR')
#         bar7 = ax.bar(df2['Year'], df2['45Q-Aquifer'],   width, bottom = df2['45Q-Methanol'], color = 'saddlebrown', label = '45Q-Aquifer')
#         bar8 = ax.bar(df2['Year'], df2['45Q-Methanol'], width, color = 'teal', label = '45Q-Methanol')

#         # bar5 = ax.bar(df2['Year'], df2['45Q-EOR'], width)

#         plt.title('Contribution to total mile cost [\$/mile] \n under a ' + scenario_.lower() + ' cost scenario', fontsize=16, color = 'midnightblue', y = 1)
#         # plt.subtitle(, fontsize=14, y = 0.98)
#         plt.xlabel('Year', fontsize=14)
#         plt.ylabel('$', fontsize=14)
#         plt.legend(fontsize=14)
#         plt.xticks(fontsize= 14)
#         plt.yticks(fontsize= 14)
#         ax.set_xticks(df2['Year'])

#         ax.xaxis.set_ticks_position('both')
#         ax.yaxis.set_ticks_position('both')

#         x_ = list(range(2022,2032))
#         y_ = [0.65]*10
#         ax.scatter(x_, y_, alpha =0.0001, color = 'black', marker = '*')
#         ax.yaxis.set_minor_locator(AutoMinorLocator())
#         annot = []
#         for year_ in YEAR:
#             div_ = sum(DATA_[scenario_][year_]['Net_S']['HO'][i_]['Mile_annual'] for i_ in ['H2_C', 'H2_L', 'CH3OH', 'Power'])
#             value = DATA_[scenario_][year_]['Total']['HO']['Objective']/div_

#             annot.append(str(round(value,2)))

#         for i, txt in enumerate(annot):
#             ax.annotate(txt, (x_[i], y_[i]), verticalalignment = 'top', horizontalalignment = 'center'\
#                 , fontsize = 14, color = 'midnightblue')
#         plt.legend( bbox_to_anchor=(1.005, 1), fontsize = 13)
#         # plt.ylim([-0.75,3.5])
#         plt.grid(alpha = 0.25)
#         plt.show()

#     return

# for DATA_ in DATA:
#     plot_ = mile_cost_contr(DATA_)


# #%%MATERIAL FLOW SANKEY

# for DATA_ in DATA:
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]

#     year_ = 0

#     for scenario_ in SCENARIO:
#         fig = go.Figure(data=[go.Sankey(
#             node = dict(
#             pad = 15,
#             thickness = 20,
#             line = dict(color = "black", width = 0.5),
#             label = ["Water", "Carbon dioxide (captured)", "Natural gas",\
#                 "Hydrogen (Green)", "Hydrogen (Blue)",\
#                 "Carbon dioxide (sequestered)", "Carbon dioxide (vented)",\
#                     "Methanol", 'Enhanced Oil Recovery', 'Crude oil'],
#             color = ['turquoise', 'darksalmon', 'darkslategrey', 'forestgreen', \
#                 'cadetblue', 'sandybrown', 'darkred', 'seagreen', 'darkorange', 'dimgray']
#             ),
#             link = dict(
#             source = [0, 1, 2, 2, 2, 3, 2, 8, 8, 0], # indices correspond to labels, eg A1, A2, A1, B1, ...
#             target = [3, 7, 4, 5, 6, 7, 8, 9, 6, 4],
#             color = ['mediumaquamarine', 'salmon', 'powderblue', 'peachpuff', 'red',\
#                 'mediumseagreen', 'orange', 'lightgray', 'red', 'powderblue'],
#             value =  [DATA_[scenario_][year_]['Net_P']['HO']['AKE']['P_annual']*dict_conversion['AKE']['H2_G'],\
#                 DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual']*dict_conversion['MEFC']['CH3OH'],\
#                     DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']*dict_conversion['SMRH']['H2_B'],\
#                         DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']*dict_conversion['SMRH']['CO2'],\
#                             DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']*dict_conversion['SMRH']['CO2_Vent'],\
#                                 DATA_[scenario_][year_]['Net_P']['HO']['DAC']['P_annual']*dict_conversion['DAC']['CO2_DAC']*-1,\
#                                     DATA_[scenario_][year_]['Net_P']['HO']['EOR']['P_annual']*dict_conversion['EOR']['CO2']*-1,\
#                                         DATA_[scenario_][year_]['Net_P']['HO']['EOR']['P_annual']*dict_conversion['EOR']['CO2_EOR']*136,\
#                                             DATA_[scenario_][year_]['Net_P']['HO']['EOR']['P_annual']*dict_conversion['EOR']['CO2_Vent'],\
#                                                 DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']*dict_conversion['SMRH']['H2O']*-1]
#             # value = [10]*9
#         ))])
#         # fig.update_layout(title_text='Material flow for ' + str(2022+ year_) + ' under a ' + scenario_.lower() + ' cost scenario', font_size=14)
#         # fig.savefig(, dpi = 300)
#         pio.write_image(fig, 'MF_' + str(2022+year_) + '_' + scenario_.lower() + '.png',  scale=1)

#         fig.show()

# #%%ENERGY FLOWS

# for DATA_ in DATA:
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     year_ = 4

#     for scenario_ in SCENARIO:
#         I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'AKE', 'SMRH', 'DAC', 'MEFC', 'EOR', 'AQoff', 'Power_dummy']
#         fig = go.Figure(data=[go.Sankey(
#             node = dict(
#             pad = 10,
#             thickness = 20,
#             line = dict(color = "black", width = 0.5),
#             label = [I_labels_['short'][i] for i in I ],
#             color = ['darkorange', 'cornflowerblue', 'yellow', 'royalblue', \
#                 'darkgoldenrod', 'forestgreen', 'cadetblue', 'indigo', 'teal', 'slategrey', 'saddlebrown', 'cadetblue']
#             ),
#             link = dict(
#             source = [0, 1, 11, 2, 11, 3, 11, 4, 11, 11, 11, 11, 11, 11], # indices correspond to labels, eg A1, A2, A1, B1, ...
#             target = [11, 11, 2, 11, 3, 11, 4, 11, 5, 6, 7, 8, 9, 10],
#             # color = ['mediumaquamarine', 'lightsteelblue', 'powderblue', 'peachpuff', 'red',\
#             #     'mediumseagreen', 'orange', 'lightgray', 'red', 'powderblue'],
#             color = ['orange', 'lightblue', 'khaki', 'aquamarine', 'cornflowerblue', 'aquamarine', 'coral', 'aquamarine', \
#                 'lightsteelblue', 'lightsteelblue', 'lightsteelblue', 'lightsteelblue', 'lightsteelblue', 'lightsteelblue' ],
#             value =  [
#                 DATA_[scenario_][year_]['Net_P']['HO']['PV']['P_annual']*dict_conversion['PV']['Power'],
#                 DATA_[scenario_][year_]['Net_P']['HO']['WF']['P_annual']*dict_conversion['WF']['Power'],
#                 DATA_[scenario_][year_]['Net_P']['HO']['LiI_c']['P_annual']*dict_conversion['LiI_c']['Charge'],
#                 DATA_[scenario_][year_]['Net_P']['HO']['LiI_d']['P_annual']*dict_conversion['LiI_d']['Power'],
#                 DATA_[scenario_][year_]['Net_P']['HO']['PSH_c']['P_annual']*dict_conversion['PSH_c']['H2O_E'],
#                 DATA_[scenario_][year_]['Net_P']['HO']['PSH_d']['P_annual']*dict_conversion['PSH_d']['Power'],
#                 DATA_[scenario_][year_]['Net_P']['HO']['CAES_c']['P_annual']*dict_conversion['CAES_c']['Air_C'],
#                 DATA_[scenario_][year_]['Net_P']['HO']['CAES_d']['P_annual']*dict_conversion['CAES_d']['Power'],
#                 DATA_[scenario_][year_]['Net_P']['HO']['AKE']['P_annual']*dict_conversion['AKE']['Power']*-1,
#                 DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']*dict_conversion['SMRH']['Power']*-1,
#                 DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual']*dict_conversion['MEFC']['Power']*-1,
#                 DATA_[scenario_][year_]['Net_P']['HO']['DAC']['P_annual']*dict_conversion['DAC']['Power']*-1,
#                 DATA_[scenario_][year_]['Net_P']['HO']['EOR']['P_annual']*dict_conversion['EOR']['Power']*-1,
#                 # DATA_[scenario_][year_]['Net_P']['HO']['AQoff_DAC']['P_annual']*dict_conversion['AQoff_DAC']['Power']*-1 + \
#                 DATA_[scenario_][year_]['Net_P']['HO']['AQoff_SMR']['P_annual']*dict_conversion['AQoff_SMR']['Power']*-1
#                 ]
#             # value = [10]*9
#         ))])
#         fig.update_layout(title_text='Energy flow', font_size=14)
#         fig.show()

# #%%

# I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'AKE', 'SMRH', 'DAC', 'MEFC', 'EOR', 'AQoff_DAC', 'AQoff_SMR']

# label = [I_labels_['short'][i] for i in I ]


# #%%

# def annual_bg(DATA_):
#     """Plots annual blue and green hydrogen contribution to the overall demand over the entire planning horizon

#     Args:
#         DATA_ (list): list containing dictionaiers with data
#     """
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     for scenario_ in SCENARIO:
#         Green_H2, Blue_H2, X_ = ([] for _ in range(3))
#         for year_ in YEAR:
#             # Green_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['AKE']['P_annual']*37.50/(365*907.185))
#             Green_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual']/(907.185))

#             # print(Green_H2)
#             # Blue_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']/(365*907.185))
#             Blue_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual']/(907.185))

#             # print(Blue_H2)
#             X_.append(int(year_ + 2022))

#         print(Green_H2)
#         print(Blue_H2)

#         width = 0.8
#         space = 0.2
#         fig, ax = plt.subplots(figsize=(8.27/3, 11.69/3))
#         ax.bar(X_, Blue_H2, width, color= 'lightsteelblue', label= 'Blue H2')
#         ax.bar(X_, Green_H2, width, bottom= Blue_H2, color='mediumseagreen', label='Green H2')
#         plt.title('Total hydrogen production under a ' + scenario_ + ' cost scenario', fontsize=20)
#         plt.xlabel('Year', fontsize=20)
#         plt.ylabel('US tonnes', fontsize=20)
#         plt.legend(fontsize=20)
#         plt.xticks(fontsize= 16)
#         plt.yticks(fontsize= 16)
#         ax.set_xticks(X_)
#         plt.show()
#     return

# for DATA_ in DATA:
#     annual_bg(DATA_)


# #%%
# def h2_cost(DATA:list):
#     """Compares the cost of hydrogen production under

#     Args:
#         DATA (list): list containing dictionaiers with data
#     """
#     iter_ = 0
#     fig, ax = plt.subplots(figsize=(20, 6))
#     color = ['lightcoral', 'palegoldenrod', 'yellowgreen', 'lightcoral', 'palegoldenrod', 'yellowgreen']
#     width = 0.3
#     space = 0.2
#     for DATA_ in DATA:
#         SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#         scenario_ = SCENARIO[0]
#         Y_, X_ = [], []

#         for year_ in YEAR:
#             Y_.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/(DATA_[scenario_][year_]['Net_S']['HO']['H2_C']['S_annual']\
#                 + DATA_[scenario_][year_]['Net_S']['HO']['H2_L']['S_annual']))
#             # Green_H2.append(RESULTS[scenario_][year_]['Total']['HO']['Objective']/(RESULTS[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']))
#             X_.append(year_ + 2022)# + iter_*width)

#         # ax.(X_, Y_, width, color = color[iter_], label = scenario_, align='edge')
#         ax.plot(X_, Y_, color = color[iter_], label = scenario_)
#         ax.scatter(X_, Y_, color = color[iter_])

#         iter_+= 1
#     plt.title('Cost of hydrogen production under different cost scenarios', fontsize=20)
#     plt.xlabel('Year', fontsize=20)
#     plt.ylabel('$/kg.H2', fontsize=20)
#     plt.legend(fontsize=20)
#     plt.xticks(fontsize= 16)
#     plt.yticks(fontsize= 16)
#     plt.grid(axis = 'y', color = '0.85')
#     ax.set_xticks(X_)# - (iter_-1)*width for x in X_])
#     # ax.set_yticks(np.arange(0,7))# - (iter_-1)*width for x in X_])
#     plt.show()
#     return


# h2_cost(DATA)

# #%%

# def mile_cost(DATA:list):
#     """Compares the cost of hydrogen production under

#     Args:
#         DATA (list): list containing dictionaiers with data
#     """
#     iter_ = 0
#     fig, ax = plt.subplots(figsize=(20, 6))
#     color = ['lightcoral', 'palegoldenrod', 'yellowgreen', 'lightcoral', 'palegoldenrod', 'yellowgreen']
#     width = 0.3
#     space = 0.2
#     for DATA_ in DATA:
#         SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#         scenario_ = SCENARIO[0]
#         Y_, X_ = [], []

#         for year_ in YEAR:
#             Y_.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/sum(DATA_[scenario_][year_]['Net_S']['HO'][j]['Mile_annual'] for j in ['Power', 'H2_C', 'H2_L', 'CH3OH']))
#             # Green_H2.append(RESULTS[scenario_][year_]['Total']['HO']['Objective']/(RESULTS[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']))
#             X_.append(year_ + 2022)# + iter_*width)

#         # ax.(X_, Y_, width, color = color[iter_], label = scenario_, align='edge')
#         ax.plot(X_, Y_, color = color[iter_], label = scenario_)
#         ax.scatter(X_, Y_, color = color[iter_])

#         iter_+= 1
#     plt.title('Cost per mile under different cost scenarios', fontsize=20)
#     plt.xlabel('Year', fontsize=20)
#     plt.ylabel('$/kg.H2', fontsize=20)
#     plt.legend(fontsize=20)
#     plt.xticks(fontsize= 16)
#     plt.yticks(fontsize= 16)
#     plt.grid(axis = 'y', color = '0.85')
#     ax.set_xticks(X_)# - (iter_-1)*width for x in X_])
#     # ax.set_yticks(np.arange(0,7))# - (iter_-1)*width for x in X_])
#     plt.show()
#     return

# mile_cost(DATA)
# #%%
# # J = ['H2O_E']
# # J = ['Air_C', 'Charge', 'H2O_E', 'CO2_AQoff', 'CO2_DAC']
# # J = ['CO2_EOR']
# # J = ['PV']
# # J = ['LiI_c', 'LiI_d', 'CAES_c', 'CAES_d', 'PSH_c', 'PSH_d', 'PV', 'WF', 'AKE',\
#     # 'SMRH', 'H2_C_c', 'H2_C_d', 'H2_L_c', 'H2_L_d',  'MEFC', 'DAC', 'EOR', 'AQoff_SMR','AQoff_DAC', 'H2_Sink1', 'H2_Sink2']

# # J = ['Charge', 'Air_C', 'H2O_E', 'Solar', 'Wind', 'Power', 'H2_C', 'H2_L', 'H2', \
# #     'H2_B', 'H2_G', 'H2O', 'O2', 'CH4', 'CO2', 'CO2_DAC', 'CO2_AQoff', \
# #         'CO2_EOR', 'CH3OH']

# J = ['Charge', 'Air_C', 'H2O_E', 'CO2_AQoff', 'CO2_EOR']


# def inventory(DATA_:list):
#     """Plots inventory levels of all storage facilities

#     Args:
#         DATA_ (list): list containing dictionaiers with data
#         year_ (int): year being plotted
#     """
#     Inv = []
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     scenario_ = SCENARIO[0]
#     for y, d, h in product(YEAR, D, H):
#         Inv.append(DATA_[scenario_][y]['Sch_S']['HO'][j][h][d]['Inv'])
#         # Inv.append(DATA_[scenario_][year_]['Sch_P']['HO'][j][h][d]['P'])
#         # Inv.append(DATA_[scenario_][year_]['Sch_S']['HO'][j][h][d]['S'])
#     pos_list = [8760*y for y in YEAR] # hours of the year corresponding to month]
#     name_list = [y + 2022 for y in YEAR]

#     fig, ax = plt.subplots(figsize = (12,6))
#     X_ = np.arange(1,87601)
#     ax.plot(X_, Inv, color = 'dodgerblue', label = 'Blue pathway')
#     ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
#     ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
#     ax.tick_params(axis='x', labelsize =13)
#     plt.grid(alpha  = 0.40)
#     plt.title(str(j))
#     plt.show()

#     return
# for DATA_ in DATA:
#     for j in J:
#         plot = inventory(DATA_)


#    pos_list = [8760*y for y in YEAR] # hours of the year corresponding to month]
#     name_list = [y + 2022 for y in YEAR]
#         ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
#     ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
# #%%
# def h2_prod_inv(DATA_:list, year_:int):
#     """Plots green and blue hydrogen production for a chosen year alongside hydrogen local and geological storage

#     Args:
#         DATA_ (list): list containing dictionaiers with data
#         year_ (int): year being plotted
#     """
#     Green, Blue, Local, Geo, H2, Solar, Wind, Pow_stor, Pow_rel = ([] for _ in range(9))
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     scenario_ = SCENARIO[0]
#     for d, h in product(D, H):
#         Local.append(DATA_[scenario_][year_]['Sch_S']['HO']['H2_C'][h][d]['Inv']/907.185)
#         Geo.append(DATA_[scenario_][year_]['Sch_S']['HO']['H2_L'][h][d]['Inv']/907.185)
#         H2.append((DATA_[scenario_][year_]['Sch_S']['HO']['H2_C'][h][d]['S'] \
#             + DATA_[scenario_][year_]['Sch_S']['HO']['H2_L'][h][d]['S'])/907.185)

#         Green.append(DATA_[scenario_][year_]['Sch_P']['HO']['AKE'][h][d]['P']*dict_conversion['AKE']['H2_G']/907.185)
#         Blue.append(DATA_[scenario_][year_]['Sch_P']['HO']['SMRH'][h][d]['P']/907.185)
#         # value = DATA_[scenario_][year_]['Sch_P']['HO']['AKE'][h][d]['P']*dict_conversion['AKE']['H2_G'] +  DATA_[scenario_][year_]['Sch_P']['HO']['SMRH'][h][d]['P']
#         Solar.append(DATA_[scenario_][year_]['Sch_P']['HO']['PV'][h][d]['P'])
#         Wind.append(DATA_[scenario_][year_]['Sch_P']['HO']['WF'][h][d]['P'])
#         Pow_stor.append(-1*sum(DATA_[scenario_][year_]['Sch_P']['HO'][i][h][d]['P'] for i in ['LiI_c', 'CAES_c', 'PSH_c']))
#         Pow_rel.append(sum(DATA_[scenario_][year_]['Sch_P']['HO'][i][h][d]['P'] for i in ['LiI_d', 'CAES_d', 'PSH_d']))

#     fig, (ax1, ax3) = plt.subplots(2, 1 , figsize = (24,12))
#     X_ = np.arange(1,8761)
#     ax1.bar(X_, Blue, color = 'dodgerblue', label = 'Blue pathway')
#     ax1.bar(X_, Green, bottom = Blue, color = 'seagreen', label = 'Green pathway')
#     ax1.set_ylabel('Production [US tons/hour]', fontsize= 14)
#     ax1.tick_params(axis='y', colors='red', labelsize =14)

#     ax1.yaxis.label.set_color('red')
#     leg1 = ax1.legend(bbox_to_anchor=(1.18, 1), fontsize= 12)

#     pos_list = [0, 744, 1344, 2160, 2800, 3624, 4344, 5088, 5832, 6552, 7296, 8016] # hours of the year corresponding to month
#     name_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

#     ax1.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
#     ax1.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
#     ax1.tick_params(axis='x', labelsize =13)

#     ax2 = ax1.twinx()
#     ax2.plot(X_, Local, color = 'yellow', label = 'Local storage')
#     ax2.plot(X_, Geo, color = 'darkorange', label = 'Geological storage')
#     ax2.set_ylabel('Inventory levels [US tons]', fontsize= 14)
#     ax2.spines['right'].set_color('blue')
#     ax2.spines['left'].set_color('red')

#     ax2.tick_params(axis='y', colors='blue', labelsize =14)
#     ax2.yaxis.label.set_color('blue')
#     # ax2.set_ylim([0, 20000])
#     leg2 = ax2.legend(bbox_to_anchor=(1.18, 0.8), fontsize= 12)

#     leg1.get_frame().set_edgecolor('r')
#     leg2.get_frame().set_edgecolor('b')

#     ax1.set_title('Production and inventory levels for year ' + str(year_ + 2022) + \
#         ' under a(n) ' + scenario_.lower() + ' cost scenario', fontsize= 14)

#     ax3.bar(X_, Solar, color = 'darkorange', label = 'Solar')
#     ax3.bar(X_, Wind, bottom = Solar, color = 'darkgreen', label = 'Wind')
#     ax3.bar(X_, Pow_rel, bottom = [sum(x) for x in zip(Wind, Solar)], color = 'cornflowerblue', label = 'Power discharged')
#     # print(len(Solar), len(Wind), len(Pow_stor), len(Pow_rel))
#     ax3.bar(X_, Pow_stor, color = 'indianred', label = 'Power stored')
#     ax3.set_title('Renewable power generation', fontsize = 14)
#     ax3.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
#     ax3.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
#     ax3.set_ylabel('[MW]', fontsize= 14)
#     ax3.tick_params(axis='x', labelsize =13)
#     ax3.tick_params(axis='y', labelsize =14)

#     leg3 = ax3.legend(bbox_to_anchor=(1.18, 1), fontsize = 12)
#     leg3.get_frame().set_edgecolor('black')

#     ax1.xaxis.set_ticks_position('both')
#     ax3.yaxis.set_ticks_position('both')
#     ax3.xaxis.set_ticks_position('both')

#     plt.show()

#     return


# for DATA_ in DATA:
#     h2_prod_inv(DATA_, 2)

# #%%

# def scale(list_:list):
#     div = max(list_)
#     list2_ = [100*i/div for i in list_]
#     return list2_

# def schedule(DATA_:list, year_:int):
#     """Plots green and blue hydrogen production for a chosen year alongside hydrogen local and geological storage

#     Args:
#         DATA_ (list): list containing dictionaiers with data
#         year_ (int): year being plotted
#     """
#     Green, Blue, Local, Geo, H2, Solar, Wind, Pow_stor, Pow_rel = ([] for _ in range(9))
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     scenario_ = SCENARIO[0]
#     for d, h in product(D, H):
#         Local.append(DATA_[scenario_][year_]['Sch_S']['HO']['H2_C'][h][d]['Inv']/907.185)
#         Geo.append(DATA_[scenario_][year_]['Sch_S']['HO']['H2_L'][h][d]['Inv']/907.185)
#         H2.append((DATA_[scenario_][year_]['Sch_S']['HO']['H2_C'][h][d]['S'] \
#             + DATA_[scenario_][year_]['Sch_S']['HO']['H2_L'][h][d]['S'])/907.185)

#         Green.append(DATA_[scenario_][year_]['Sch_P']['HO']['AKE'][h][d]['P']*dict_conversion['AKE']['H2_G']/907.185)
#         Blue.append(DATA_[scenario_][year_]['Sch_P']['HO']['SMRH'][h][d]['P']/907.185)
#         # value = DATA_[scenario_][year_]['Sch_P']['HO']['AKE'][h][d]['P']*dict_conversion['AKE']['H2_G'] +  DATA_[scenario_][year_]['Sch_P']['HO']['SMRH'][h][d]['P']
#         Solar.append(DATA_[scenario_][year_]['Sch_P']['HO']['PV'][h][d]['P'])
#         Wind.append(DATA_[scenario_][year_]['Sch_P']['HO']['WF'][h][d]['P'])
#         Pow_stor.append(
#             sum(DATA_[scenario_][year_]['Sch_P']['HO'][i][h][d]['P'] for i in ['LiI_c', 'CAES_c', 'PSH_c'])
#             )
#         Pow_rel.append(
#             sum(DATA_[scenario_][year_]['Sch_P']['HO'][i][h][d]['P'] for i in ['LiI_d', 'CAES_d', 'PSH_d'])
#         )


#     Local = scale(Local)
#     Geo = scale(Geo)
#     Green = scale(Green)
#     Blue = scale(Blue)
#     Solar = scale(Solar)
#     Wind = scale(Wind)
#     Pow_rel = scale(Pow_rel)
#     Pow_stor = scale(Pow_stor)

#     fig, ax = plt.subplots(8,1, figsize = (16,18))
#     X_ = np.arange(1,8761)
#     pos_list = [0, 744, 1344, 2160, 2800, 3624, 4344, 5088, 5832, 6552, 7296, 8016] # hours of the year corresponding to month
#     name_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

#     ax[0].plot(X_, Blue, color = 'dodgerblue', label = 'Blue pathway')
#     ax[0].title.set_text('(a) Steam methane reforming + Carbon capture')
#     ax[0].fill_between(X_, Blue, color = 'dodgerblue', alpha = 0.5)

#     ax[1].plot(X_, Green, color = 'seagreen', label = 'Green pathway')
#     ax[1].title.set_text('(b) Alkaline water electrolysis')
#     ax[1].fill_between(X_, Blue, color = 'seagreen', alpha = 0.9)

#     ax[2].plot(X_, Local, color = 'teal', label = 'Local storage')
#     ax[2].fill_between(X_, Local, color = 'teal', alpha = 0.9)
#     ax[2].title.set_text('(c) Liquefied local $H_{2}$ storage')

#     ax[3].plot(X_, Geo, color = 'darkorange', label = 'Geological storage')
#     ax[3].fill_between(X_, Geo, color = 'darkorange', alpha = 0.9)
#     ax[3].title.set_text('(d) Geological $H_{2}$ storage')

#     ax[4].plot(X_, Solar, color = 'orange', label = 'Solar')
#     ax[4].fill_between(X_, Solar, color = 'orange', alpha = 0.9)
#     ax[4].title.set_text('(e) Solar photovoltaic array')

#     ax[5].plot(X_, Wind, color = 'darkgreen', label = 'Wind')
#     ax[5].fill_between(X_, Wind, color = 'darkgreen', alpha = 0.9)
#     ax[5].title.set_text('(f) Wind mill array')

#     ax[6].plot(X_, Pow_rel, color = 'cornflowerblue', label = 'Power discharged')
#     ax[6].fill_between(X_, Pow_rel, color = 'cornflowerblue', alpha = 0.9)
#     ax[6].title.set_text('(g) Power discharged')

#     ax[7].plot(X_, Pow_stor, color = 'indianred', label = 'Power stored')
#     ax[7].fill_between(X_, Pow_stor, color = 'indianred', alpha = 0.9)
#     ax[7].title.set_text('(i) Power stored')

#     ax[7].tick_params(axis='x', labelsize =12.5)
#     ax[0].tick_params(axis='x', labelsize =12.5)


#     for i in range(7):
#         ax[i].axes.xaxis.set_ticklabels([])
#         # ax[i].set_xticks('w')
#     for i in range(8):
#         ax[i].tick_params(axis='y', labelsize =13)
#         ax[i].grid(True, axis = 'x')
#         ax[i].tick_params(axis='y', which='minor')
#         ax[i].xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
#         ax[i].xaxis.set_ticks_position('both')
#     ax[7].xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
#     # ax[0].xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
#     # ax[0].tick_params(labelbottom=False,labeltop=True)

#     plt.savefig('capacity_utilization.png')
#     plt.show()

#     return


# for DATA_ in DATA:
#     schedule(DATA_, 4)

# #%%

# def carbon_eq(DATA:list):
#     """Compares the carbon intensity of hydrogen production [kg.CO2/kg.H2] under

#     Args:
#         DATA (list): list containing dictionaiers with data
#     """
#     iter_ = 0
#     fig, ax = plt.subplots(figsize=(10, 6))
#     color = [ 'lightcoral', 'palegoldenrod', 'yellowgreen']
#     width = 0.2
#     space = 0.2
#     for DATA_ in DATA:
#         SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#         scenario_ = SCENARIO[0]
#         Y_, X_ = [], []

#         for year_ in YEAR:
#             Y_.append(DATA_[scenario_][year_]['Net_S']['HO']['CO2_Vent']['S_annual']/(DATA_[scenario_][year_]['Net_S']['HO']['H2_C']['S_annual']\
#                 + DATA_[scenario_][year_]['Net_S']['HO']['H2_L']['S_annual']))
#             X_.append(year_ + 2022)
#         ax.bar([i  + width*(-1+iter_) for i in X_] , Y_, width, color = color[iter_], label = scenario_)
#         # ax.plot(X_ , Y_, color = color[iter_], label = scenario_)

#         iter_+= 1
#     ax.set_xticks(X_)
#     x_line = [2026.5]*70
#     y_line = np.arange(0,7,0.1)
#     ax.plot(x_line, y_line, '--', alpha = 0.5, color = 'slateblue')
#     plt.ylim([0, 7.5])
#     plt.title('Carbon intensity under different cost scenarios', fontsize=14)
#     plt.xlabel('Year', fontsize=14)
#     plt.ylabel('$kg.CO_{2}/kg.H_{2}$', fontsize=14)
#     plt.legend(fontsize=14, loc="upper left", mode = "expand", ncol = 3)
#     plt.xticks(fontsize= 14)
#     plt.yticks(fontsize= 14)
#     plt.grid(axis = 'y', alpha = 0.4, color = '0.85')
#     plt.annotate('End of term 1', (2026.5, 6.25), verticalalignment = 'top', horizontalalignment = 'center'\
#                     , fontsize = 14, color = 'slateblue')
#     plt.savefig('carbon_intensity.jpeg', dpi = 200)
#     plt.show()
#     return

# carbon_eq(DATA)

# #%%




# #%%
# YEAR = np.arange(0,5)
# def opportunistic_h2(DATA_:dict):
#     """fitted lines to show the relationship between
#     renewable generation potential and green H2 production

#     Args:
#         DATA_ (dict): dictionary with output data
#     """
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     for scenario_ in SCENARIO:
#         iter_ = 0
#         fig, ax = plt.subplots(figsize = (10,10))

#         patches = []
#         for year_ in YEAR:
#             patches.append(mpatches.Patch(color=(0, 0 + year_*0.1, 1 - year_*0.1), label= year_ + 2022))

#         for year_ in YEAR:
#             xdata, ydata = [], []
#             df = pd.DataFrame()
#             df_plot = pd.DataFrame()
#             for d in D:
#                 div = sum(DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink1'][h][d]['P'] + DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink2'][h][d]['P'] for h in H)
#                 if div >0:
#                     ydata.append(sum(DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink2'][h][d]['P'] for h in H)*100 /div)
#                     xdata.append(sum(DATA_[scenario_][year_]['Sch_P']['HO']['PV'][h][d]['P'] + DATA_[scenario_][year_]['Sch_P']['HO']['WF'][h][d]['P'] for h in H))
#             xdata = [i*100/max(xdata) for i in xdata]
#             ydata = np.array(ydata)
#             xdata = np.array(xdata)

#             df['x'] = xdata
#             df['y'] = ydata


#             z_scores = zscore(df)

#             abs_z_scores = np.abs(z_scores)
#             filtered_entries = (abs_z_scores < 1).all(axis=1)
#             filtered_df = df[filtered_entries]

#             # theta  = np.polyfit(x=df['x'], y=df['y'], deg=2)
#             theta  = np.polyfit(x=filtered_df['x'], y=filtered_df['y'], deg=2)

#             # print(f'The parameters of the curve: {theta}')

#             # Now, calculating the y-axis values against x-values according to
#             # the parameters theta0, theta1 and theta2
#             y_line = theta[2] + theta[1] * pow(filtered_df['x'], 1) + theta[0] * pow(filtered_df['x'], 2)
#             # y_line = theta[3] + theta[2] * pow(xdata, 1) + theta[1] * pow(xdata, 2) +  theta[0] * pow(xdata, 3)

#             filtered_df['yline'] = y_line

#             filtered_df = filtered_df.sort_values(by='x')


#             plot_df = pd.concat([filtered_df['x'], filtered_df['yline']], axis=1, keys= ['x', 'yline'])

#             plt.plot(filtered_df['x'], filtered_df['yline'], color =  (0, 0 + iter_*0.1, 1 - iter_*0.1), label = iter_)
#             if year_ < 5:
#                 plt.annotate(str(year_ + 2022), (filtered_df['x'].iloc[-1]+ 2, filtered_df['yline'].iloc[-1]), verticalalignment = 'top', horizontalalignment = 'center'\
#                     , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
#             elif year_ == 9:
#                 plt.annotate(str(year_ + 2022), (filtered_df['x'].iloc[0] - 1, filtered_df['yline'].iloc[0] -1), verticalalignment = 'top', horizontalalignment = 'center'\
#                     , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
#             else:
#                 plt.annotate(str(year_ + 2022), (filtered_df['x'].iloc[0] - 2, filtered_df['yline'].iloc[0]), verticalalignment = 'top', horizontalalignment = 'center'\
#                     , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
#             iter_+= 1
#         ax.xaxis.set_ticks_position('both')
#         ax.yaxis.set_ticks_position('both')
#         ax.yaxis.set_minor_locator(AutoMinorLocator())
#         plt.title('Opportunistic production of green $H_{2}$ \n under a(n) ' + scenario_.lower() + ' cost scenario', fontsize = 14)
#         plt.xlabel('Renewable power capacity utilization ', fontsize = 14)
#         plt.ylabel('Green hydrogen [$\%$ ]', fontsize = 14)
#         plt.xlim([10,75])
#         # plt.ylim([0,100])

#         # plt.legend(handles= patches, bbox_to_anchor=(1.05, 1))
#         plt.grid(alpha = 0.25)


#         plt.show()
#     return

# for DATA_ in DATA:
#     plot_ = opportunistic_h2(DATA_)

# #%%


# def split_opportunistic_h2(DATA_:dict):
#     """fitted lines to show the relationship between
#     renewable generation potential and green H2 production

#     Args:
#         DATA_ (dict): dictionary with output data
#     """
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     for scenario_ in SCENARIO:
#         iter_ = 0
#         fig, axs = plt.subplots(1,3, sharex = True, sharey = True, figsize = (15,5))
#         fig.add_subplot(111, frameon=False)
#         patches = []
#         for year_ in YEAR:
#             patches.append(mpatches.Patch(color=(0, 0 + year_*0.1, 1 - year_*0.1), label= year_ + 2022))

#         for year_ in YEAR:
#             xdata, ydata = [], []
#             df = pd.DataFrame()
#             df_plot = pd.DataFrame()
#             for d in D:
#                 div = sum(DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink1'][h][d]['P'] + DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink2'][h][d]['P'] for h in H)
#                 if div >0:
#                     ydata.append(sum(DATA_[scenario_][year_]['Sch_P']['HO']['H2_Sink2'][h][d]['P'] for h in H)*100 /div)
#                     xdata.append(sum(DATA_[scenario_][year_]['Sch_P']['HO']['PV'][h][d]['P'] + DATA_[scenario_][year_]['Sch_P']['HO']['WF'][h][d]['P'] for h in H))
#             xdata = [i*100/max(xdata) for i in xdata]
#             ydata = np.array(ydata)
#             xdata = np.array(xdata)

#             df['x'] = xdata
#             df['y'] = ydata


#             z_scores = zscore(df)

#             abs_z_scores = np.abs(z_scores)
#             filtered_entries = (abs_z_scores < 1).all(axis=1)
#             filtered_df = df[filtered_entries]

#             # theta  = np.polyfit(x=df['x'], y=df['y'], deg=2)
#             theta  = np.polyfit(x=filtered_df['x'], y=filtered_df['y'], deg=2)

#             # print(f'The parameters of the curve: {theta}')

#             # Now, calculating the y-axis values against x-values according to
#             # the parameters theta0, theta1 and theta2
#             y_line = theta[2] + theta[1] * pow(filtered_df['x'], 1) + theta[0] * pow(filtered_df['x'], 2)
#             # y_line = theta[3] + theta[2] * pow(xdata, 1) + theta[1] * pow(xdata, 2) +  theta[0] * pow(xdata, 3)

#             filtered_df['yline'] = y_line

#             filtered_df = filtered_df.sort_values(by='x')


#             plot_df = pd.concat([filtered_df['x'], filtered_df['yline']], axis=1, keys= ['x', 'yline'])


#             # plt.plot(filtered_df['x'], filtered_df['yline'], color =  (0, 0 + iter_*0.1, 1 - iter_*0.1), label = iter_)

#             if year_ < 5:
#                 axs[0].plot(filtered_df['x'], filtered_df['yline'], color =  (0, 0 + iter_*0.1, 1 - iter_*0.1), label = iter_)
#                 if year_ <3:
#                     axs[0].annotate(str(year_ + 2022), (filtered_df['x'].iloc[-1]+ 4, filtered_df['yline'].iloc[-1]), verticalalignment = 'top', horizontalalignment = 'center'\
#                         , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
#                 else:
#                     axs[0].annotate(str(year_ + 2022), (filtered_df['x'].iloc[-1]+ 4, filtered_df['yline'].iloc[-1]+ 2), verticalalignment = 'top', horizontalalignment = 'center'\
#                         , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
#             elif year_ in [5,6]:
#                 axs[1].plot(filtered_df['x'], filtered_df['yline'], color =  (0, 0 + iter_*0.1, 1 - iter_*0.1), label = iter_)
#                 if year_ == 6:
#                     axs[1].annotate(str(year_ + 2022), (filtered_df['x'].iloc[-1] + 4, filtered_df['yline'].iloc[-1]), verticalalignment = 'top', horizontalalignment = 'center'\
#                         , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
#                 else:
#                     axs[1].annotate(str(year_ + 2022), (filtered_df['x'].iloc[-1] + 4, filtered_df['yline'].iloc[-1] + 3), verticalalignment = 'top', horizontalalignment = 'center'\
#                         , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
#             else:
#                 axs[2].plot(filtered_df['x'], filtered_df['yline'], color =  (0, 0 + iter_*0.1, 1 - iter_*0.1), label = iter_)
#                 if year_ == 8:
#                     axs[2].annotate(str(year_ + 2022), (filtered_df['x'].iloc[-1] + 4, filtered_df['yline'].iloc[-1]), verticalalignment = 'top', horizontalalignment = 'center'\
#                         , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
#                 else:
#                     axs[2].annotate(str(year_ + 2022), (filtered_df['x'].iloc[-1] + 4, filtered_df['yline'].iloc[-1] + 2), verticalalignment = 'top', horizontalalignment = 'center'\
#                         , fontsize = 10, color =  (0, 0 + iter_*0.1, 1 - iter_*0.1))
#             iter_+= 1

#         plt.suptitle('Opportunistic co-production of $H_{2}$ under a ' + scenario_.lower() + ' cost scenario', fontsize = 14)
#         plt.xlabel('Renewable power capacity utilization [$\%$ ]', fontsize = 14)
#         plt.ylabel('Green hydrogen [$\%$ ]', fontsize = 14)
#         plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)
#         plt.subplots_adjust(wspace=0.05, hspace=0)
#         # plt.ylim([0,100])

#         # plt.legend(handles= patches, bbox_to_anchor=(1.05, 1))
#         for i in range(3):
#             axs[i].grid(alpha = 0.25)
#             axs[i].xaxis.set_ticks_position('both')
#             axs[i].yaxis.set_ticks_position('both')
#             # axs[i].yaxis.set_minor_locator(AutoMinorLocator())
#             axs[i].set_xlim([15,78])
#             # axs[i].set_xlabel('Renewable power capacity utilization ', fontsize = 14)
#             # axs[i].set_ylabel('Green hydrogen [$\%$ ]', fontsize = 14)


#         plt.show()
#     return

# for DATA_ in DATA:
#     plot_ = split_opportunistic_h2(DATA_)
# # %%

# def power_schedule(DATA_, year_):
#     Solar, Wind, Charge, PSH, CAES = ([] for _ in range(5))
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     scenario_ = SCENARIO[0]
#     for d, h in product(D, H):
#         Solar.append(DATA_[scenario_][year_]['Sch_P']['HO']['PV'][h][d]['P'])
#         Wind.append(DATA_[scenario_][year_]['Sch_P']['HO']['WF'][h][d]['P'])
#         Charge.append(DATA_[scenario_][year_]['Sch_S']['HO']['Charge'][h][d]['Inv'])
#         PSH.append(DATA_[scenario_][year_]['Sch_S']['HO']['H2O_E'][h][d]['Inv'])
#         CAES.append(DATA_[scenario_][year_]['Sch_S']['HO']['Air_C'][h][d]['Inv'])
#     fig, ax1 = plt.subplots()
#     X_ = np.arange(1,8761)
#     ax1.bar(X_, Wind)
#     ax1.bar(X_, Solar, bottom = Wind)
#     ax2 = ax1.twinx()
#     ax2.plot(X_, Charge, color = 'green')
#     plt.show()
#     # plt.show()
#     # plt.plot(X_, Charge)
#     # plt.show()
#     # plt.plot(X_, PSH)
#     # plt.show()
#     # plt.plot(X_, CAES)
#     # plt.show()
# power_schedule(TEST, 7)

# # for year_ in YEAR:
# # power_schedule(CON, year_)

# # %%

# # %%
# # %%


# # %%


# def annual_bgm(DATA_):
#     """Plots annual blue and green hydrogen contribution to the overall demand over the entire planning horizon

#     Args:
#         DATA_ (list): list containing dictionaiers with data
#     """
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     for scenario_ in SCENARIO:
#         Green_H2, Blue_H2, MEOH, X_ = ([] for _ in range(4))
#         for year_ in YEAR:
#             Green_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual']/(365*907.185))
#             Blue_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual']/(365*907.185))
#             MEOH.append(DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual']/(365*907.185))
#             X_.append(int(year_ + 2022))
#         width = 0.8
#         space = 0.2
#         fig, ax = plt.subplots(figsize=(8.27/3, 11.69/3))
#         ax.bar(X_, Blue_H2, width, color= 'lightsteelblue', label= 'Blue H2')
#         ax.bar(X_, Green_H2, width, bottom= Blue_H2, color='mediumseagreen', label='Green H2')
#         ax.bar(X_, MEOH, width, bottom= [sum(x) for x in zip(Blue_H2, Green_H2)] , color='r', label='Methanol')
#         plt.title('Total fuels production under a ' + scenario_ + ' cost scenario', fontsize=20)
#         plt.xlabel('Year', fontsize=20)
#         plt.ylabel('US tonnes', fontsize=20)
#         plt.legend(fontsize=20)
#         plt.xticks(fontsize= 16)
#         plt.yticks(fontsize= 16)
#         ax.set_xticks(X_)
#         plt.show()
#     return

# for DATA_ in DATA:
#     annual_bgm(DATA_)

# #%%

# def h2_cost(DATA:list):
#     """Compares the cost of hydrogen production under

#     Args:
#         DATA (list): list containing dictionaiers with data
#     """
#     iter_ = 0
#     fig, ax = plt.subplots(figsize=(8.27/3, 11.69/3))
#     color = ['lightcoral', 'palegoldenrod', 'yellowgreen']
#     width = 0.3
#     space = 0.2
#     for DATA_ in DATA:
#         SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#         scenario_ = SCENARIO[0]
#         Y_, X_ = [], []

#         for year_ in YEAR:
#             Y_.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/(DATA_[scenario_][year_]['Net_S']['HO']['H2_C']['S_annual']\
#                 + DATA_[scenario_][year_]['Net_S']['HO']['H2_L']['S_annual']))
#             # Green_H2.append(RESULTS[scenario_][year_]['Total']['HO']['Objective']/(RESULTS[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']))
#             X_.append(year_ + 2022)# + iter_*width)

#         # ax.(X_, Y_, width, color = color[iter_], label = scenario_, align='edge')
#         ax.plot(X_, Y_, color = color[iter_], label = scenario_)
#         ax.scatter(X_, Y_, color = color[iter_])

#         iter_+= 1
#     plt.title('Cost of hydrogen production under different cost scenarios', fontsize=20)
#     plt.xlabel('Year', fontsize=20)
#     plt.ylabel('$/kg.H2', fontsize=20)
#     plt.legend(fontsize=20)
#     plt.xticks(fontsize= 16)
#     plt.yticks(fontsize= 16)
#     plt.grid(axis = 'y', color = '0.85')
#     ax.set_xticks(X_)# - (iter_-1)*width for x in X_])
#     ax.set_yticks(np.arange(0,7))# - (iter_-1)*width for x in X_])
#     plt.show()
#     return


# h2_cost(DATA)


# # %%


# def annual_mile(DATA_):
#     """Plots percentage fuels contribution to meet mileage over the entire planning horizon

#     Args:
#         DATA_ (list): list containing dictionaiers with data
#     """
#     I = ['H2_Sink2', 'H2_Sink1', 'MEFC']
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     for scenario_ in SCENARIO:
#         Green_H2, Blue_H2, MEOH,  Green_H2x, Blue_H2x, MEOHx, X_, SUM = ([] for _ in range(8))
#         for year_ in YEAR:
#             Green_H2x.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual']*0.0315)
#             Blue_H2x.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual']*0.0315)
#             MEOHx.append(DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual']*0.19)
#             SUM.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual']*0.0315 + \
#                 DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual']*0.0315 + \
#                     DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual']*0.19)
#             Green_H2 = [a/b*100 for a,b in zip(Green_H2x, SUM)]
#             Blue_H2 = [a/b*100 for a,b in zip(Blue_H2x, SUM)]
#             MEOH = [a/b*100 for a,b in zip(MEOHx, SUM)]
#             X_.append(int(year_ + 2022))
#         width = 0.8
#         space = 0.2
#         fig, ax = plt.subplots(figsize=(8.27/3, 11.69/3))
#         ax.bar(X_, Blue_H2, width, color= 'lightsteelblue', label= 'Blue H2')
#         ax.bar(X_, Green_H2, width, bottom= Blue_H2, color='mediumseagreen', label='Green H2')
#         ax.bar(X_, MEOH, width, bottom= [sum(x) for x in zip(Blue_H2, Green_H2)] , color='r', label='Methanol')
#         plt.title('Percentage of miles met by fuel source for a ' + scenario_ + ' cost scenario', fontsize=20)
#         plt.xlabel('Year', fontsize=20)
#         plt.ylabel('Percentage', fontsize=20)
#         plt.legend(fontsize=20)
#         plt.xticks(fontsize= 16)
#         plt.yticks(fontsize= 16)
#         ax.set_xticks(X_)
#         plt.show()
#     return

# for DATA_ in DATA:
#     annual_mile(DATA_)

# # %%

# def annual_prod(DATA_):
#     """Plots percentage fuels contribution to meet mileage over the entire planning horizon

#     Args:
#         DATA_ (list): list containing dictionaiers with data
#     """
#     I = ['H2_Sink2', 'H2_Sink1', 'MEFC']
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     for scenario_ in SCENARIO:
#         Green_H2, Blue_H2, MEOH,  Green_H2x, Blue_H2x, MEOHx, X_, SUM = ([] for _ in range(8))
#         for year_ in YEAR:
#             Green_H2x.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual'])
#             Blue_H2x.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual'])
#             MEOHx.append(DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual'])
#             SUM.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual'] + \
#                 DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual'] + \
#                     DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual'])
#             Green_H2 = [a/b*100 for a,b in zip(Green_H2x, SUM)]
#             Blue_H2 = [a/b*100 for a,b in zip(Blue_H2x, SUM)]
#             MEOH = [a/b*100 for a,b in zip(MEOHx, SUM)]
#             X_.append(int(year_ + 2022))
#         width = 0.9
#         space = 0.2
#         fig, ax = plt.subplots(figsize=(8.27/3, 11.69/3))
#         ax.bar(X_, Blue_H2, width, color= 'lightsteelblue', label= 'Blue H2')
#         ax.bar(X_, Green_H2, width, bottom= Blue_H2, color='mediumseagreen', label='Green H2')
#         ax.bar(X_, MEOH, width, bottom= [sum(x) for x in zip(Blue_H2, Green_H2)] , color='r', label='Methanol')
#         plt.title('Percentage production by products ' + scenario_ + ' cost scenario', fontsize=20)
#         plt.xlabel('Year', fontsize=20)
#         plt.ylabel('Percentage', fontsize=20)
#         plt.legend(fontsize=20)
#         plt.xticks(fontsize= 16)
#         plt.yticks(fontsize= 16)
#         ax.set_xticks(X_)
#         plt.show()
#     return

# for DATA_ in DATA:
#     annual_prod(DATA_)
# #%%

# def annual_bgm(DATA_):
#     """Plots annual blue and green hydrogen, and methanol contribution to the overall mileage over the entire planning horizon

#     Args:
#         DATA_ (list): list containing dictionaiers with data
#     """
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     for scenario_ in SCENARIO:
#         Green_H2, Blue_H2, MEOH, X_ = ([] for _ in range(4))
#         for year_ in YEAR:
#             Green_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink2']['P_annual']*0.0315*10**(-3)/(365))
#             Blue_H2.append(DATA_[scenario_][year_]['Net_P']['HO']['H2_Sink1']['P_annual']*0.0315*10**(-3)/(365))
#             MEOH.append(DATA_[scenario_][year_]['Net_P']['HO']['MEFC']['P_annual']*0.19*10**(-3)/(365))
#             X_.append(int(year_ + 2022))
#         width = 0.6
#         space = 0.2
#         fig, ax = plt.subplots(figsize=(8.27/3, 11.69/3))
#         ax.bar(X_, Blue_H2, width, color= 'lightsteelblue', label= 'Blue H2')
#         ax.bar(X_, Green_H2, width, bottom= Blue_H2, color='mediumseagreen', label='Green H2')
#         ax.bar(X_, MEOH, width, bottom= [sum(x) for x in zip(Blue_H2, Green_H2)] , color='r', label='Methanol')
#         plt.title('Mileage controbution by fuel source under a ' + scenario_ + ' cost scenario', fontsize=20)
#         plt.xlabel('Year', fontsize=20)
#         plt.ylabel('1000 Miles/day', fontsize=20)
#         plt.legend(fontsize=20)
#         plt.xticks(fontsize= 16)
#         plt.yticks(fontsize= 16)
#         ax.set_xticks(X_)
#         plt.show()
#     return

# for DATA_ in DATA:
#     annual_bgm(DATA_)
# # %%


# def mile_cost(DATA:list):
#     """Compares the cost of hydrogen production under

#     Args:
#         DATA (list): list containing dictionaiers with data
#     """
#     iter_ = 0
#     fig, ax = plt.subplots(figsize=(8.27/3, 11.69/3))
#     color = ['lightcoral', 'palegoldenrod', 'yellowgreen']
#     width = 0.3
#     space = 0.2
#     for DATA_ in DATA:
#         SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#         scenario_ = SCENARIO[0]
#         Y_, X_ = [], []

#         for year_ in YEAR:
#             Y_.append(DATA_[scenario_][year_]['Total']['HO']['Objective']/((2 + year_*2)*1000*1.5*365))
#             # Green_H2.append(RESULTS[scenario_][year_]['Total']['HO']['Objective']/(RESULTS[scenario_][year_]['Net_P']['HO']['SMRH']['P_annual']))
#             X_.append(year_ + 2022)# + iter_*width)

#         # ax.(X_, Y_, width, color = color[iter_], label = scenario_, align='edge')
#         ax.plot(X_, Y_, color = color[iter_], label = scenario_)
#         ax.scatter(X_, Y_, color = color[iter_])

#         iter_+= 1
#     plt.title('Cost per mile under different cost scenarios', fontsize=20)
#     plt.xlabel('Year', fontsize=20)
#     plt.ylabel('$/mile', fontsize=20)
#     plt.legend(fontsize=20)
#     plt.xticks(fontsize= 16)
#     plt.yticks(fontsize= 16)
#     plt.grid(axis = 'y', color = '0.85')
#     ax.set_xticks(X_)# - (iter_-1)*width for x in X_])
#     # ax.set_yticks(np.arange(0,7))# - (iter_-1)*width for x in X_])
#     plt.show()
#     return

# mile_cost(DATA)

# # %%

# dict_demand = {
#     0: 10,
#     1: 20,
#     2: 40,
#     3: 80,
#     4: 160,
#     5: 320,
#     6: 420,
#     7: 520,
#     8: 620,
#     9: 720,
#     10: 820
# }
# list_ = sorted(dict_demand.items())
# x, y = zip(*list_)
# x = [x + 2021 for x in x]
# plt.plot(x,y)
# plt.title('Hydrogen demand')
# plt.xlabel('Year')
# plt.ylabel('USton/day')
# plt.xticks(x)


# # %%
# y = [(2 + year_*2)*1000 for year_ in YEAR]
# x = [year_ + 2021 for year_ in YEAR]
# plt.plot(x,y)
# plt.title('Mileage demand')
# plt.xlabel('Year')
# plt.ylabel('miles/day')
# plt.xticks(x)

# # %%
# #%%CAPACITY PLOT

# YEAR = np.arange(0,3)
# I = ['PV', 'WF', 'LiI_c', 'PSH_c', 'CAES_c', 'AKE', 'SMRH', 'DAC', 'MEFC', 'EOR', 'AQoff_DAC', 'AQoff_SMR', 'H2_C_c', 'H2_C_d', 'H2_L_c', 'H2_L_d' ]

# for DATA_ in DATA:
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     for scenario_ in SCENARIO:
#         for i_ in I:
#             input_ = []
#             for year_ in YEAR:
#                 input_.append(DATA_[scenario_][year_]['Net_P']['HO'][i_]['Cap_P'])
#             plt.plot(input_)
#             plt.title(i_)
#             # plt.title(I_labels_['short'][i_])
#             plt.show()

# #%%Total mileage
# for DATA_ in DATA:
#     SCENARIO = [scenario_ for scenario_ in DATA_.keys()]
#     for scenario_ in SCENARIO:
#             input_ = []
#             for year_ in YEAR:
#                 input_.append(DATA_[scenario_][year_]['Total']['HO']['Objective'])
#             plt.plot(input_)

#             plt.title('Total miles')
#             plt.show()
#     print(input_)

# #%%TEXAS STATE ENERGY PROFILE 2022
# size_ = 0.3

# #Consumption by source
# dict_con_source =   {
#     'Coal': 992.7,
#     'Hydroelectric Power':13.1,
#     'Natural Gas':4795.2,
#     'Motor Gasoline excl. Ethanol':1634,
#     'Distillate Fuel Oil':1148.7,
#     'Jet Fuel':320.5,
#     'Hydro-carbon gas liquid':2355,
#     'Residual Fuel':165.6,
#     'Other Petroleum':1261.5,
#     'Nuclear Electric Power':431.2,
#     'Biomass':262.4,
#     'Other Renewables':795.5,
#     # 'Net Electricity Imports':-15.2
#     # 'Net Interstate Flow of Electricity':111.5
# }

# inner_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown',\
#     'tab:olive', 'tab:cyan', 'tab:pink', 'tab:gray', 'indianred', 'teal']

# # create data
# dict_ = dict_con_source
# names = [i + ' (' + str(dict_[i]) + ')' for i in dict_.keys()]
# size = [dict_[i] for i in dict_.keys()]

# # Create a circle at the center of the plot
# # my_circle = plt.Circle( (0,0), 0.7, color='white')
# # Give color names
# plt.pie(size, labels=names, colors = inner_colors, textprops={'fontsize': 14}, wedgeprops={"edgecolor": 'white','linewidth': 3 , 'antialiased': True}, radius=1)
# p = plt.gcf()
# # p.gca().add_artist(my_circle)
# p.set_size_inches(10,10)
# # Show the graph
# plt.title('Outer - Texas power consumption by source (Trillion Btu) \
#     \n Inner - Texas power consumption by sector (%)', fontsize = 16)
# # plt.legend(bbox_to_anchor=(1, 1), fontsize = 14)


# #Consumption by sector
# dict_con_sec =   {
#     'Residential': 12.4,
#     'Commercial': 11.4,
#     'Industrial': 52.7,
#     'Transportation': 23.5
# }


# inner_colors2 = ['powderblue', 'darkseagreen', 'moccasin', 'darksalmon']

# # create data
# dict_ =  dict_con_sec
# names = [i + ' (' + str(dict_[i]) + '%)' for i in dict_.keys()]
# size = [dict_[i] for i in dict_.keys()]

# patches = []
# for i in range(len(inner_colors2)):
#     patches.append(mpatches.Patch(color=inner_colors2[i], label=names[i]))

# plt.legend(handles= patches, bbox_to_anchor=(1.03, 1))
# # Create a circle at the center of the plot
# my_circle = plt.Circle( (0,0), 0.7 - size_, color='white')
# # Give color names
# plt.pie(size,  colors = inner_colors2, textprops={'fontsize': 14, 'color' : 'white'}, wedgeprops={"edgecolor": 'white','linewidth': 3 , 'antialiased': True}, radius = 1 - size_)
# p = plt.gcf()
# p.gca().add_artist(my_circle)
# # p.set_size_inches(10,10)
# # Show the graph
# # plt.title('Texas power consumption by sector (%)', fontsize = 16)
# # plt.legend()
# plt.show()

# #%%

# #Production by source

# dict_prod_source = {
#     'Coal' :  308.4,
#     'Natural Gas - Marketed' :  11224.1,
#     'Wood and Waste' :  86.4,
#     'Crude Oil' :  10545.4,
#     'Nuclear Electric Power' :  431.2,
#     'Biofuels' :  67.8,
#     'Noncombustible Renewables' :  808.6,
# }

# dict_  = dict_prod_source
# # create data
# names = [i + ' (' + str(dict_[i]) + ')' for i in dict_.keys()]
# size = [dict_[i] for i in dict_.keys()]


# # Create a circle at the center of the plot
# my_circle = plt.Circle( (0,0), 0.7, color='white')
# # my_circle2 = plt.Circle( (0,0), 0.71, color='white')

# # Give color names
# plt.pie(size, labels=names, textprops={'fontsize': 14}, radius=1)
# p = plt.gcf()
# p.set_size_inches(10,10)

# p.gca().add_artist(my_circle)
# # p.gca().add_artist(my_circle2)

# # plt.legend()
# # p.set_size_inches(8,8)
# plt.title('Texas power production by source (Trillion Btu)', fontsize = 16)
# plt.show()


# # %%


# dict_con_source =   {
#     'Coal': 992.7,
#     'Hydroelectric':13.1,
#     'Natural Gas':4795.2,
#     'Motor Gasoline':1634,
#     'Distillate Fuel Oil':1148.7,
#     'Jet Fuel':320.5,
#     'Hydro-carbon gas liq.':2355,
#     'Residual Fuel':165.6,
#     'Other Petroleum':1261.5,
#     'Nuclear':431.2,
#     'Biomass':262.4,
#     'Other Renewables':795.5,
#     # 'Net Electricity Imports':-15.2
#     # 'Net Interstate Flow of Electricity':111.5
# }

# inner_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown',\
#     'tab:olive', 'tab:cyan', 'tab:pink', 'tab:gray', 'indianred', 'teal']

# # create data
# dict_ = dict_con_source
# names = [i + ' (' + str(dict_[i]) + ')' for i in dict_.keys()]
# size = [dict_[i] for i in dict_.keys()]

# # Create a circle at the center of the plot
# my_circle = plt.Circle( (0,0), 0.7, color='white')
# # Give color names
# plt.pie(size, labels=names, colors = inner_colors, textprops={'fontsize': 14}, wedgeprops={"edgecolor": 'white','linewidth': 0 , 'antialiased': True}, radius=1)
# p = plt.gcf()
# p.gca().add_artist(my_circle)
# p.set_size_inches(10,10)
# # Show the graph
# plt.title('Texas power consumption by source (Trillion Btu)' , fontsize = 16)
# # plt.legend(bbox_to_anchor=(1, 1), fontsize = 14)


# # %%
# dict_con_sec =   {
#     'Residential': 12.4,
#     'Commercial': 11.4,
#     'Industrial': 52.7,
#     'Transportation': 23.5
# }


# inner_colors2 = ['powderblue', 'darkseagreen', 'moccasin', 'darksalmon']

# # create data
# dict_ =  dict_con_sec
# names = [i + ' (' + str(dict_[i]) + '%)' for i in dict_.keys()]
# size = [dict_[i] for i in dict_.keys()]

# patches = []
# for i in range(len(inner_colors2)):
#     patches.append(mpatches.Patch(color=inner_colors2[i], label=names[i]))

# # plt.legend(handles= patches, bbox_to_anchor=(1, 1), fontsize = 14)
# # Create a circle at the center of the plot
# my_circle = plt.Circle( (0,0), 0.7, color='white')
# # Give color names
# plt.pie(size, labels = names, colors = inner_colors2, textprops={'fontsize': 14}, wedgeprops={"edgecolor": 'white','linewidth': 3 , 'antialiased': True}, radius = 1)
# p = plt.gcf()
# p.gca().add_artist(my_circle)
# p.set_size_inches(10,10)
# # Show the graph
# plt.title('Texas power consumption by sector (%)', fontsize = 16)
# # plt.legend()
# plt.show()
# # %%

# def f_conv(i):
#     with open('F_CONV.pkl', 'rb') as f:
#         data = pkl.load(f)
#     D = np.arange(1,366)#Seasons (d) days in this case
#     H = np.arange(0,24)#Time (t)
#     list_ = []
#     for d, h in product(D,H):
#         list_.append(data['HO'][i][d][h])
#     pos_list = [0, 744, 1344, 2160, 2800, 3624, 4344, 5088, 5832, 6552, 7296, 8016] # hours of the year corresponding to month
#     name_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
#     fig, ax = plt.subplots(figsize=(20,5))
#     # plt.figure(figsize=(20,5))
#     ax.set_title(I_labels_['long'][i] , fontsize = 14)
#     ax.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
#     ax.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
#     ax.plot(list_)
#     plt.show()
#     return

# f_conv('PV')
# f_conv('WF')
