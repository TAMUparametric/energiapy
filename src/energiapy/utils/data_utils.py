#%%
"""Data management utilities  
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

import pandas 
import numpy
import pickle
import json
from itertools import product
from ..components.location import location


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
            pickle.dump(data, f)
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
    conversion_dict_ = pandas.read_csv(file_name, index_col=0).dropna(
        axis='rows').transpose().to_dict()
    dump_data(conversion_dict_, 'conversion.json')
    return conversion_dict_


def make_material_dict(file_name: str):
    """updates infra_mat.json which contains infrastructaral material needs by facility

    Returns:
        infra_mat_dict_: dictionary with infrastructaral material needs
    """
    material_dict_ = pandas.read_csv(file_name, index_col=0).dropna(
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


def make_f_conv(location_list: list, day_list: list, hour_list: list, process_list: list, varying_process_dict: dict):
    """makes a dictionary of varying conversion factors.
    minimum resolution: hour

    Args:
        location_list (list): list of locations
        day_list (list): list of days/seasons
        hour_list (list): list of hours
        process_list (list): list of processes
        varying_process_dict[location.name] (pandas.DataFrame): dataframe with varying outputs for processes

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


def make_f_purchase(location_list: list, day_list: list, hour_list: list, resource_list: list, varying_resource_df: pandas.DataFrame) -> dict:
    """makes a dictionary for varying resource costs.
    minimum resolution hour|

    Args:
        location_list (list): list of locations
        day_list (list): list of days/seasons
        hour_list (list): list of hours
        process_list (list): list of processes
        varying_resource_df (pandas.DataFrame): dataframe with varying resource costs

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

    # varying_resource_df2_ = pandas.DataFrame(columns = ['day', 'hour', var])

    # for day, hour in product(varying_resource_df['day'], hour_list):
    #     varying_resource_df2_ = varying_resource_df2_.append({'day': day, 'hour': hour, var: varying_resource_df[var][varying_resource_df['day'] == day].values[0] }, ignore_index = True)

    # , varying_resource_df2_

    return f_purchase_dict_


def make_henry_price_df(file_name: str, year: int, stretch: bool) -> pandas.DataFrame:
    """makes a df from Henry Spot Price Index data
    Days with missing data are filled using previous day values
    The costs are converted to $/kg from $/MMBtu using a factor of /22.4

    Args:
        file_name (str): provide csv file with data
        year (int): import data from a particular year
        stretch (bool): if True, streches the timescale from days (365) to hours (8760)


    Returns:
        pandas.DataFrame: data frame with varying natural gas prices
    """

    df_ = pandas.read_csv(file_name, skiprows=5, names=['date', 'CH4'])

    df_[["month", "day", "year"]] = df_['date'].str.split("/", expand=True)
    df_ = df_[df_['year'] == str(year)].astype(
        {"month": int, "day": int, "year": int})
    df_['date'] = pandas.to_datetime(df_['date'])  # , format='%d%b%Y:%H:%M:%S.%f')
    df_['doy'] = df_['date'].dt.dayofyear
    df_ = df_.sort_values(by=['doy'])
    df_ = df_.drop(columns='date').dropna(axis='rows')
    doy_list = [i for i in df_['doy']]

    for i in numpy.arange(1, 366):  # fixes values for weekends and holidays to last active day
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


def make_nrel_cost_df(location: location, nrel_cost_xlsx, pick_nrel_process_list: list, year_list: list, case: str, crpyears: float) -> pandas.DataFrame:
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
        pandas.DataFrame: with nrel costing data for the specified year
    """
    cost_metrics_list = ['CAPEX', 'Fixed O&M', 'Variable O&M', 'units']

    # import nrel atb cost dataset
    nrel_cost_df_ = pandas.read_excel(nrel_cost_xlsx, sheet_name='cost')
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
              year_list: list, cost_parameters: dict, nrel_cost_dict:dict = {}): #: pandas.DataFrame = {}):
    """fills cost_dict with costing data(CAPEX, Variable and Fixed OPEX), nominal basis (units), and source
    data can be user-defined or taken from NREL

    Args:
        cost_dict (dict): contains cost data for processes
        process ([type]): process object
        location_list (list): set of locations
        cost_scenario_list (list): set of scenarios
        cost_parameters (dict): feeds values for cost metrics
        nrel_cost_df (pandas.DataFrame): contains data from NREL ATB
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

# %%
