# %%
#!/usr/bin/env python3

"""Energia module for energy systems modeling and optimization
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
# from IPython.display import display, Math, Latex
import IPython.display as ip
import inspect

from pyomo.environ import *
from pyomo.opt import SolverStatus, TerminationCondition


class opt:
    """
    choose how to optimize the model
    """

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name


class process:
    """
    creates a process object
    """

    def __init__(self, name: str, conversion: dict, label: str = '', year: int = 0, prod_max: float = 0, prod_min: float = 0, cap_seg: dict = {}, capex_seg: dict = {},
                 carbon_credit: bool = False, gwp: float = 0, land: float = 0, trl: str = '', block: str = '', source: str = 'citation needed'):
        """process object parameters

        Args:
            name (str): ID for process
            conversion (dict): conversion data
            label (str, optional): name of the process. Defaults to ''.
            year (int, optional): Year when process is introduced. Defaults to 0.
            prod_max (float, optional): Maximum allowed capacity increase in a year. Defaults to 0.
            prod_min (float, optional): Minimum allowed capacity increase in a year. Defaults to 0.
            cap_seg (float, optional): capacity segment for pwl costing. Defaults to {}.
            capex_seg (float, optional): capex segment for pwl costing. Defaults to {}.
            carbon_credit(bool, optional): True if carbon tax credits are earned through the process. Defaults to False
            gwp (float, optional): global warming potential for process. Defaults to 0.
            land (float, optional): land use per production of nominal resource. Defaults to 0.
            trl (str, optional): TRL level of the process. Defaults to ''.
            block (str, optional): representative block. Defaults to ''.
            source (str, optional): data source. Defaults to ''.

        """
        self.name = name
        self.conversion = conversion
        self.label = label
        self.year = year
        self.prod_max = prod_max
        self.prod_min = prod_min
        self.cap_seg = cap_seg
        self.capex_seg = capex_seg
        self.carbon_credit = carbon_credit
        self.gwp = gwp
        self.land = land
        self.trl = trl
        self.block = block
        self.source = source

    def __repr__(self):
        return self.name


class resource:
    """
    creates a resource object
    """

    def __init__(self, name: str, label: str = '', consumption_max: float = 0, loss: float = 0, revenue: float = 0, 
                 price: float = 0, mile: float = 0, store_max: float = 0, store_min: float = 0, sell: bool = False, demand: bool = False, basis: str = '', block: str = ''):
        """resource object parameters

        Args:
            name (str): ID for the resource
            label (str, optional): name of the resource. Defaults to ''.
            consumption_max (float, optional): Maximum allowed resource consumption in time period [unit/h]. Defaults to 0.
            loss (float, optional): Amount of resource lost in time period [h]. Defaults to 0.
            revenue (float, optional): Amount earned through sale of resource [$/unit]. Defaults to 0.
            price (float, optional): Purchase cost of unit [$/unit]. Defaults to 0.
            mile (float, optional): mileage offered by resource [mile/unit]. Defaults to 0.
            store_max (float, optional): Maximum storage capacity increase in a year. Defaults to 0.
            store_min (float, optional): Minimum storage capacity increase in a year. Defaults to 0.
            sell (bool, optional): True if resource can be discharged. Defaults to False.
            demand (bool, optional): True, if the process has to meet set demand. Defaults to False.
            basis (str, optional): Base unit for the resource. Defaults to ''.

        """
        self.name = name
        self.label = label
        self.consumption_max = consumption_max
        self.loss = loss
        self.revenue = revenue
        self.price = price
        self.mile = mile
        self.store_max = store_max
        self.store_min = store_min
        self.sell = sell
        self.demand = demand
        self.basis = basis
        self.block = block

    def __repr__(self):
        return self.name


class material:
    """
    creates a material object
    """

    def __init__(self, name: str, label: str = '', gwp: float = 0):
        """material object parameters

        Args:
            name (str): ID for material 
            label (str, optional): name of the material. Defaults to ''.
            gwp (float, optional): global warming potential. Defaults to 0.
        """
        self.name = name
        self.label = label
        self.gwp = gwp

    def __repr__(self):
        return self.name

class transport:
    """creates a transport object for specific material
    """
    def __init__(self, name:str, resources:list, locations:list, year:int = 0, label:str = '', trans_max: float = 0, trans_loss: float = 0, trans_cost: float = 0, trans_emit: float = 0):
        """transport object parameters

        Args:
            name (str): ID for transportation mode
            resources (list): specific resources transported through mode.
            locations (list): locations between which transport mode is setup.
            label (int, optional): year when transportation mode is introduced. Defaults to 0.
            label (str, optional): name for the transportation mode. Defaults to ''.
            trans_max (float, optional): maximum capacity of material that can be transported. Defaults to 0.
            trans_loss (float, optional): _description_. Defaults to 0.
            trans_cost (float, optional): _description_. Defaults to 0.
            trans_emit (float, optional): _description_. Defaults to 0.
        """
        self.name = name
        self.resources = resources
        self.locations = locations
        self.year = year
        self.label = label 
        self.trans_max = trans_max
        self.trans_loss = trans_loss
        self.trans_cost = trans_cost
        self.trans_emit = trans_emit
    
    def __refr__(self):
        return self.name



 
class location:
    """
    creates a location object
    """

    def __init__(self, name: str, label: str = '', PV_class: str = '', WF_class: str = '', LiI_class: str = '', PSH_class: str = ''):
        """location object parameters

        Args:
            name (str): ID for locations
            label (str, optional): name of the location. Defaults to ''.
            PV_class (str, optional): Residential solar PV costing class based on average availability (DOE/NRELatb). Defaults to ''.
            WF_class (str, optional): Wind costing class based on average availability (DOE/NRELatb). Defaults to ''.
            LiI_class (str, optional): Charging cycle for lithium ion batteries (NRELatb). Defaults to ''.
            PSH_class (str, optional): PSH category (NRELatb). Defaults to ''.
        """
        self.name = name
        self.label = label
        self.PV_class = PV_class
        self.WF_class = WF_class
        self.LiI_class = LiI_class
        self.PSH_class = PSH_class

    def __repr__(self):
        return self.name


class cost_scenario:
    """
    choose a cost scenario
    """

    def __init__(self, name: str, horizon: float, label: str = '', enterprise: float = '', utility: float = '', pilot: float = '', repurposed: float = ''):
        """cost scenario parameters

        Args:
            name (str): ID for the cost scenario
            label (str, optional): name of the location. Defaults to ''.
            horizon (float): length of planning horizon
            enterprise (float, optional): reduction in cost over horizon for enterprise TRL. Defaults to ''.
            utility (float, optional): reduction in cost over horizon for utility TRL. Defaults to ''.
            pilot (float, optional): reduction in cost over horizon for pilot TRL. Defaults to ''.
            repurposed (float, optional): reduction in cost over horizon for repurposed TRL. Defaults to ''.
        """
        self.name = name
        self.label = label
        self.horizon = horizon
        self.enterprise = enterprise
        self.utility = utility
        self.pilot = pilot
        self.repurposed = repurposed

    def __repr__(self):
        return self.name


# Functions
def get_data(file_name: str) -> dict:
    """gets data from energia json database

    Args:
        file_name (str): name of file

    Returns:
        dict: dictionary with data
    """
    with open(file_name + '.json') as f:
        data_ = json.load(f)
        f.close()
    return data_


def dump_data(data: dict, file_name: str):
    """dump data in any of the following formats: .json, .txt, .pkl

    Args:
        data (dict): dictionary with cost trajectories for all processes
        file_name (str): name of output file with format, e.g. file_name.pkl
    """

    if '.pkl' in file_name:
        with open(file_name, "wb") as f:
            pkl.dump(data, f)
            f.close()
    elif '.json' in file_name:
        with open(file_name, 'w') as f:
            json.dump(data, f)

    elif '.txt' in file_name:
        with open(file_name, "w") as f:
            f.write(str(data))
            f.close()
    return


def make_conversion_dict(file_name: str) -> dict:
    """updates conversion.json conversion values by process

    Returns:
        dict: dictionary with conversion values
    """
    conversion_dict_ = pd.read_csv(file_name, index_col=0).dropna(
        axis='rows').transpose().to_dict()
    dump_data(conversion_dict_, 'conversion.json')
    return conversion_dict_


def make_material_dict(file_name: str):
    """updates infra_mat.json which contains infrastructaral material needs by facility

    Returns:
        infra_mat_dict_: dictionary with infrastructaral material needs
    """
    material_dict_ = pd.read_csv(file_name, index_col=0).dropna(
        axis='rows').transpose().to_dict()
    dump_data(material_dict_, 'material.json')
    return material_dict_


def make_cost_dict(location_list: list, cost_scenario_list: list, process_list: list, year_list: list) -> dict:
    """intializes an empty dictionary for cost data for all processes

    Args:
        location_list (list): list of locations
        cost_scenario_list (list): list of scenarios
        process_list (list): list of processes
        year_list (list): list of years

    Returns:
        dict: dictionary with costs
    """

    cost_metrics_list = ['CAPEX', 'Fixed O&M',
                         'Variable O&M', 'units', 'source']
    cost_dict = {location_.name: {cost_scenario.name: {process_.name: {year_: {cost_metric_: {} for cost_metric_ in cost_metrics_list}
                                                                       for year_ in year_list} for process_ in process_list} for cost_scenario in cost_scenario_list} for location_ in location_list}

    return cost_dict


def fetch_components(process_list: list, master_list: list, dict_with_relevant_data: dict) -> str:
    """Fetches a list of materials for which relevant data is available 
    conversion for example will be used draw resources from the specified processes

    Args:
        process_list (list): list of processes
        master_list (list): master list of all defined elements 
        dict_with_relevant_data (dict): dictionary to look up for matches, conversion with resources for example


    Returns:
        str: list of components
    """
    list_ = []
    for process, value in product(process_list, master_list):
        if dict_with_relevant_data[process.name][value.name] != 0:
            list_.append(value) if value not in list_ else list_
    return list_


def make_f_conv(location_list: list, day_list: list, hour_list: list, process_list: list, varying_process_dict: dict):
    """makes a dictionary of varying conversion factors.
    minimum resolution: hour

    Args:
        location_list (list): list of locations
        day_list (list): list of days/seasons
        hour_list (list): list of hours
        process_list (list): list of processes
        varying_process_dict[location.name] (pd.DataFrame): dataframe with varying outputs for processes

    Returns:
        dict: dictionary containing hourly conversion factors for all processes
    """
    # declare empty dict
    f_conv_dict_ = {location.name: {process.name: {day: {hour: {} for hour in hour_list}
                                                   for day in day_list} for process in process_list} for location in location_list}
    for process, location in product(process_list, location_list):
        if process.name in [col for col in varying_process_dict[location.name]]:
            varying_process_dict[location.name][process.name] = varying_process_dict[location.name][process.name] / \
                max(varying_process_dict[location.name][process.name])
    for location, process, day, hour in product(location_list, process_list, day_list, hour_list):
        if process.name in [col for col in varying_process_dict[location.name]]:
            f_conv_dict_[location.name][process.name][day][hour] = varying_process_dict[location.name][(
                varying_process_dict[location.name]['day'] == day) & (varying_process_dict[location.name]['hour'] == hour)][process.name].values[0]
        else:
            f_conv_dict_[location.name][process.name][day][hour] = 1

    return f_conv_dict_


def make_f_purchase(location_list: list, day_list: list, hour_list: list, resource_list: list, varying_resource_df: pd.DataFrame) -> dict:
    """makes a dictionary for varying resource costs.
    minimum resolution hour|

    Args:
        location_list (list): list of locations
        day_list (list): list of days/seasons
        hour_list (list): list of hours
        process_list (list): list of processes
        varying_resource_df (pd.DataFrame): dataframe with varying resource costs

    Returns:
        dict: dictionary containing hourly conversion factors for all processes
    """

    f_purchase_dict_ = {location.name: {resource.name: {day: {hour: {} for hour in hour_list}
                                                        for day in day_list} for resource in resource_list} for location in location_list}
    for location, resource, day, hour in product(location_list, resource_list, day_list, hour_list):
        if resource.name in [col for col in varying_resource_df]:
            f_purchase_dict_[location.name][resource.name][day][hour] = varying_resource_df[varying_resource_df['day']
                                                                                            == day][resource.name].values[0]  # use day of the year (doy)
        else:
            f_purchase_dict_[location.name][resource.name][day][hour] = 1

    # varying_resource_df2_ = pd.DataFrame(columns = ['day', 'hour', var])

    # for day, hour in product(varying_resource_df['day'], hour_list):
    #     varying_resource_df2_ = varying_resource_df2_.append({'day': day, 'hour': hour, var: varying_resource_df[var][varying_resource_df['day'] == day].values[0] }, ignore_index = True)

    # , varying_resource_df2_

    return f_purchase_dict_


def make_henry_price_df(file_name: str, year: int, stretch: bool) -> pd.DataFrame:
    """makes a df from Henry Spot Price Index data
    Days with missing data are filled using previous day values
    The costs are converted to $/kg from $/MMBtu using a factor of /22.4

    Args:
        file_name (str): provide csv file with data
        year (int): import data from a particular year
        stretch (bool): if True, streches the timescale from days (365) to hours (8760)


    Returns:
        pd.DataFrame: data frame with varying natural gas prices
    """

    df_ = pd.read_csv(file_name, skiprows=5, names=['date', 'CH4'])

    df_[["month", "day", "year"]] = df_['date'].str.split("/", expand=True)
    df_ = df_[df_['year'] == str(year)].astype(
        {"month": int, "day": int, "year": int})
    df_['date'] = pd.to_datetime(df_['date'])  # , format='%d%b%Y:%H:%M:%S.%f')
    df_['doy'] = df_['date'].dt.dayofyear
    df_ = df_.sort_values(by=['doy'])
    df_ = df_.drop(columns='date').dropna(axis='rows')
    doy_list = [i for i in df_['doy']]

    for i in np.arange(1, 366):  # fixes values for weekends and holidays to last active day
        if i not in doy_list:
            if i == 1:  # onetime fix if first day has no value, takes value from day 2
                df_ = df_.append({'CH4': df_['CH4'][df_[
                                 'doy'] == 2].values[0], 'month': 1, 'day': 1, 'year': year, 'doy': 1}, ignore_index=True)
            else:
                df_ = df_.append({'CH4': df_['CH4'][df_['doy'] == i-1].values[0],
                                  'month': df_['month'][df_['doy'] == i-1].values[0],
                                  'day': df_['day'][df_['doy'] == i-1].values[0],
                                  'year': df_['year'][df_['doy'] == i-1].values[0],
                                  'doy': i}, ignore_index=True)

    df_ = df_.sort_values(by=['doy'])
    df_ = df_.reset_index(drop=True)
    df_['CH4'] = df_['CH4'] / 22.4  # convert from $/MMBtu to $/kg
    df_ = df_[['CH4', 'doy']].rename(columns={'doy': 'day'})

    if stretch == False:
        df_ = df_
    else:
        df_ = df_.loc[df_.index.repeat(24)].reset_index(drop=True)
        df_['hour'] = [int(i) for i in range(0, 24)]*365
    return df_


def make_nrel_cost_df(location: location, nrel_cost_xlsx, pick_nrel_process_list: list, year_list: list, case: str, crpyears: float) -> pd.DataFrame:
    """makes dataframe for nrel atb data
    processes should be specified based on NREL technology tags
    classes for technology will be picked based on location 
    list of cost metrics ('CAPEX', 'Fixed O&M', 'Variable O&M')

    Args:
        location (location): location object
        nrel_cost_xlsx (.xlsx): excel file from NREL ATB 
        pick_nrel_process_list (list): list of nrel defined processes 
        year_list (list): list of years
        case (str): Market or Research case
        crpyears (float): cost recovery period

    Returns:
        pd.DataFrame: with nrel costing data for the specified year
    """
    cost_metrics_list = ['CAPEX', 'Fixed O&M', 'Variable O&M', 'units']

    # import nrel atb cost dataset
    nrel_cost_df_ = pd.read_excel(nrel_cost_xlsx, sheet_name='cost')
    nrel_cost_df_ = nrel_cost_df_[nrel_cost_df_['technology'].isin(
        pick_nrel_process_list)]  # choose technologies
    nrel_cost_df_ = nrel_cost_df_[nrel_cost_df_['core_metric_parameter'].isin(
        cost_metrics_list)]  # choose costing data to import
    nrel_cost_df_ = nrel_cost_df_[nrel_cost_df_[
        'core_metric_case'].isin([case])]  # choose market case
    nrel_cost_df_ = nrel_cost_df_[nrel_cost_df_['crpyears'].isin(
        [crpyears])]  # choose cost recovery period of 20 year
    nrel_cost_df_['technology'].replace({'LandbasedWind': 'WF', 'UtilityPV': 'PV', 'Utility-Scale Battery Storage': 'LiI_c',
                                        'Pumped Storage Hydropower': 'PSH_c'}, inplace=True)  # replace names to process IDS
    nrel_cost_df_ = nrel_cost_df_[((nrel_cost_df_['technology'] == 'PV') & (nrel_cost_df_['techdetail'] == location.PV_class)) |  # class 5 solar PV\
                                  ((nrel_cost_df_['technology'] == 'WF') & (nrel_cost_df_[
                                   'techdetail'] == location.WF_class))  # class 4 wind farms\
                                  | ((nrel_cost_df_['technology'] == 'LiI_c') & (nrel_cost_df_['techdetail'] == location.LiI_class))  # 8hr battery cycle LiI\
                                  | ((nrel_cost_df_['technology'] == 'PSH_c') & (nrel_cost_df_['techdetail'] == location.PSH_class))]  # class 3 PSH
    year_list = [year_ + 2021 for year_ in year_list]
    nrel_cost_df_ = nrel_cost_df_[nrel_cost_df_['core_metric_variable'].isin(
        year_list)]  # get data for years in years_list
    nrel_cost_df_ = nrel_cost_df_.drop(columns=['index', 'revision', 'atb_year', 'core_metric_key',
                                       'core_metric_case', 'crpyears', 'techdetail'])  # drop unnecessary columns
    nrel_cost_df_.columns = [
        'metric', 'process', 'cost_scenario_list', 'year', 'units', 'cost']  # rename columns
    nrel_cost_df_ = nrel_cost_df_.reset_index(drop=True)  # reset index
    # change years to int list 0...
    nrel_cost_df_['year'] = nrel_cost_df_['year'] - 2021
    nrel_cost_df_['cost_scenario_list'] = nrel_cost_df_[
        'cost_scenario_list'].str.lower()

    # bring all units to $/MW
    
    nrel_cost_df_.loc[nrel_cost_df_.units == '$/KW-yr', ['cost', 'units']] = 1000*nrel_cost_df_.loc[nrel_cost_df_.units == '$/KW-yr']['cost'].values[0], '$/MW'
    nrel_cost_df_.loc[nrel_cost_df_.units == '$/kW', ['cost', 'units']] = 1000*nrel_cost_df_.loc[nrel_cost_df_.units == '$/kW']['cost'].values[0], '$/MW'
    nrel_cost_df_.loc[nrel_cost_df_.units == '$/MWh', ['cost', 'units']] = 8760*nrel_cost_df_.loc[nrel_cost_df_.units == '$/MWh']['cost'].values[0], '$/MW'
    
    # nrel_cost_df_['cost'][nrel_cost_df_['units']
    #                       == '$/KW-yr'] = nrel_cost_df_['cost'][nrel_cost_df_['units'] == '$/KW-yr']*1000
    # nrel_cost_df_['units'][nrel_cost_df_['units'] == '$/KW-yr'] = '$/MW'
    # nrel_cost_df_['cost'][nrel_cost_df_['units']
    #                       == '$/kW'] = nrel_cost_df_['cost'][nrel_cost_df_['units'] == '$/kW']*1000
    # nrel_cost_df_['units'][nrel_cost_df_['units'] == '$/kW'] = '$/MW'
    # nrel_cost_df_['cost'][nrel_cost_df_['units']
    #                       == '$/MWh'] = nrel_cost_df_['cost'][nrel_cost_df_['units'] == '$/MWh']*8760
    # nrel_cost_df_['units'][nrel_cost_df_['units'] == '$/MWh'] = '$/MW'

    return nrel_cost_df_


def fill_cost(cost_dict: dict, process, location_list: list, cost_scenario_list: list,
              year_list: list, cost_parameters: dict, nrel_cost_dict:dict = {}): #: pd.DataFrame = {}):
    """fills cost_dict with costing data(CAPEX, Variable and Fixed OPEX), nominal basis (units), and source
    data can be user-defined or taken from NREL

    Args:
        cost_dict (dict): contains cost data for processes
        process ([type]): process object
        location_list (list): set of locations
        cost_scenario_list (list): set of scenarios
        cost_parameters (dict): feeds values for cost metrics
        nrel_cost_df (pd.DataFrame): contains data from NREL ATB
    """
    cost_metrics_list = ['CAPEX', 'Fixed O&M',
                         'Variable O&M', 'units', 'source']

    for location, cost_scenario, year, cost_metric in product(location_list, cost_scenario_list, year_list, cost_metrics_list):
        if cost_metric == 'source':
            cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters['source']

        elif cost_metric in ['CAPEX', 'Fixed O&M', 'Variable O&M']:
            if process.trl == 'enterprise':
                if year == 0:
                    cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]
                elif year > 0 and year <= 10:
                    cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
                        cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.05*cost_scenario.enterprise*year)
                elif year > 10 and year <= 20:
                    cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
                        cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.05*cost_scenario.enterprise*year)
                else:
                    cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
                        cost_scenario.name][process.name][year-1][cost_metric]*(1 - 0.04*cost_scenario.enterprise*year)

            elif process.trl == 'utility':
                if year == 0:
                    cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]
                elif year > 0 and year <= 10:
                    cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
                        cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.6*cost_scenario.utility*year)
                elif year > 10 and year <= 20:
                    cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
                        cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.2*cost_scenario.utility*year)
                else:
                    cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
                        cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.0*cost_scenario.utility*year)

            elif process.trl == 'pilot':
                if year == 0:
                    cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]
                elif year > 0 and year <= 10:
                    cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[
                        location.name][cost_scenario.name][process.name][year-1][cost_metric]*(1 - cost_scenario.pilot*year)
                elif year > 10 and year <= 20:
                    cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
                        cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.6*cost_scenario.pilot*year)
                else:
                    cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
                        cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.1*cost_scenario.pilot*year)

            elif process.trl == 'repurposed':
                cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]*(
                    1 - cost_scenario.repurposed*year/(cost_scenario.horizon-1))
            elif process.trl == 'discharge':
                cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]
            elif process.trl == 'nocost':
                cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = 0
            elif process.trl == 'nrel':
                dict_ = nrel_cost_dict
                value = dict_[location.name]['cost'][((dict_[location.name]['metric'] == cost_metric) & (dict_[location.name]['process'] == process.name) & (
                    dict_[location.name]['cost_scenario_list'] == cost_scenario.name) & (dict_[location.name]['year'] == year))].values
                if not value.any():
                    cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = 0
                else:
                    cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = value[0]

        elif cost_metric == 'units':
            if process.trl == 'nrel':
                dict_ = nrel_cost_dict
                cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] \
                    = dict_[location.name]['units'][((dict_[location.name]['metric'].isin(cost_metrics_list)) & (dict_[location.name]['process'] == process.name) & (dict_[location.name]['cost_scenario_list'] == cost_scenario.name) & (dict_[location.name]['year'] == year))].values[0]
            elif process.trl == 'nocost':
                cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = 'None'
            else:
                cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] \
                    = cost_parameters['units']

    return


def scaler(input_df: pd.DataFrame, process: str) -> pd.DataFrame:
    """creates a scaled list from a df column for a process
    useful as input for functions such as reduce_scenario

    Args:
        input_df (pd.DataFrame): df with values to be scaled
        process (str): process object

    Returns:
        list: scaled list
    """
    rng = range(0, 24)
    col = [process[0:2] + str(i) for i in rng]
    reshaped_df = np.reshape(input_df[process].values, (365, 24))
    scale = StandardScaler().fit(reshaped_df)
    scaled_df = pd.DataFrame(scale.transform(reshaped_df), columns=col)
    return scaled_df


def find_euclidean_distance(cluster_node_a: list, cluster_node_b: list) -> float:
    """finds euclidean distances between two cluster nodes

    Args:
        cluster_node_a (float): index tag for cluster node a
        cluster_node_b (float): index tag for cluster node b

    Returns:
        float: euclidean distance 
    """
    euclidean_distance_ = [
        (a - b)**2 for a, b in zip(cluster_node_a, cluster_node_b)]
    euclidean_distance_ = sum(euclidean_distance_)
    return euclidean_distance_


def generate_connectivity_matrix():
    """generates a connectivity matrixto maintain chronology [..1,0,1..]

    Returns:
        array: matrix with connectivity relations
    """
    connect_ = np.zeros((365, 365), dtype=int)
    for i_ in range(len(connect_)):

        if i_ == 0:
            # connect_[i,364] = 1 #uncomment these to generate a cyclic matrix
            connect_[i_, 1] = 1
        elif i_ == 364:
            connect_[i_, 363] = 1
            # connect_[i,0] = 1
        else:
            connect_[i_, i_-1] = 1
            connect_[i_, i_+1] = 1
    return connect_


def reduce_scenario(varying_process_df: pd.DataFrame, varying_resource_df: pd.DataFrame, red_scn_method: str, rep_days_no: int) -> dict:
    """Reduces scenario to set of representative days
    days closest to the cluster centroids are chosen
    red_scn_methods available: Agglomorative Hierarchial Clustering (AHC)
    output dictionary contains representative days and their corresponding cluster weights

    Args:
        varying_process_df (pd.DataFrame): contains varying process paramters (e.g.: conversion factors)
        varying_resource_df (pd.DataFrame): contains varying resource paramters (e.g.: cost)
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

        scaled_df = pd.DataFrame()

        # standardize the values for all process and resources
        for var in varying_process:
            scaled_iter = scaler(varying_process_df, var)
            scaled_df = pd.concat([scaled_df, scaled_iter], axis=1)

        for var in varying_resource:
            scaled_iter = scaler(varying_resource_df, var)
            scaled_df = pd.concat([scaled_df, scaled_iter], axis=1)

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
            nearest_centroid_df = pd.DataFrame(data=nearest_centroid_array, columns=[
                                               col for col in scaled_df])

            # add cluster numbers to the dataset
            scaled_df['cluster_no'] = cluster_labels
            # add cluster numbers to the dataset
            nearest_centroid_df['cluster_no'] = scaled_df['cluster_no'].unique()
            euclidean_distance_list = []
            # closest actual days to the cluster centroids
            closest_to_centroid_df = pd.DataFrame(
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


def ahc_elbow(varying_process_df: pd.DataFrame, varying_resource_df: pd.DataFrame, red_scn_method: str, rep_days_no: int) -> dict:
    """Reduces scenario to set of representative days
    days closest to the cluster centroids are chosen
    red_scn_methods available: Agglomorative Hierarchial Clustering (AHC)
    output dictionary contains representative days and their corresponding cluster weights

    Args:
        varying_process_df (pd.DataFrame): contains varying process paramters (e.g.: conversion factors)
        varying_resource_df (pd.DataFrame): contains varying resource paramters (e.g.: cost)
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

        scaled_df = pd.DataFrame()

        # standardize the values for all process and resources
        for var in varying_process:
            scaled_iter = scaler(varying_process_df, var)
            scaled_df = pd.concat([scaled_df, scaled_iter], axis=1)

        for var in varying_resource:
            scaled_iter = scaler(varying_resource_df, var)
            scaled_df = pd.concat([scaled_df, scaled_iter], axis=1)

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
            nearest_centroid_df = pd.DataFrame(data=nearest_centroid_array, columns=[
                                               col for col in scaled_df])

            # add cluster numbers to the dataset
            scaled_df['cluster_no'] = cluster_labels
            # add cluster numbers to the dataset
            nearest_centroid_df['cluster_no'] = scaled_df['cluster_no'].unique()
            euclidean_distance_list = []
            # closest actual days to the cluster centroids
            closest_to_centroid_df = pd.DataFrame(
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
    matrix = np.zeros((len(series1) + 1, len(series2) + 1))
    for i,j in product(range(1, len(series1)+1), range(1, len(series2) + 1)):
        matrix[i, j] = np.inf
    matrix[0,0] = 0
    for i,j in product(range(1, len(series1)+1), range(1, len(series2) + 1)):
        cost = abs(series1[i-1] - series2[j-1]) 
        prev = np.min([matrix[i-1, j], matrix[i, j-1], matrix[i-1, j-1]]) 
        matrix[i,j] = cost + prev
    return matrix


def find_dtw_path(matrix:np.ndarray)-> list:
    """finds optimal warping path from a dynamic time warping cost matrix 

    Args:
        matrix (np.ndarray): cost matrix from application of dtw

    Returns:
        list: optimal path with list of coordinates
    """
    path  = []
    i,j = len(matrix) -1, len(matrix[0]) -1
    path.append([i,j])
    while i > 0 and j > 0:
        index_min = np.argmin([matrix[i-1, j], matrix[i, j-1], matrix[i-1, j-1]])
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


def get_annual_results(results_dict: dict, for_what, result_metric: str, location: location, scenario: cost_scenario, year_list: list) -> list:
    """Gets a list of results over the years for a chosen result metric 
    Annual results could included annual production ('P_annual')
    Annual results could included annual resource sales ('S_annual')
    Useful for plotting 

    Args:
        results_dict (dict): dictionary with results
        for_what: energia.object, can be resource or process
        result_metric (str): result metric to fetch data
        location (energia.location): location of choice
        scenario (energia.cost_scenario): cost scenario of choice
        year_list (list): list of years in the planning period

    Returns:
        list: results for the metric over the years

    annual system level: 'Opex_fix_total', 'Opex_var_total', 'Opex_total', 'Capex_total', 'Credit_total', 'Objective', 'B_total', 'GWP_total', 'Land_total' 'CO2_total', 'Mile_total', 'LCOH', 'LCPM', 'comp_time'
    annual production decisions: 'Opex', 'Opex_fix', 'Opex_var', 'Capex', 'P_annual', 'Cap_P', 'X_P' , 'Credit', 'GWP', 'Land'
    hourly production scheduling decisions: 'P'
    annual storage decisions: 'B_annual', 'S_annual', 'C_annual', 'GHG_total', 'Mile_annual', 'Cap_S', 'X_S'
    hourly inventory scheduling and resource purchase decisions: 'B', 'C', 'S', 'Inv'

    Example:
    list_PV_capacity = get_annual_results(results_dict = results_dict, for_what = PV, result_metric = 'Cap_P', location = HO, scenario = conservative, year_list = year_list)
    """

    Total = ['Opex_fix_total', 'Opex_var_total', 'Opex_total', 'Capex_total', 'Credit_total', 'Objective',
             'B_total', 'GWP_total', 'Land_total' 'CO2_total', 'Mile_total', 'LCOH', 'LCPM', 'comp_time']
    Net_P = ['Opex', 'Opex_fix', 'Opex_var', 'Capex',
             'P_annual', 'Cap_P', 'X_P', 'Credit', 'GWP', 'Land']
    Sch_P = ['P']
    Net_S = ['B_annual', 'S_annual', 'C_annual',
             'GHG_total', 'Mile_annual', 'Cap_S', 'X_S']
    Sch_S = ['B', 'C', 'S', 'Inv']

    annual_list = []
    year_list = [year for year in results_dict[scenario.name].keys()]

    for year in year_list:
        if result_metric in Total:
            annual_list.append(
                results_dict[scenario.name][year]['Total'][location.name][result_metric])

        elif result_metric in Net_P:
            annual_list.append(
                results_dict[scenario.name][year]['Net_P'][location.name][for_what.name][result_metric])

        elif result_metric in Net_S:
            annual_list.append(
                results_dict[scenario.name][year]['Net_S'][location.name][for_what.name][result_metric])

        elif result_metric in Sch_P:
            day_list = [day for day in results_dict[scenario.name]
                        [year]['Sch_P'][location.name][for_what.name].keys()]
            hour_list = [hour for hour in results_dict[scenario.name]
                         [year]['Sch_P'][location.name][for_what.name][1].keys()]
            for day, hour in product(day_list, hour_list):
                annual_list.append(results_dict[scenario.name][year]['Sch_P']
                                   [location.name][for_what.name][day][hour][result_metric])

        elif result_metric in Sch_S:
            day_list = [day for day in results_dict[scenario.name]
                        [0]['Sch_S'][location.name][for_what.name].keys()]
            hour_list = [hour for hour in results_dict[scenario.name]
                         [0]['Sch_S'][location.name][for_what.name][1].keys()]
            for day, hour in product(day_list, hour_list):
                annual_list.append(results_dict[scenario.name][year]['Sch_S']
                                   [location.name][for_what.name][day][hour][result_metric])

    return annual_list

# =================================================================================================================
# *                                         CONSTRAINTS
# =================================================================================================================


def nameplate_production_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                                    processes: pyomo.core.base.set.OrderedSimpleSet, hours: pyomo.core.base.set.OrderedSimpleSet, days: pyomo.core.base.set.OrderedSimpleSet,
                                    years: pyomo.core.base.set.OrderedSimpleSet, f_conv_dict: dict, rep_days_dict: dict) -> pyomo.core.base.constraint.IndexedConstraint:
    """Bounds hourly production nameplate production capacity based on varying production factors

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        hours (pyomo.core.base.set.OrderedSimpleSet): set of hours
        days (pyomo.core.base.set.OrderedSimpleSet): set of days
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        f_conv_dict (dict): varying process conversion factors
        rep_days_dict (dict): set of representative days

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: nameplate production capacity constraint
    """

    def nameplate_production_rule(instance, location, process, hour, day, year):
        return instance.P[location, process, hour, day, year] <= instance.Cap_P[location, process, year]*f_conv_dict[location][process][rep_days_dict[day]['rep_day']][hour]
    instance.nameplate_production_constraint = Constraint(
        locations, processes, hours, days, years, rule=nameplate_production_rule, doc='nameplate production capacity constraint')
    eqn_latex_render(nameplate_production_rule)
    return instance.nameplate_production_constraint


def nameplate_inventory_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                                   resources: pyomo.core.base.set.OrderedSimpleSet, hours: pyomo.core.base.set.OrderedSimpleSet, days: pyomo.core.base.set.OrderedSimpleSet,
                                   years: pyomo.core.base.set.OrderedSimpleSet, storable_resources: pyomo.core.base.set.OrderedSimpleSet) -> pyomo.core.base.constraint.IndexedConstraint:
    """Bounds inventory levels to nameplate inventory capacity

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        resources (pyomo.core.base.set.OrderedSimpleSet): set of resources
        hours (pyomo.core.base.set.OrderedSimpleSet): set of hours
        days (pyomo.core.base.set.OrderedSimpleSet): set of days
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        storable_resources (pyomo.core.base.set.OrderedSimpleSet): set of storable resources
        rep_days_dict (pyomo.core.base.set.OrderedSimpleSet): representative days


    Returns:
        pyomo.core.base.constraint.IndexedConstraint: nameplate inventory capacity constraint
    """

    def nameplate_inventory_rule(instance, location, resource, hour, day, year):
        if resource in instance.resource_store:
            return instance.Inv[location, resource, hour, day, year] <= instance.Cap_S[location, resource, year]
        else:
            return instance.Inv[location, resource, hour, day, year] <= 0
    instance.nameplate_inventory_constraint = Constraint(
        locations, resources, hours, days, years, rule=nameplate_inventory_rule, doc='nameplate inventory capacity constraint')

    return instance.nameplate_inventory_constraint


def resource_consumption_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                                    resources: pyomo.core.base.set.OrderedSimpleSet, hours: pyomo.core.base.set.OrderedSimpleSet, days: pyomo.core.base.set.OrderedSimpleSet,
                                    years: pyomo.core.base.set.OrderedSimpleSet, resource_list: list) -> pyomo.core.base.constraint.IndexedConstraint:
    """Bounds consumption to resource consumption on an hourly basis #TBF : avoid needing the resource list to be pulled in

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        resources (pyomo.core.base.set.OrderedSimpleSet): set of resources
        hours (pyomo.core.base.set.OrderedSimpleSet): set of hours
        days (pyomo.core.base.set.OrderedSimpleSet): set of days
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        resource_list (pyomo.core.base.set.OrderedSimpleSet): list of energia resource objects

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: resource consumption constraint
    """

    def resource_consumption_rule(instance, location, resource, hour, day, year):
        return instance.C[location, resource, hour, day, year] <= next((resource_.consumption_max for resource_ in resource_list if resource_.name == resource))
    instance.resource_consumption_constraint = Constraint(
        instance.locations, instance.resources, instance.hours, instance.days, instance.years, rule=resource_consumption_rule, doc='resource consumption')
    return instance.resource_consumption_constraint


def resource_expenditure_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                                    resources: pyomo.core.base.set.OrderedSimpleSet, hours: pyomo.core.base.set.OrderedSimpleSet, days: pyomo.core.base.set.OrderedSimpleSet,
                                    years: pyomo.core.base.set.OrderedSimpleSet, f_purchase_dict: dict, rep_days_dict: dict, resource_list: list) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates the expenditure on resource purchase

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        resources (pyomo.core.base.set.OrderedSimpleSet): set of resources
        hours (pyomo.core.base.set.OrderedSimpleSet): set of hours
        days (pyomo.core.base.set.OrderedSimpleSet): set of days
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        f_purchase_dict (dict): varying purchase cost factors
        rep_days_dict (dict): representative days
        resource_list (list): list of energia resource objects

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: resource expenditure constraint
    """
    def resource_expenditure_rule(instance, location, resource, hour, day, year):
        return instance.B[location, resource, hour, day, year] == f_purchase_dict[location][resource][rep_days_dict[day]['rep_day']][hour] *\
            next((resource_.price for resource_ in resource_list if resource_.name ==
                 resource))*instance.C[location, resource, hour, day, year]
    instance.resource_expenditure_constraint = Constraint(instance.locations, instance.resources, instance.hours,
                                                          instance.days, instance.years, rule=resource_expenditure_rule, doc='expenditure on purchase of resource')
    return instance.resource_expenditure_constraint


def inventory_balance_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet, transports: pyomo.core.base.set.OrderedSimpleSet,
                                 resources: pyomo.core.base.set.OrderedSimpleSet, hours: pyomo.core.base.set.OrderedSimpleSet, days: pyomo.core.base.set.OrderedSimpleSet,
                                 years: pyomo.core.base.set.OrderedSimpleSet, horizon: pyomo.core.base.set.OrderedSimpleSet, conversion_dict: dict, rep_days_dict: dict,
                                 resource_list: list, results_dict: dict, cost_scenario: cost_scenario) -> pyomo.core.base.constraint.IndexedConstraint:
    """Balances and cycles the inventory for all resources 

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        transports (pyomo.core.base.set.OrderedSimpleSet): set of transport modes
        resources (pyomo.core.base.set.OrderedSimpleSet): set of resources
        hours (pyomo.core.base.set.OrderedSimpleSet): set of hours
        days (pyomo.core.base.set.OrderedSimpleSet): set of days
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        horizon (pyomo.core.base.set.OrderedSimpleSet): planning horizon
        conversion_dict (dict): conversion parameters
        rep_days_dict (dict): representative days
        resource_list (list): list of energia resource objects
        results_dict (dict): results dictionary, need to cycle inventory from previous year in the planning horizon
        cost_scenario (cost_scenario): current scenario in consideration

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: inventory balance constraint
    """
    location_list = [i for i in instance.locations]
    transport_list = [i for i in instance.transports]

    def inventory_balance_rule(instance, location, resource, hour, day, year):
        if (hour == instance.hours.data()[0]) and (day == instance.days.data()[0]) and (instance.years.data()[0] == instance.horizon.data()[0]):
            return instance.Inv[location, resource, hour, day, year] == \
                rep_days_dict[day]['cluster_wt']*(sum(conversion_dict[year][process][resource]*instance.P[location, process, hour, day, year] for process in instance.processes)
                                                  + instance.C[location, resource, hour, day, year] - instance.S[location, resource, hour, day, year]) \
                                                      + sum(sum(instance.Trans_in[location, location_ , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
                                                          - sum(sum(instance.Trans_in[location_, location , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
                                                          
        elif (hour == instance.hours.data()[0]) and (day == instance.days.data()[0]) and (instance.years.data()[0] > instance.horizon.data()[0]):
            return instance.Inv[location, resource, hour, day, year] - (1 - next((resource_.loss for resource_ in resource_list if resource_.name == resource)))*results_dict[cost_scenario.name][instance.years.data()[0]- 1]['Sch_S'][location][resource][instance.days.data()[-1]][instance.hours.data()[-1]]['Inv']\
                == rep_days_dict[day]['cluster_wt']*(sum(conversion_dict[year][process][resource]*instance.P[location, process, hour, day, year] for process in instance.processes)
                                                     + instance.C[location, resource, hour, day, year] - instance.S[location, resource, hour, day, year])\
                                                         + sum(sum(instance.Trans_in[location, location_ , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
                                                          - sum(sum(instance.Trans_in[location_, location , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
                                                          

        elif (day > instance.days.data()[0]) and (hour == instance.hours.data()[0]):
            return instance.Inv[location, resource, hour, day, year] - (1 - next((resource_.loss for resource_ in resource_list if resource_.name == resource)))*instance.Inv[location, resource, instance.hours.data()[-1], day-1, year]\
                == rep_days_dict[day]['cluster_wt']*(sum(conversion_dict[year][process][resource]*instance.P[location, process, hour, day, year] for process in instance.processes)
                                                     + instance.C[location, resource, hour, day, year] - instance.S[location, resource, hour, day, year])\
                                                         + sum(sum(instance.Trans_in[location, location_ , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
                                                          - sum(sum(instance.Trans_in[location_, location , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
                                                          

        else:
            return instance.Inv[location, resource, hour, day, year] - (1 - next((resource_.loss for resource_ in resource_list if resource_.name == resource)))*instance.Inv[location, resource, hour-1, day, year] \
                == rep_days_dict[day]['cluster_wt']*(sum(conversion_dict[year][process][resource]*instance.P[location, process, hour, day, year] for process in instance.processes)
                                                     + instance.C[location, resource, hour, day, year] - instance.S[location, resource, hour, day, year])\
                                                         + sum(sum(instance.Trans_in[location, location_ , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
                                                          - sum(sum(instance.Trans_in[location_, location , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
                                                          
    instance.inventory_balance_constraint = Constraint(instance.locations, instance.resources, instance.hours, instance.days,
                                                       instance.years, rule=inventory_balance_rule, doc='balances and cycles inventory between consecutive periods')
    # if resource in ['Charge']:
    #     print(instance.inventory_balance_constraint)
    return instance.inventory_balance_constraint


def discharge_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                         resources: pyomo.core.base.set.OrderedSimpleSet, hours: pyomo.core.base.set.OrderedSimpleSet, days: pyomo.core.base.set.OrderedSimpleSet,
                         years: pyomo.core.base.set.OrderedSimpleSet, resource_nosell: pyomo.core.base.set.OrderedSimpleSet) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates the expenditure on resource purchase

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        resources (pyomo.core.base.set.OrderedSimpleSet): set of resources
        hours (pyomo.core.base.set.OrderedSimpleSet): set of hours
        days (pyomo.core.base.set.OrderedSimpleSet): set of days
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        resource_nosell (pyomo.core.base.set.OrderedSimpleSet): set of resources which cannot be discharged

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: discharge constraint
    """
    def discharge_rule(instance, location, resource, hour, day, year):
        if resource in instance.resource_nosell:
            return instance.S[location, resource, hour, day, year] == 0
    instance.discharge_cons = Constraint(instance.locations, instance.resource_nosell, instance.hours,
                                         instance.days, instance.years, rule=discharge_rule, doc='restrict discharge of non marketable resources')
    return instance.discharge_cons


def annual_discharge_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                                resources: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet, rep_days_dict: dict) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates annual discharge of each resource

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        resources (pyomo.core.base.set.OrderedSimpleSet): set of resources
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        rep_days_dict (dict): representative days

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: annual discharge constraint
    """

    def annual_discahrge_rule(instance, location, resource, year):
        return instance.S_annual[location, resource, year] == sum(rep_days_dict[day]['cluster_wt']*sum(instance.S[location, resource, hour, day, year] for hour in instance.hours) for day in instance.days)
    instance.annual_discahrge_constraint = Constraint(
        instance.locations, instance.resources, instance.years, rule=annual_discahrge_rule, doc='annual sale of each resource')
    return instance.annual_discahrge_constraint


def annual_consumption_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                                  resources: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet, rep_days_dict: dict) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates annual consumption of each resource

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        resources (pyomo.core.base.set.OrderedSimpleSet): set of resources
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        rep_days_dict (dict): representative days

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: annual consumption constraint
    """

    def annual_consumption_rule(instance, location, resource, year):
        return instance.C_annual[location, resource, year] == sum(rep_days_dict[day]['cluster_wt']*sum(instance.C[location, resource, hour, day, year] for hour in instance.hours) for day in instance.days)
    instance.annual_consumption_constraint = Constraint(
        instance.locations, instance.resources, instance.years, rule=annual_consumption_rule, doc='annual purchase of each resource')
    return instance.annual_consumption_constraint


def annual_resource_expenditure_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                                           resources: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet, rep_days_dict: dict) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates annual consumption of each resource

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        resources (pyomo.core.base.set.OrderedSimpleSet): set of resources
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        rep_days_dict (dict): representative days

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: annual resource expenditure constraint
    """
    def annual_resource_expenditure_rule(instance, location, resource, year):
        return instance.B_annual[location, resource, year] == sum(rep_days_dict[day]['cluster_wt']*sum(instance.B[location, resource, hour, day, year] for hour in instance.hours) for day in instance.days)
    instance.annual_resource_expenditure_constraint = Constraint(
        instance.locations, instance.resources, instance.years, rule=annual_resource_expenditure_rule, doc='annual expenditure on purchase of each resource')
    return instance.annual_resource_expenditure_constraint


def annual_production_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                                 processes: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet, rep_days_dict: dict) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates annual production by each process on nominal basis

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        rep_days_dict (dict): representative days

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: annual production constraint
    """

    def annual_production_rule(instance, location, process, year):
        return instance.P_annual[location, process, year] == sum(rep_days_dict[day]['cluster_wt']*sum(instance.P[location, process, hour, day, year] for hour in instance.hours) for day in instance.days)
    instance.annual_production_constraint = Constraint(instance.locations, instance.processes, instance.years,
                                                       rule=annual_production_rule, doc='annual production utilization of each facility on nominal resource basis')
    return instance.annual_production_constraint


def annual_mileage_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                              resources: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet, resource_list: list) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates annual mileage from each 

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        resources (pyomo.core.base.set.OrderedSimpleSet): set of resources
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        resource_list (list): list of resource objects

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: annual mileage constraint
    """

    def annual_mileage_rule(instance, location, resource, year):
        return instance.Mile_annual[location, resource, year] == next((resource_.mile for resource_ in resource_list if resource_.name == resource))*instance.S_annual[location, resource, year]
    instance.annual_mileage_constraint = Constraint(
        instance.locations, instance.resources, instance.years, rule=annual_mileage_rule, doc='annual mileage from fuel resource')
    return instance.annual_mileage_constraint

    # # ======================= COSTING FUNCTIONS ==================================


def capex_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                     processes: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet, cost_dict: dict, cost_scenario: cost_scenario,
                     annualization_factor: float) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates the capital expenditure for each process

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        cost_dict (dict): costing values under defined cost scenarios
        cost_scenario (cost_scenario): scenario under consideration
        annualization_factor (float): annualize results as a percentage

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: capex constraint
    """

    def capex_rule(instance, location, process, year):
        return instance.Capex[location, process, year] == annualization_factor*cost_dict[location][cost_scenario.name][process][year]['CAPEX']*instance.Cap_P[location, process, year]
    instance.capex_constraint = Constraint(instance.locations, instance.processes,
                                           instance.years, rule=capex_rule, doc='capital expenditure for each process')
    return instance.capex_constraint


def fixed_opex_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                          processes: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet, cost_dict: dict, cost_scenario: cost_scenario) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates the capital expenditure for each process

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        cost_dict (dict): costing values under defined cost scenarios
        cost_scenario (cost_scenario): scenario under consideration

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: fixed opex constraint
    """

    def fixed_opex_rule(instance, location, process, year):
        return instance.Opex_fix[location, process, year] == cost_dict[location][cost_scenario.name][process][year]['Fixed O&M']*instance.Cap_P[location, process, year]
    instance.fixed_opex_constraint = Constraint(
        instance.locations, instance.processes, instance.years, rule=fixed_opex_rule, doc='fixed operational expenditure for each process')
    return instance.fixed_opex_constraint


def variable_opex_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                             processes: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet, cost_dict: dict, cost_scenario: cost_scenario) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates the capital expenditure for each process

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        cost_dict (dict): costing values under defined cost scenarios
        cost_scenario (cost_scenario): scenario under consideration

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: variable opex constraint
    """

    def variable_opex_rule(instance, location, process, year):
        return instance.Opex_var[location, process, year] == cost_dict[location][cost_scenario.name][process][year]['Variable O&M']*instance.P_annual[location, process, year]
    instance.variable_opex_constraint = Constraint(
        instance.locations, instance.processes, instance.years, rule=variable_opex_rule, doc='variable operational expenditure for each process')
    return instance.variable_opex_constraint


def opex_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                    processes: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates the capital expenditure for each process

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        years (pyomo.core.base.set.OrderedSimpleSet): set of years

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: opex constraint
    """

    def opex_rule(instance, location, process, year):
        return instance.Opex[location, process, year] == instance.Opex_var[location, process, year] + instance.Opex_fix[location, process, year]
    instance.opex_constraint = Constraint(instance.locations, instance.processes, instance.years,
                                          rule=opex_rule, doc='operational expenditure (fix + var) for each process')
    return instance.opex_constraint


def capex_total_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                           processes: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates the total capital expenditure at a location

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        years (pyomo.core.base.set.OrderedSimpleSet): set of years

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: capex total constraint
    """

    def capex_total_rule(instance, location, year):
        return instance.Capex_total[location, year] == sum(instance.Capex[location, process, year] for process in instance.processes)
    instance.capex_total_constraint = Constraint(
        instance.locations, instance.years, rule=capex_total_rule, doc='Total capital expenditure')
    return instance.capex_total_constraint


def variable_opex_total_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                                   processes: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates the total capital expenditure at a location

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        years (pyomo.core.base.set.OrderedSimpleSet): set of years

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: variable opex total constraint
    """

    def variable_opex_total_rule(instance, location, year):
        return instance.Opex_var_total[location, year] == sum(instance.Opex_var[location, process, year] for process in instance.processes)
    instance.variable_opex_total_constraint = Constraint(
        instance.locations, instance.years, rule=variable_opex_total_rule, doc='Total variable operational expenditure')
    return instance.variable_opex_total_constraint


def fixed_opex_total_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                                processes: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates the total capital expenditure at a location

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        years (pyomo.core.base.set.OrderedSimpleSet): set of years

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: fixed opex total constraint
    """

    def fixed_opex_total_rule(instance, location, year):
        return instance.Opex_fix_total[location, year] == sum(instance.Opex_fix[location, process, year] for process in instance.processes)
    instance.fixed_opex_total_constraint = Constraint(
        instance.locations, instance.years, rule=fixed_opex_total_rule, doc='Total fixed operational expenditure')
    return instance.fixed_opex_total_constraint


def opex_total_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates the total capital expenditure at a location

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        years (pyomo.core.base.set.OrderedSimpleSet): set of years

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: opex total constraint
    """

    def opex_total_rule(instance, location, year):
        return instance.Opex_total[location, year] == instance.Opex_var_total[location, year] + instance.Opex_fix_total[location, year]
    instance.opex_total_constraint = Constraint(
        instance.locations, instance.years, rule=opex_total_rule, doc='Total operational expenditure (fix + var)')
    return instance.opex_total_constraint


def resource_expenditure_total_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                                          resources: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates total resource expenditure

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        resources (pyomo.core.base.set.OrderedSimpleSet): set of resources
        years (pyomo.core.base.set.OrderedSimpleSet): set of years

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: total resource expenditure constraint
    """

    def resource_expenditure_total_rule(instance, location, year):
        return instance.B_total[location, year] == sum(instance.B_annual[location, resource, year] for resource in instance.resources)
    instance.resource_expenditure_total_constraint = Constraint(
        instance.locations, instance.years, rule=resource_expenditure_total_rule, doc='Total expenditure on resource purchase')
    return resource_expenditure_total_constraint


def mileage_total_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                             resources: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates total mileage constraint

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        resources (pyomo.core.base.set.OrderedSimpleSet): set of resources
        years (pyomo.core.base.set.OrderedSimpleSet): set of years

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: total mileage constraint
    """

    def mileage_total_rule(instance, location, year):
        return instance.Mile_total[location, year] == sum(instance.Mile_annual[location, resource, year] for resource in instance.resources)
    instance.mileage_total_constraint = Constraint(
        instance.locations, instance.years, rule=mileage_total_rule, doc='Total miles')
    return instance.mileage_total_constraint


def gwp_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                   processes: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet, process_list: list,
                   annualization_factor: float) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates global warming potential for each process

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        process_list (list): list of energia process objects
        annualization_factor (float): annualize results as a percentage


    Returns:
        pyomo.core.base.constraint.IndexedConstraint: global warming potential constraint
    """

    def gwp_rule(instance, location, process, year):
        return instance.GWP[location, process, year] == annualization_factor*next((process_.gwp for process_ in process_list if process_.name == process))*instance.Cap_P[location, process, year]
    instance.gwp_constraint = Constraint(
        instance.locations, instance.processes, instance.years, rule=gwp_rule, doc='GWP of each process')
    return instance.gwp_constraint


def land_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                    processes: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet, process_list: list) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates land use for each process

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        process_list (list): list of energia process objects

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: global warming potential constraint
    """

    def land_rule(instance, location, process, year):
        return instance.Land[location, process, year] == next((process_.land for process_ in process_list if process_.name == process))*instance.Cap_P[location, process, year]
    instance.land_constraint = Constraint(
        instance.locations, instance.processes, instance.years, rule=land_rule, doc='Land use for each process')
    return instance.land_constraint


def gwp_total_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                         processes: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates total global warming potential at location

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        years (pyomo.core.base.set.OrderedSimpleSet): set of years

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: total global warming potential constraint
    """

    def gwp_total_rule(instance, location, year):
        return instance.GWP_total[location, year] == sum(instance.GWP[location, process, year] for process in instance.processes)
    instance.gwp_total_constraint = Constraint(
        instance.locations, instance.years, rule=gwp_total_rule, doc='Total GWP')
    return instance.gwp_total_constraint


def land_total_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                          processes: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates total land use at location

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        years (pyomo.core.base.set.OrderedSimpleSet): set of years

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: total global warming potential constraint
    """
    def land_total_rule(instance, location, year):
        return instance.Land_total[location, year] == sum(instance.Land[location, process, year] for process in instance.processes)
    instance.land_total_constraint = Constraint(
        instance.locations, instance.years, rule=land_total_rule, doc='Total land use')
    return instance.land_total_constraint


def credit_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                      process_45Q: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet, tax_credit_dict: dict) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates tax credits earned from processes in a location

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        process_45Q (pyomo.core.base.set.OrderedSimpleSet): set of processes that earn tax credits
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        tax_credit_dict (dict): tax credits under different periods

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: tax credit constraint
    """

    def credit_rule(instance, location, process, year):
        if instance.years.data()[0] <= 5:
            period_ = 1
        else:
            period_ = 2
        # TBF
        return instance.Credit[location, process, year] == tax_credit_dict[period_][process]*instance.P_annual[location, process, year]
    instance.credit_constraint = Constraint(instance.locations, instance.process_45Q,
                                            instance.years, rule=credit_rule, doc='Tax credit recieved through 45Q for each process')
    return instance.credit_constraint


def credit_total_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                            process_45Q: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet) -> pyomo.core.base.constraint.IndexedConstraint:
    """calculates total tax credits earned from processes in a location

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        process_45Q (pyomo.core.base.set.OrderedSimpleSet): set of processes that earn tax credits
        years (pyomo.core.base.set.OrderedSimpleSet): set of years

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: total tax credit constraint
    """

    def credit_total_rule(instance, location, year):
        return instance.Credit_total[location, year] == sum(instance.Credit[location, process, year] for process in instance.process_45Q)
    instance.credit_total_constraint = Constraint(
        instance.locations, instance.years, rule=credit_total_rule, doc='Total tax credit recieved through 45Q')
    return instance.credit_total_constraint


def material_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                        materials: pyomo.core.base.set.OrderedSimpleSet, processes: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet, material_dict: dict, annualization_factor: float) -> pyomo.core.base.constraint.IndexedConstraint:
    """materials consumed by process on an annual basis 

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        materials (pyomo.core.base.set.OrderedSimpleSet): set of materials
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processeses
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        material_dict (dict): material requirements for processes
        annualization_factor (float): annualize results as a percentage

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: material constraint
    """

    def material_rule(instance, location, process, material, year):
        return instance.Material[location, process, material, year] == annualization_factor*material_dict[process][material]*instance.Cap_P[location, process, year]
    instance.material_constraint = Constraint(instance.locations, instance.processes, instance.materials,
                                              instance.years, rule=material_rule, doc='Material use for each process')
    return instance.material_constraint


def material_total_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet,
                              materials: pyomo.core.base.set.OrderedSimpleSet, processes: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet) -> pyomo.core.base.constraint.IndexedConstraint:
    """total materials consumed at a location 

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        materials (pyomo.core.base.set.OrderedSimpleSet): set of materials
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processeses
        years (pyomo.core.base.set.OrderedSimpleSet): set of years

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: total material constraint
    """

    def material_total_rule(instance, location, material, year):
        return instance.Material_total[location, material, year] == sum(instance.Material[location, process, material, year] for process in instance.processes)
    instance.material_total_cons = Constraint(
        instance.locations, instance.materials, instance.years, rule=material_total_rule, doc='Material use for each process')
    return instance.material_total_cons


def co2_total_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet,
                         co2_emmitted: resource) -> pyomo.core.base.constraint.IndexedConstraint:
    """Total CO2 emissions at a location 

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        CO2_Vent (resource): Resource object defined for vented carbon dioxide

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: CO2 emission constraint
    """
    def co2_total_rule(instance, location, year):

        return instance.CO2_total[location, year] == instance.S_annual[location, co2_emmitted.name, year] + instance.GWP_total[location, year]
    instance.co2_total_cons = Constraint(
        instance.locations, instance.years, rule=co2_total_rule, doc='Total CO2-eq emitted')
    return instance.co2_total_cons


def daily_demand_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet, demand_list: pyomo.core.base.set.OrderedSimpleSet,
                            hours: pyomo.core.base.set.OrderedSimpleSet, days: pyomo.core.base.set.OrderedSimpleSet, years: pyomo.core.base.set.OrderedSimpleSet, demand_dict: dict) -> pyomo.core.base.constraint.IndexedConstraint:
    """Meets the daily resource demands for a set of processes

    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        demand_list (pyomo.core.base.set.OrderedSimpleSet): set of resources with set demand (tons/day) 
        hours (pyomo.core.base.set.OrderedSimpleSet): set of hours
        days (pyomo.core.base.set.OrderedSimpleSet): set of days
        years (pyomo.core.base.set.OrderedSimpleSet): set of years
        demand_dict (dict): demand values to be met over the year 

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: CO2 emission constraint
    """
    location_list = [i for i in instance.locations]
    def daily_demand_rule(instance, location, day, year):  # TBF , will be good to try demands embedded as a list in the resource object, try generalizing units !
        return sum(sum(instance.S[location, resource, hour, day, year] for resource in instance.demand_list) for hour in instance.hours) == demand_dict[location][instance.years.data()[0]]*907.185
    instance.daily_demand_constraint = Constraint(
        instance.locations, instance.days, instance.years, rule=daily_demand_rule, doc='meet daily demand')
    print('Meeting a daily demand in year ' + str(2022 + instance.years.data()[0]) + ' of:')
    for location_ in location_list:
        print(str(demand_dict[location_][0]) + ' US ton/day [' + str("{:.2f}".format(
                demand_dict[location_][0]*907.185/24)) + ' kgs/h] in the year in location ' + location_) 
    
    return instance.daily_demand_constraint


def nameplate_production_LB_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet, processes: pyomo.core.base.set.OrderedSimpleSet,
                                       years: pyomo.core.base.set.OrderedSimpleSet, cost_scenario: cost_scenario, results_dict: dict, process_list: list) -> pyomo.core.base.constraint.IndexedConstraint:
    """Ensures that production capacity over the planning horizon is not depreciated.
    Prevents loss of invested capital and ensures continuity
    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        cost_scenario (cost_scenario): cost scenario object
        results_dict (dict): results dictionary, need to cycle inventory from previous year in the planning horizon
        process_list (list): list of processes

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: nameplate production capacity lower bound constraint
    """
    def nameplate_production_LB_rule(instance, location, process, year):
        if instance.years.data()[0] > 0:
            return instance.Cap_P[location, process, year] - results_dict[cost_scenario.name][instance.years.data()[0] - 1]['Net_P'][location][process]['Cap_P'] \
                >= next(process_.prod_min for process_ in process_list if process_.name == process)*instance.X_P[location, process, year]
        else:
            return instance.Cap_P[location, process, year] >= next(process_.prod_min for process_ in process_list if process_.name == process)*instance.X_P[location, process, year]
    instance.nameplate_production_LB_constraint = Constraint(
        instance.locations, instance.processes, instance.years, rule=nameplate_production_LB_rule, doc='nameplate production capacity lower bound')
    return instance.nameplate_production_LB_constraint


def nameplate_production_UB_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet, processes: pyomo.core.base.set.OrderedSimpleSet,
                                       years: pyomo.core.base.set.OrderedSimpleSet, cost_scenario: cost_scenario, results_dict: dict, process_list: list) -> pyomo.core.base.constraint.IndexedConstraint:
    """Ensures that production capacity over the planning horizon is does not increase over a stated value
    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        processes (pyomo.core.base.set.OrderedSimpleSet): set of processes
        cost_scenario (cost_scenario): cost scenario object
        results_dict (dict): results dictionary, need to cycle inventory from previous year in the planning horizon
        process_list (list): list of processes

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: nameplate production capacity upper bound constraint
    """
    def nameplate_production_UB_rule(instance, location, process, year):
        if instance.years.data()[0] > 0:
            return instance.Cap_P[location, process, year] - results_dict[cost_scenario.name][instance.years.data()[0] - 1]['Net_P'][location][process]['Cap_P'] \
                <= next(process_.prod_max for process_ in process_list if process_.name == process)*instance.X_P[location, process, year]
        else:
            return instance.Cap_P[location, process, year] <= next(process_.prod_max for process_ in process_list if process_.name == process)*instance.X_P[location, process, year]
    instance.nameplate_production_UB_constraint = Constraint(
        instance.locations, instance.processes, instance.years, rule=nameplate_production_UB_rule, doc='nameplate production capacity upper bound')
    return instance.nameplate_production_UB_constraint


def nameplate_inventory_LB_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet, resource_store: pyomo.core.base.set.OrderedSimpleSet,
                                      years: pyomo.core.base.set.OrderedSimpleSet, cost_scenario: cost_scenario, results_dict: dict, resource_list: list) -> pyomo.core.base.constraint.IndexedConstraint:
    """Ensures that storage capacity over the planning horizon is not depreciated.
    Prevents loss of invested capital and ensures continuity
    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        resources (pyomo.core.base.set.OrderedSimpleSet): set of resources that can be stored
        cost_scenario (cost_scenario): cost scenario object
        results_dict (dict): results dictionary, need to cycle inventory from previous year in the planning horizon
        resource_list (list): list of resources

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: nameplate storage capacity lower bound constraint
    """
    def nameplate_inventory_LB_rule(instance, location, resource, year):
        if instance.years.data()[0] > 0:
            return instance.Cap_S[location, resource, year] - results_dict[cost_scenario.name][instance.years.data()[0] - 1]['Net_S'][location][resource]['Cap_S'] \
                >= next(resource_.store_min for resource_ in resource_list if resource_.name == resource)*instance.X_S[location, resource, year]
        else:
            return instance.Cap_S[location, resource, year] >= next(resource_.store_min for resource_ in resource_list if resource_.name == resource)*instance.X_S[location, resource, year]
    instance.nameplate_inventory_LB_constraint = Constraint(
        instance.locations, instance.resource_store, instance.years, rule=nameplate_inventory_LB_rule, doc='nameplate storage capacity lower bound')
    return instance.nameplate_inventory_LB_constraint


def nameplate_inventory_UB_constraint(instance: pyomo.core.base.PyomoModel.ConcreteModel, locations: pyomo.core.base.set.OrderedSimpleSet, resource_store: pyomo.core.base.set.OrderedSimpleSet,
                                      years: pyomo.core.base.set.OrderedSimpleSet, cost_scenario: cost_scenario, results_dict: dict, resource_list: list) -> pyomo.core.base.constraint.IndexedConstraint:
    """Ensures that storage capacity over the planning horizon is does not increase over a stated value
    Args:
        instance (pyomo.core.base.PyomoModel.ConcreteModel): model instance
        locations (pyomo.core.base.set.OrderedSimpleSet): set of locations
        resources (pyomo.core.base.set.OrderedSimpleSet): set of resources that can be stored
        cost_scenario (cost_scenario): cost scenario object
        results_dict (dict): results dictionary, need to cycle inventory from previous year in the planning horizon
        resource_list (list): list of resources

    Returns:
        pyomo.core.base.constraint.IndexedConstraint: nameplate storage capacity upper bound constraint
    """
    def nameplate_inventory_UB_rule(instance, location, resource, year):
        if instance.years.data()[0] > 0:
            return instance.Cap_S[location, resource, year] - results_dict[cost_scenario.name][instance.years.data()[0] - 1]['Net_S'][location][resource]['Cap_S'] \
                <= next(resource_.store_max for resource_ in resource_list if resource_.name == resource)*instance.X_S[location, resource, year]
        else:
            return instance.Cap_S[location, resource, year] <= next(resource_.store_max for resource_ in resource_list if resource_.name == resource)*instance.X_S[location, resource, year]
    instance.nameplate_inventory_UB_constraint = Constraint(
        instance.locations, instance.resource_store, instance.years, rule=nameplate_inventory_UB_rule, doc='nameplate storage capacity upper bound')
    return instance.nameplate_inventory_UB_constraint


def power_efficiency_curve(conversion_dict: dict, process_list: list, resource_list: list, year_list: list) -> dict:
    """Augments power efficiency over the planning horizon based on technology readiness level (TRL)
    Args:
        conversion_dict (dict): original conversion dict for base year
        process_list (list): list of processes 
        resource_list (list): list of resources
        year_list (list): planning horizon

    Returns:
        dict: augmented conversion dictionary with increasing power efficiencies over planning horizon 
    """
    conversion_dict2 = {year: {process.name: {resource.name: {
    } for resource in resource_list} for process in process_list} for year in year_list}
    for year in year_list:
        for process, process_ in product(conversion_dict.keys(), process_list):
            if process == process_.name:
                for resource in conversion_dict[process].keys():
                    if conversion_dict[process][resource] < 0:
                        if resource == 'Power':
                            if process_.trl == 'pilot':
                                if year == 0:
                                    conversion_dict2[year][process][resource] = conversion_dict[process][resource]
                                elif year > 0 and year < 20:
                                    conversion_dict2[year][process][resource] = conversion_dict2[year -
                                                                                                 1][process][resource]*0.99
                                else:
                                    conversion_dict2[year][process][resource] = conversion_dict2[year -
                                                                                                 1][process][resource]*0.985
                            elif process_.trl == 'utility':
                                if year == 0:
                                    conversion_dict2[year][process][resource] = conversion_dict[process][resource]
                                elif year > 0 and year < 15:
                                    conversion_dict2[year][process][resource] = conversion_dict2[year -
                                                                                                 1][process][resource]*0.985
                                else:
                                    conversion_dict2[year][process][resource] = conversion_dict2[year -
                                                                                                 1][process][resource]*0.9999
                            elif process_.trl == 'nrel':
                                if year == 0:
                                    conversion_dict2[year][process][resource] = conversion_dict[process][resource]
                                elif year > 0 and year < 15:
                                    conversion_dict2[year][process][resource] = conversion_dict2[year -
                                                                                                 1][process][resource]*0.985
                                else:
                                    conversion_dict2[year][process][resource] = conversion_dict2[year -
                                                                                                 1][process][resource]*0.9999
                            else:
                                conversion_dict2[year][process][resource] = conversion_dict[process][resource]
                        else:
                            conversion_dict2[year][process][resource] = conversion_dict[process][resource]
                    else:
                        conversion_dict2[year][process][resource] = conversion_dict[process][resource]
    return conversion_dict2

def eqn_latex_render(constraint_rule, latex_alias_dict:dict= {}) -> str:
    """renders a string for equation in latex format

    Args:
        constraint_rule (function, optional): constraint definition rule. Defaults to {}
        latex_alias_dict (dict): aliases for vaiables, sets, and symbols

    Returns:
        str: string in latex format
    """
    general_dict = {
        '**': '^',
        '*': '.',
        '==': '=',
        '<=': '\leq',
        '>=': '\geq',
        '[': '(',
        ']': ')',
        'exp': 'exp',
        'instance.':'',
        }
    
    unsorted_dict_ = {**latex_alias_dict, **general_dict}
    
    
    list_ = [i for i in unsorted_dict_.keys()]
    list_.sort(key = len)
    list_.reverse()

    dict_ = {i: unsorted_dict_[i] for i in list_}
    str_ = inspect.getsource(constraint_rule).split('return ')[1].split('\n')[0]
    for key in dict_.keys():
        str_ = str_.replace(key, dict_[key])
    # str_ = '\begin{equation}'
    ip.display(ip.Math(str_))
    # display(str_)
    
    return str_

#     def Daily_H2Demand_rule(m, location, day, year):
#         return sum(instance.S[location, H2_C.name, hour, day, year] for hour in instance.hours)  >= 0.2*demand_dict[instance.years.data()[0]]*907.185
#     instance.Daily_H2Demand_cons = Constraint(instance.locations, instance.days, instance.years, rule = Daily_H2Demand_rule, doc = 'Ensures > 20pc for local consumption')
#     print('With atleast ' + str(0.2*demand_dict[instance.years.data()[0]]) + ' (US ton/day) available for local consumption')


#     def Daily_Mile_Demand_rule(m, location, day, year):
#         return sum(sum(next((resource_.mile for resource_ in resource_list if resource_.name == resource))*instance.S[location, resource, hour, day, year ] for resource in instance.resource_mile) for hour in hour_list)  == (2 + year_*2)*1000*1.5
#     instance.Daily_Mile_Demand_cons = Constraint(instance.locations, instance.days, instance.years, rule = Daily_Mile_Demand_rule, doc = 'Ensures that daily demand is met')

#     #=============================
#     #OBJECTIVES
#     #=============================

#     def Cost_Total_obresource_rule(m):
#         return sum(sum(instance.Opex_total[location, year ]  + instance.Capex_total[location, year ]  - instance.Credit_total[location, year ]  + instance.B_total[location, year ] for location in instance.locations) for year in instance.years)
#     instance.Obj = Objective(rule = Cost_Total_obresource_rule, sense = minimize, doc = 'minimize total annualized cost')


# %%

    # #If 10% of college station's (51.3 sq miles, 32832 acres) land is allocated every year
    # def Land_res_rule(instance, location, year):
    #     return instance.Land_total[location,year] <= 32832*0.20
    # instance.Land_res_cons = Constraint(instance.locations, instance.years, rule = Land_res_rule, doc = 'Restrict land use')

    # # ======================= MODE BASED ==================================

    # # #MODE BASED PRODUCTION
    # # def ModeBased_Prod_Cap_rule(instance, location, process, u, hour, day, year):
    # #     return instance.P_M[location, process, u, hour, day, year] <= CAP_PROD_M[u][process]*instance.Y_P[location, process, u, hour, day, year]
    # # instance.ModeBased_Prod_Cap_cons = Constraint(instance.locations, instance.processes, instance.U, instance.hours, instance.days, instance.years, rule = ModeBased_Prod_Cap_rule)

    # # def ModeBased_Prod_Bal_rule(instance, location, process, hour, day, year):
    # #     return  instance.P[location, process, hour, day, year ] == sum (instance.P_M[location, process, u, hour, day, year] for u in U)
    # # instance.ModeBased_Prod_Bal_cons = Constraint(instance.locations, instance.processes, instance.hours, instance.days, instance.years, rule = ModeBased_Prod_Bal_rule)

    # # def Mode_Bal_rule(instance, location, process, hour, day, year):
    # #     return sum(instance.Y_P[location, process, u, hour, day, year] for u in U) ==  instance.X_P[location, process, year]
    # # instance.Mode_Bal_cons = Constraint(instance.locations, instance.processes, instance.hours, instance.days, instance.years, rule = Mode_Bal_rule)

# %%
