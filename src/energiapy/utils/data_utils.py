# %%
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
from ..components.location import Location
from ..components.result import Result


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


def make_material_dict(file_name: str) -> dict:
    """updates infra_mat.json which contains infrastructaral material needs by facility

    Args:
        file_name (str):name of file

    Returns:
        dict: dictionary with infrastructaral material needs
    """
    material_dict_ = pandas.read_csv(file_name, index_col=0).dropna(axis='rows').transpose().to_dict()
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

    df = pandas.read_csv(file_name, skiprows=5, names=['date', 'CH4'])

    df[["month", "day", "year"]] = df['date'].str.split("/", expand=True)
    df = df[df['year'] == str(year)].astype(
        {"month": int, "day": int, "year": int})
    # , format='%d%b%Y:%H:%M:%S.%f')
    df['date'] = pandas.to_datetime(df['date'])
    df['doy'] = df['date'].dt.dayofyear
    df = df.sort_values(by=['doy'])
    df = df.drop(columns='date').dropna(axis='rows')
    doy_list = [i for i in df['doy']]

    # fixes values for weekends and holidays to last active day
    for i in numpy.arange(1, 366):
        if i not in doy_list:
            if i == 1:  # onetime fix if first day has no value, takes value from day 2
                df = pandas.concat([df, pandas.DataFrame.from_records([{'CH4': df['CH4'][df['doy'] == 2].values[0],
                                                                        'month': 1, 'day': 1, 'year': year, 'doy': 1}])])
                # df = df.append({'CH4': df['CH4'][df['doy'] == 2].values[0], 'month': 1, 'day': 1, 'year': year, 'doy': 1}, ignore_index=True)
            else:
                df = pandas.concat([df, pandas.DataFrame.from_records([{'CH4': df['CH4'][df['doy'] == i-1].values[0],
                                                                        'month': df['month'][df['doy'] == i-1].values[0], 'day': df['day'][df['doy'] == i-1].values[0],
                                                                        'year': df['year'][df['doy'] == i-1].values[0], 'doy': i}])])
                # df = df.append({'CH4': df['CH4'][df['doy'] == i-1].values[0], 'month': df['month'][df['doy'] == i-1].values[0], 'day': df['day'][df['doy'] == i-1].values[0], 'year': df['year'][df['doy'] == i-1].values[0], 'doy': i}, ignore_index=True)

    df = df.sort_values(by=['doy'])
    df = df.reset_index(drop=True)
    df['CH4'] = df['CH4'] / 22.4  # convert from $/MMBtu to $/kg
    df = df[['CH4', 'doy']].rename(columns={'doy': 'day'})
    if stretch == False:
        df = df
        df['scales'] = [(0, int(i - 1)) for i in df['day']]

    else:
        df = df.loc[df.index.repeat(24)].reset_index(drop=True)
        df['hour'] = [int(i) for i in range(0, 24)]*365
        df['scales'] = [(0, int(i - 1), int(j))
                        for i, j in zip(df['day'], df['hour'])]
    df = df[['CH4', 'scales']]
    return df


def make_nrel_cost_df(location: Location, nrel_cost_xlsx, pick_nrel_process_list: list, year_list: list, case: str, crpyears: float) -> pandas.DataFrame:
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

    nrel_cost_df_.loc[nrel_cost_df_.units == '$/KW-yr', ['cost', 'units']] = 1000 * \
        nrel_cost_df_.loc[nrel_cost_df_.units ==
                          '$/KW-yr']['cost'].values[0], '$/MW'
    nrel_cost_df_.loc[nrel_cost_df_.units == '$/kW', ['cost', 'units']] = 1000 * \
        nrel_cost_df_.loc[nrel_cost_df_.units ==
                          '$/kW']['cost'].values[0], '$/MW'
    nrel_cost_df_.loc[nrel_cost_df_.units == '$/MWh', ['cost', 'units']] = 8760 * \
        nrel_cost_df_.loc[nrel_cost_df_.units ==
                          '$/MWh']['cost'].values[0], '$/MW'

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


def load_results(filename: str) -> Result:
    """loads saved results

    Args:
        filename (str): file name

    Returns:
        Result: a energiapy result type object
    """
    file_ = open(filename, 'rb')
    results_dict = pickle.load(file_)
    if results_dict['output']['termination'] != 'optimal':
        print('WARNING: Loading non-optimal results')
    results = Result(name=filename.split('.')[
                     0], output=results_dict['output'], components=results_dict['components'], duals=results_dict['duals'])
    return results


def remove_outliers(data: pandas.DataFrame, sd_cuttoff: int = 2) -> pandas.DataFrame:
    """Removes outliers upto chosen standard deviations
    fixes data as the mean of data around the point
    Args:
        data (pandas.DataFrame): input data
        sd_cuttoff (int, optional): data upto integer number of standard deviations. Defaults to 2.

    Returns:
        pandas.DataFrame: data sans outliers
    """
    data_mean, data_std = data.mean(), data.std()
    # identify outliers
    cut_off = data_std * 3
    lower, upper = data_mean - cut_off, data_mean + cut_off
    for i in range(len(data)):
        x = data.iloc[i].values[0]
        if x < float(lower) or x > float(upper):
            data.iloc[i] = (data.iloc[i-1] + data.iloc[i+1])/2
    return data

# %%
