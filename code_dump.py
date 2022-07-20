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



# Functions


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
