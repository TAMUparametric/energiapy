# %%
"""This model is a capacitated facility location problem for a two-stage supply chain with:
n supply points, 7 potential sites, and 3 demand points. Objective is to maximize total system profit. 
Calculates environmental impact via carbon-equivalent footprint, and safety risk factor via HPSI 
and transport risk but does not restrict solution based on environmental or safety factors.
"""

__author__ = "Rahul Kakodkar, Natasha Chrisandina"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Natasha Chrisandina",
               "Efstratios N. Pistikopoulos", "Mahmoud El-Halwagi", "Sergiy Butenko"]
__license__ = "Open"
__version__ = "1.0.0"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"


from ast import Constant
from re import I
from xmlrpc.client import Boolean
import pandas as pd
import numpy as np
import random
import pickle as pkl
import csv
from itertools import product
from functools import reduce
from pyomo.environ import *
from pyomo.opt import SolverStatus, TerminationCondition
import time
from subprocess import call
from datetime import datetime, date
from collections import defaultdict
# from sklearn.cluster import AgglomerativeClustering
# from sklearn.preprocessing import StandardScaler
# from sklearn.linear_model import LinearRegression
# from sklearn.cluster import KMeans
# import scipy.stats as stats

import json as json
import matplotlib.pyplot as plt
import os
from matplotlib.ticker import (
    MultipleLocator, FormatStrFormatter, AutoMinorLocator)
from matplotlib.colors import ListedColormap
from sys import executable
from pyomo.core import *
# from graphviz import Digraph
from typing import Tuple

# import networkx as nx

# graph = nx.Graph()


# Three different types of nodes:
# Source (feed availability)
# Facility (production potential)
# Sink (demand levels)


# =================================================================================================================
# *                                                 Functions
# =================================================================================================================



def plot_loc(location_dict: dict, specify_type: str = '', color: str = 'red'):
    """Plots the locations of the nodes
    Args:
        location_dict (dict): dictionary with location coordinates
        specify_type (str, optional): specific what notes are being input, will show up in title. Defaults to ''.
        color (str, optional): color of the nodes. Defaults to 'red'.
    """
    x_ = [location_dict[i][0] for i in list(location_dict.keys())]
    y_ = [location_dict[i][1] for i in list(location_dict.keys())]

    plt.rc('font', **{'family': 'serif',
           'serif': ['Computer Modern'], 'size': 16})
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter(x_, y_, color=color)
    ax.set_xlabel('Normalized x-axis')
    ax.set_ylabel('Normalized y-axis')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.title(specify_type + ' location plot')
    plt.rcdefaults()
    return

def plot_graph(source_dict: dict, sink_dict: dict, facility_dict:dict):
    """Plots the source and sink nodes
    Args:
        source_dict (dict): dictionary with location coordinates of source node
        sink_dict (dict): dictionary with location coordinates of sink node
        facility_dict (dict): dictionary with location coordinates of facility node
        
    """
    x_source = [source_dict[i][0] for i in list(source_dict.keys())]
    y_source = [source_dict[i][1] for i in list(source_dict.keys())]

    x_sink = [sink_dict[i][0] for i in list(sink_dict.keys())]
    y_sink = [sink_dict[i][1] for i in list(sink_dict.keys())]

    x_facility = [facility_dict[i][0] for i in list(facility_dict.keys())]
    y_facility = [facility_dict[i][1] for i in list(facility_dict.keys())]

    
    plt.rc('font', **{'family': 'serif',
           'serif': ['Computer Modern'], 'size': 16})

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter(x_source, y_source, color='darkorange', s=200, label='source')
    ax.scatter(x_sink, y_sink, color='forestgreen', s=150, label='sink')
    ax.scatter(x_facility, y_facility, color='royalblue', s=150, label='facility')

    ax.set_xlabel('Normalized x-axis')
    ax.set_ylabel('Normalized y-axis')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    plt.legend()
    plt.grid(alpha=0.4)
    plt.title('source, facility, and sink locations')
    plt.rcdefaults()
    return

def plot_distance(distances_dict: dict):
    """plots the distances from source and sink
    Args:
        distances_dict (dict): dictionary with distances between source and sink 
    """
    plt.rc('font', **{'family': 'serif',
           'serif': ['Computer Modern'], 'size': 16})

    x_list = [i for i in distances_dict.keys()]
    fig, ax = plt.subplots(figsize=(10, 10))

    x_label = [int(k) for k in list(distances_dict.keys())]

    for i in x_list:
        y_ = [distances_dict[i][j] for j in distances_dict[i].keys()]
        sink_tag = [k for k in distances_dict[i]]
        # align = ['left', 'right']*(int(round(len(y_)/2)))
        # aligndist = [+0.1, -0.1]*(int(round(len(y_)/2)))
        x_ = [i]*len(y_)
        ax.scatter(x_, y_,)
        for l in range(len(y_)):
            # ax.annotate(sink_tag[l], (x_[l]+ aligndist[l] ,y_[l]), horizontalalignment = align[l])
            ax.annotate('s' + str(sink_tag[l]), (x_[l] + 0.1,
                        y_[l]), horizontalalignment='left', fontsize=12)

        # print(x_, y_, sink_tag)
    plt.xlabel('Sources')
    plt.ylabel('Distance')
    plt.xticks(x_label)
    plt.title('Distances from source to sink')
    plt.grid(alpha=0.4)
    plt.show()
    plt.rcdefaults()

    return


def plot_feed(prod_feed_dict: dict):
    """plots the feed available for each prod at each source
    Args:
        prod_feed_dict (dict): dictionary with feeds available for products at each source
    """

    plt.rc('font', **{'family': 'serif',
           'serif': ['Computer Modern'], 'size': 16})

    x_list = [i for i in prod_feed_dict.keys()]

    fig, ax = plt.subplots(figsize=(10, 10))

    for i in x_list:
        x_ = [j for j in prod_feed_dict[i].keys()]
        size_ = [5*prod_feed_dict[i][j] for j in prod_feed_dict[i].keys()]

        # sink_tag = [k for k in prod_feed_dict[i]]
        # align = ['left', 'right']*(int(round(len(y_)/2)))
        # aligndist = [+0.1, -0.1]*(int(round(len(y_)/2)))
        y_ = [i]*len(x_)
        ax.scatter(x_, y_, s=size_)
        # for l in range(len(y_)):
        # ax.annotate(sink_tag[l], (x_[l]+ aligndist[l] ,y_[l]), horizontalalignment = align[l])
        # ax.annotate('s' + str(sink_tag[l]), (x_[l]+ 0.1 ,y_[l]), horizontalalignment = 'left', fontsize = 12)

        # print(x_, y_, sink_tag)
    plt.xlabel('Sources')
    plt.ylabel('Product')

    plt.title('Feed available (size of marker)')
    plt.grid(alpha=0.4)
    plt.show()
    plt.rcdefaults()

    return


def plot_feed_conv(prod_feed_dict: dict, conversion_dict: dict):
    """Plots feed available * conversion
    Args:
        prod_feed_dict (dict): feed availability for each prod at each source
        conversion_dict (dict): conversio factors
    """

    plt.rc('font', **{'family': 'serif',
           'serif': ['Computer Modern'], 'size': 16})

    x_list = [i for i in prod_feed_dict.keys()]

    fig, ax = plt.subplots(figsize=(8, 8))

    for i in x_list:
        x_ = [j for j in prod_feed_dict[i].keys()]
        x_label = [int(j) for j in prod_feed_dict[i].keys()]

        size_ = [conversion_dict[i]*prod_feed_dict[i][j]
                 for j in prod_feed_dict[i].keys()]
        size_ = [100*i/max(size_) for i in size_]

        # sink_tag = [k for k in prod_feed_dict[i]]
        # align = ['left', 'right']*(int(round(len(y_)/2)))
        # aligndist = [+0.1, -0.1]*(int(round(len(y_)/2)))
        y_ = [i]*len(x_)
        ax.scatter(x_, y_, s=size_)
        # for l in range(len(y_)):
        # ax.annotate(sink_tag[l], (x_[l]+ aligndist[l] ,y_[l]), horizontalalignment = align[l])
        # ax.annotate('s' + str(sink_tag[l]), (x_[l]+ 0.1 ,y_[l]), horizontalalignment = 'left', fontsize = 12)

        # print(x_, y_, sink_tag)
    plt.xlabel('Sources')
    plt.ylabel('Product')
    plt.xticks(x_label)
    plt.title('Feed available x conversion (size of marker)')
    plt.grid(alpha=0.4)
    plt.show()
    plt.rcdefaults()

    return


def plot_link(result_dict: dict, prod: str, heuristic: bool):
    """plots the linkages between source and sink for prod of choice
    blue if set up, red otherwise
    Args:
        result_dict (dict): Transport linkages set up between sources and sinks
        prod (str): prod of choice
        heuristic (bool): using heuristic?
    """
    plt.rc('font', **{'family': 'serif',
           'serif': ['Computer Modern'], 'size': 16})
    x_list = [i for i in result_dict['Link'].keys()]
    x_label = [int(i) for i in result_dict['Link'].keys()]

    fig, ax = plt.subplots(figsize=(10, 10))
    for i in x_list:
        y_ = [j for j in result_dict['Link'][i].keys()]
        x_ = [i]*len(y_)
        color_dict = {
            1.0: 'cornflowerblue',
            -0.0: 'indianred'
        }
        for j in result_dict['Link'][i].keys():
            # print(x_, y_ , color_dict[result_dict['Link'][i][j][prod]])
            ax.scatter(
                x_[j], y_[j], color=color_dict[result_dict['Link'][i][j][prod]])
    plt.xlabel('Sources')
    plt.ylabel('Sinks')
    plt.xticks(x_label)
    plt.suptitle('Linkages(blue) from source to sink for prod ' + prod)
    plt.title('Heuristic: ' + str(heuristic))
    plt.grid(alpha=0.3)
    plt.show()
    plt.rcdefaults()

    return


def plot_fac(result_dict: dict, prod_list: list, heuristic: bool):
    """Facilities set up for the production of prod 
    blue if set up, red otherwise
    Args:
        result_dict (dict): dictionary with results 
        prod_list (list): list of products
        heuristic (bool): using heuristic?
    """

    plt.rc('font', **{'family': 'serif',
           'serif': ['Computer Modern'], 'size': 16})
    x_list = [i for i in result_dict['Fac'].keys()]
    x_label = [int(i) for i in result_dict['Fac'].keys()]

    fig, ax = plt.subplots(figsize=(10, 10))
    for i in x_list:
        y_ = [j for j in result_dict['Fac'][i].keys()]
        x_ = [i]*len(y_)
        color_dict = {
            1.0: 'cornflowerblue',
            -0.0: 'indianred'
        }
        iter_ = 0
        for j in result_dict['Fac'][i].keys():
            # print(x_, y_ , color_dict[result_dict['Link'][i][j][prod]])
            ax.scatter(x_[iter_], y_[iter_],
                       color=color_dict[result_dict['Fac'][i][j]])
            iter_ += 1
    # plt.xlabel('Sources')
    # plt.ylabel('Sinks')
    # plt.title('Linkages set up (blue) from source to sink for prod ' + prod )
    plt.grid(alpha=0.3)
    plt.xlabel('Sources')
    plt.ylabel('Products')
    plt.xticks(x_label)
    plt.suptitle('Facilites located (blue) for prod at source')
    plt.title('Heuristic: ' + str(heuristic))
    plt.show()
    plt.rcdefaults()

    return


# =================================================================================================================
# *                                                 Initialize/Plot graph
# =================================================================================================================


# sources, sinks, distances  = make_graph(n_sources= 5, n_sinks= 20, method = 'euclidean')
# plot_loc(location_dict = sources, specify_type = 'sources', color = 'indianred')
# plot_loc(location_dict = sinks, specify_type = 'sinks', color = 'cornflowerblue')
# plot_graph(source_dict= sources, sink_dict= sinks)
# plot_loc(location_dict = sources, specify_type = 'sources', color = 'indianred')
# plot_loc(location_dict = sinks, specify_type = 'sinks', color = 'cornflowerblue')


def solve(sources: dict, sinks: dict, facility: dict, distances_feed: dict, distances_prod: dict, prod_pot_dict: dict, sink_demand_dict: dict, conversion_dict: dict,
          capex_linkage_cost: dict, capex_prod_dict: dict, cost_prod_dict: dict, cost_prod_trans_dict: dict,
          source_re_dict: dict, linkage_re_dict: dict, iteration: int, objective: list,
          prod_list: list = ['z'], feed_list: list = ['a'], tran_list:list = ['m'], heuristic: bool = False):
    """Solves MIP, graph, kicks ass
    Args:
        sources (dict): source node defined as location coordinates
        sinks (dict): sink nodes defined as location coordinates
        facility (dict): facility nodes defined as location coordinates
        distances_feed (dict): distances between sinks and facilities
        distances_prod (dict): distances between sources and facilities 
        prod_pot_dict (dict): production potential = conversion [random] * feed availability [random] for each source, product
        sink_demand_dict (dict): demand for each sink, product
        conversion_dict (dict): conversion for each product
        capex_linkage_dict (dict): capex of transport linkage
        capex_prod_dict (dict): capex of production facility
        cost_prod_dict (dict): opex for production
        cost_prod_trans_dict (dict): opex of transporting product 
        source_re_dict (dict): sources to be re-affixed [cycled every iteration]
        linkage_re_dict (dict): linkages to be re-affixed [cycled every iteration]
        iteration (int): iteration duh!
        objective (list): objective value [all iterations]. Objective set to 10**10 (bigM) if infeasible 
        prod_list (list, optional): list of products. Defaults to ['z'].
        feed_list (list, optional): list of feeds. Defaults to ['a'].
        tran_list (list, optional): list of feeds. Defaults to ['a'].
        heuristic (bool, optional): True if running with heuristic. Defaults to False.
    Returns:
        results (dict): solution for iteration
        source_re_dict (dict): sources that need to be re-fixed
        linakge_re_dict (dict): linkages that need to be re-fixed
    """

    start_time = time.time()  # records start time

    n_sources = len(sources.keys())  # number of source nodes
    n_sinks = len(sinks.keys())  # number of sink nodes
    n_facilities = len(facility.keys())  # number of sink nodes
    # n_utility = n_utility #number of utilities modes
    # n_transport = n_transport #number of transport modes

    # declares graph with random distances
    # plot_distance(distances)

    # =================================================================================================================
    # *                                                 Ordered dictionaries
    # =================================================================================================================
    distances_feed_ord_dict = {i: dict(sorted(distances_feed[i].items(
    ), key=lambda item: item[1])) for i in distances_feed.keys()}  # distances ordered
    distances_prod_ord_dict = {i: dict(sorted(distances_prod[i].items(
    ), key=lambda item: item[1])) for i in distances_prod.keys()}  # distances ordered
    
    prod_pot_ord_dict = {i: dict(sorted(prod_pot_dict[i].items(
    ), key=lambda item: item[1])) for i in prod_pot_dict.keys()}  # production potential ordered
    # prod_feed_ord_dict = {i: dict(sorted(prod_feed_dict[i].items(), key=lambda item: item[1])) for i in prod_feed_dict.keys()}

    # print(distances_ord_dict)
    # print(prod_feed_ord_dict)
    # print(conversion_dict)
    # print(prod_pot_ord_dict)
    # print(prod_feed_dict)

    # plot_feed(prod_feed_dict = prod_feed_dict)
    # plot_feed_conv(prod_feed_dict = prod_feed_dict, conversion_dict= conversion_dict)

    bigM = 10**3

    m = ConcreteModel()  # declare instance

    # =================================================================================================================
    # *                                                 Sets
    # =================================================================================================================

    m.source = Set(initialize=range(n_sources), doc='source node indices')
    m.sink = Set(initialize=range(n_sinks), doc='sink node indices')
    m.facility = Set(initialize=range(n_facilities), doc = 'facility node indices')
    # m.utility = Set(initialize = range(n_utility), doc = 'utility indices')
    m.tran = Set(initialize =tran_list, doc = 'transport indices')
    m.prod = Set(initialize=prod_list, doc='prod indices')
    m.feed = Set(initialize=feed_list, doc='feed indices')
    

    # =================================================================================================================
    # *                                                 Binary variables
    # =================================================================================================================

    m.source_x = Var(m.feed, m.source, domain=Binary,
                     doc='1 if facility for feed (a) is established at source')
    m.facility_x = Var(m.feed, m.prod, m.facility, domain=Binary,
                     doc='1 if facility for feed(a) converted to prod (z) is established at facility')
    m.sink_x = Var(m.prod, m.sink, domain=Binary,
                     doc='1 if facility for prod (z) is established at sink')
    
    m.linkage_feed_x = Var(m.feed, m.source, m.facility, m.tran, domain=Binary,
                      doc='1 if transportation linkage is established for feed from source to facility')

    m.linkage_prod_x = Var(m.prod, m.facility, m.sink,  m.tran, domain=Binary,
                      doc='1 if transportation linkage is established for prod from facility to sink')

    # =================================================================================================================
    # *                                                 Continuous variables
    # =================================================================================================================

    m.trans_feed_cost = Var(m.feed, m.source, m.facility,  m.tran, domain=NonNegativeReals,
                       doc='cost of transporting feed (a) from source to facility through transport mode (m)')
    m.trans_prod_cost = Var(m.prod, m.facility, m.sink,  m.tran, domain=NonNegativeReals,
                       doc='cost of transporting prod (z) from facility to sink through thransport mode (m)')
    m.fac_feed = Var(m.feed, m.facility, domain=NonNegativeReals,
                        doc='amount of feed (a) consumed at facility')
    m.fac_feed_trans = Var(m.feed, m.source, m.facility, m.tran, domain=NonNegativeReals,
                        doc='amount of feed (a) routed from source to facility through transport model')
    m.fac_prod = Var(m.prod, m.facility, domain=NonNegativeReals,
                        doc='amount of prod (z) produced at facility')
    m.fac_prod_trans = Var(m.prod, m.facility, m.sink, m.tran, domain=NonNegativeReals,
                              doc='amount of prod (z) routed from facility to sink through transport mode (m)')
    m.fac_cap = Var(m.prod, m.facility, domain=NonNegativeReals,
                              doc='capacity of facility to produce z')
    m.fac_capex = Var(m.prod, m.facility, domain=NonNegativeReals,
                         doc='fixed capital investment for producing prod (z) at source')
    m.fac_opex = Var(m.prod, m.facility, domain=NonNegativeReals,
                        doc='variable operation expenditure for producing prod (z) at source')
    m.trans_feed_cap = Var(m.feed, m.source, m.facility, m.tran,  domain=NonNegativeReals,
                      doc='transportation linkage capacity from source to facility for feed (a) through transport mode (m)')
    m.trans_feed_capex = Var(m.feed, m.sink, m.facility, m.tran,  domain=NonNegativeReals,
                      doc='fixed capital investment in transport linkage from source to facility for feed (a) through transport mode (m)')
    m.trans_feed_capex = Var(m.feed, m.sink, m.facility, m.tran,  domain=NonNegativeReals,
                      doc='variable operation expenditure for  transporting for feed (a) from sink to facility through transport mode (m)')
    m.trans_prod_cap = Var(m.feed, m.facility, m.sink, m.tran,  domain=NonNegativeReals,
                      doc='transportation linkage capacity from facility to sink for prod (z) through transport mode (m)')
    m.trans_prod_capex = Var(m.feed, m.facility, m.sink, m.tran,  domain=NonNegativeReals,
                      doc='fixed capital investment in transport linkage from facility to sink for prod (z) through transport mode (m)')
    m.trans_prod_capex = Var(m.feed, m.facility, m.sink, m.tran,  domain=NonNegativeReals,
                      doc='variable operation expenditure for  transporting for prod (z) from facility to sink through transport mode (m)')
    
    
     
    
    # m.source_feed_cons = Var(m.prod, m.prod, m.source, domain=NonNegativeReals,
    #                          doc='amount of feed used for production of prod (z) at source')
    # m.prod_cost = Var(m.prod, m.source, domain=NonNegativeReals,
    #                   doc='cost of making prod (z) at source')

    # m.source_sale = Var(m.prod, m.source, domain=NonNegativeReals,
    #                     doc='annual sales of prod (z) at source')
    
    # m.source_emission = Var(m.prod, m.source, domain=NonNegativeReals,
    #                         doc='emissions from producing prod (z) at source')

    # # m.safety_risk = Var(m.prod, m.source, domain=NonNegativeReals, doc = 'process safety scaling factor')
    # # m.process_risk = Var(m.prod, m.source, domain=NonNegativeReals, doc = 'total process risk factor')
    # # m.transport_risk = Var(m.prod, m.transport, m.sink, m.source,  domain=NonNegativeReals, doc = 'transport risk factor for transportion mode of prod (z) from source to sink')

    # m.source_cap = Var(m.prod, m.source, domain=NonNegativeReals,
    #                    doc='capacity for production of prod (z) at source')
    # m.trans_cap = Var(m.prod, m.sink, m.source,  domain=NonNegativeReals,
    #                   doc='transportation linkage capacity from source to sink for prod (z)')

    # m.trans_capex = Var(m.prod, m.sink, m.source,  domain=NonNegativeReals,
    #                     doc='capacity of linkage for prod (z) between source and sink')

    # =================================================================================================================
    # *                                                 Affix binaries based on ordered dicts
    # =================================================================================================================
    if heuristic == True:
        # if last iteration was infeasible... diversify [toll is lower as well]
        if objective[iter_ - 1] == 10**10:
            toll = 0.5  # tolerance to be used
            for prod in prod_list:  # problem is combinatorally divided for each product
                # print(prod)
                # ordered sources based on production potential
                prod_pot_ord = [source for source in list(
                    prod_pot_ord_dict[prod].keys())]
                # fix sources [source_x = 1] for top two quartiles
                prod_pot_fix = prod_pot_ord[:int(round(len(prod_pot_ord)/2))]

                # print('prod_pot_ord')
                # print(prod_pot_ord)
                # print('prod_pot_fix')
                # print(prod_pot_fix)

                for source in range(n_sources):
                    # print('source ' + str(source))
                    if source in prod_pot_fix:  # source in 2nd quartile essentially
                        # print('fix 1')
                        # print(source)
                        # generate a random number
                        random_n = random.uniform(0, 1)
                        # if number less than tolerance affix source [lower tolerance helps diversify]
                        if random_n < toll:
                            m.source_x[prod, source].fix(1.0)
                        else:
                            m.source_x[prod, source].fix(0.0)

                        # now affix sinks with the 2nd quartile of distances
                        sinks_distance_ord = [sink for sink in list(
                            distances_ord_dict[source].keys())]
                        sinks_distance_fix = sinks_distance_ord[:int(
                            round(len(sinks_distance_ord)/2))]
                        fix = 1.0  # affix transportation linkages to 1 only if source exists, and within 2nd distance quartile

                    else:
                        # print('fix 0')
                        # print(source)
                        random_n = random.uniform(0, 1)
                        if random_n < toll:  # for the rest randomly affix some.
                            m.source_x[prod, source].fix(0.0)
                        else:
                            m.source_x[prod, source].fix(1.0)

                        sinks_distance_ord = [sink for sink in list(
                            distances_ord_dict[source].keys())]
                        sinks_distance_fix = sinks_distance_ord
                        fix = 0.0  # affix transportation linkages to 0 if source does not exist
                    # print('sinks_distance_ord')
                    # print(sinks_distance_ord)
                    # print('sinks_distance_fix')
                    # print(sinks_distance_fix)
                    for sink in range(n_sinks):
                        if sink in sinks_distance_fix:
                            # print('fix ' + str(fix))
                            # print(sink)
                            m.linkage_x[prod, sink, source].fix(fix)
                        # else:
                            # print('fix 0')
                            # print(sink)
                            # m.linkage_x[prod, sink, source].fix(0.0)

        # if last iteration was not infeasible... intensify [toll is higher as well]
        else:
            toll = 0.8  # higher tolerance, accept more solutions
            # first iter is set to MIP solution [can be changed, need to generalize].
            if iter_ == 1:
                # so this is the first heuristic iteration
                for prod in prod_list:
                    # print(prod)

                    prod_pot_ord = [source for source in list(
                        prod_pot_ord_dict[prod].keys())]  # order sources by prod pot
                    # affix within 2nd quartile
                    prod_pot_fix = prod_pot_ord[:int(
                        round(len(prod_pot_ord)/2))]

                    # print('prod_pot_ord')
                    # print(prod_pot_ord)
                    # print('prod_pot_fix')
                    # print(prod_pot_fix)
                    for source in range(n_sources):
                        # print('source ' + str(source))
                        if source in prod_pot_fix:
                            # print('fix 1')
                            # print(source)

                            # located facilities greedily
                            m.source_x[prod, source].fix(1.0)
                            sinks_distance_ord = [sink for sink in list(
                                distances_ord_dict[source].keys())]
                            sinks_distance_fix = sinks_distance_ord[:int(
                                round(len(sinks_distance_ord)/2))]
                            fix = 1.0

                        else:
                            # print('fix 0')
                            # print(source)

                            # do not locate facilities here
                            m.source_x[prod, source].fix(0.0)
                            sinks_distance_ord = [sink for sink in list(
                                distances_ord_dict[source].keys())]
                            sinks_distance_fix = sinks_distance_ord
                            fix = 0.0
                        # print('sinks_distance_ord')
                        # print(sinks_distance_ord)
                        # print('sinks_distance_fix')
                        # print(sinks_distance_fix)
                        for sink in range(n_sinks):
                            if sink in sinks_distance_fix:
                                # print('fix ' + str(fix))
                                # print(sink)
                                # set all linkages to 1 from affixed sources to sinks
                                m.linkage_x[prod, sink, source].fix(fix)
                            # else:
                                # print('fix 0')
                                # print(sink)
                                # m.linkage_x[prod, sink, source].fix(0.0)

            else:
                if (iter_ > 3):
                    # if solution has not improved
                    if (objective[iter_-1] < 1.005*objective[iter_ - 2]):

                        # print(objective[iter_-1], objective[iter_-2])
                        print('===============================================')
                        for prod, source in product(prod_list, range(n_sources)):
                            # if source was already affixed to 1 and needs to be reassigned
                            if source_re_dict[source][prod] == 1:
                                # randomly shuffle the affixed
                                random_n = random.uniform(0, 1)
                                if random_n < toll:
                                    m.source_x[prod, source].fix(1.0)
                                else:
                                    m.source_x[prod, source].fix(0.0)

                            else:  # if source was already affixed to 0 and needs to be reassigned
                                random_n = random.uniform(
                                    0, 1)  # randomly shuffle
                                if random_n < toll:
                                    m.source_x[prod, source].fix(1.0)
                                else:
                                    m.source_x[prod, source].fix(0.0)

                            for sink in range(n_sinks):
                                # if linkage was already affixed to 1 and needs to be reassigned
                                if linkage_re_dict[source][sink][prod] == 1:
                                    random_n = random.uniform(0, 1)
                                    if random_n < toll:
                                        m.linkage_x[prod, sink,
                                                    source].fix(1.0)
                                    else:
                                        m.linkage_x[prod, sink,
                                                    source].fix(0.0)

                                else:  # if linkage was already affixed to 0 and needs to be reassigned
                                    random_n = random.uniform(0, 1)
                                    if random_n < toll:
                                        m.linkage_x[prod, sink,
                                                    source].fix(1.0)
                                    else:
                                        m.linkage_x[prod, sink,
                                                    source].fix(0.0)

                else:  # if solution is not too bad, start stitching the solution
                    # note that sources and linkages are cycled with the intension of being affixed
                    # not utilized facilities and linakges are set to 0
                    # this helps improve the solution by avoiding uncessary facilities, linkages
                    # All binaries are still affixed!
                    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++')

                    for prod, source in product(prod_list, range(n_sources)):
                        # keep the affixed sources
                        if source_re_dict[source][prod] == 1:
                            m.source_x[prod, source].fix(1.0)
                        else:
                            m.source_x[prod, source].fix(0.0)

                        for sink in range(n_sinks):  # keep the affixed linkages
                            if linkage_re_dict[source][sink][prod] == 1:
                                m.linkage_x[prod, sink, source].fix(1.0)
                            else:
                                m.linkage_x[prod, sink, source].fix(0.0)

    # =================================================================================================================
    # *                                                 Material flow constraints
    # =================================================================================================================

    def fac_prod_rule(m, prod, feed, facility):
        return m.fac_prod[prod, facility] == conversion_dict[prod][feed]*m.fac_feed[feed, facility]
    m.prod_prod_constraint = Constraint(
        m.prod, m.feed, m.facility, rule=fac_prod_rule, doc='prod (z) produced at facility from feed (a)')

    def trans_feed_rule(m, feed, facility):
        return m.fac_feed[feed, facility] == sum(m.fac_feed_trans[feed, source_, facility, tran_] for source_, tran_ in zip(m.source, m.tran))
    m.trans_feed_cons = Constraint(
        m.feed, m.facility, rule=trans_feed_rule, doc='sum of feed from source to facility')


    def trans_prod_rule(m, prod, facility):
        return m.fac_prod[prod, facility] == sum(m.fac_prod_trans[prod, facility, sink_, tran_] for sink_, tran_ in zip(m.sink, m.tran))
    m.trans_prod_cons = Constraint(
        m.feed, m.facility, rule=trans_prod_rule, doc='sum of feed from source to facility')

    # amount of feed consumed to produce prod at source
    def feed_cons_rule(m, feed, source):
        return sum(m.fac_feed_trans[feed, source, facility_, tran_] for facility_, tran_ in zip(m.facility, m.tran))  <= source_feed_dict[feed][source]
    m.feed_cons_cons = Constraint(
        m.feed, m.source, rule=feed_cons_rule, doc='total feed (a) consumed at source')

    def prod_cons_rule(m, prod, sink):
        return sum(m.fac_prod_trans[prod, facility_, sink, tran_] for facility_, tran_ in zip(m.facility, m.tran))  <= sink_prod_dict[prod][sink]
    m.prod_cons_cons = Constraint(
        m.prod, m.sink, rule=prod_cons_rule, doc='total prod (z) sent to sink')

    # # meet demand through source at sink
    # def prod_dem_rule(m, prod, sink):
    #     return sum(m.source_prod_trans[prod, sink, source_] for source_ in range(n_sources)) == sink_demand_dict[prod][sink]
    # m.prod_dem_cons = Constraint(
    #     m.prod, m.sink, rule=prod_dem_rule, doc='meet demand at sink from all available sources')

    # m.prod_prod_constraint.pprint()
    # m.prod_dem_constraint.pprint()
    # m.feed_cons_constraint.pprint()
    # m.prod_dem_constraint.pprint()

    # def prod_dem_rule(m, sink):
    #     return sum(m.source_prod_trans['a', source_, sink] for source_ in range(n_sources)) == sink_demand_dict['a'][sink]
    # m.prod_dem_constraint = Constraint(m.sink, rule = prod_dem_rule, doc = 'meet demand at sink from all available sources')

    # amount of material transported to sink from source
    def trans_rule(m, prod, source):
        return m.source_prod[prod, source] == sum(m.source_prod_trans[prod, sink_, source] for sink_ in range(n_sinks))
    m.trans_cons = Constraint(
        m.prod, m.source, rule=trans_rule, doc='send prod out of source to sinks')

    # =================================================================================================================
    # *                                                 Network design constraints
    # =================================================================================================================

    def facility_loc_rule(m, prod, source):
        return m.source_cap[prod, source] <= 1000*m.source_x[prod, source]
    m.facility_loc_cons = Constraint(m.prod, m.source, rule=facility_loc_rule,
                                     doc='decides whether to set up facility for prod (z) at source')

    def linkage_loc_rule(m, prod, sink, source):
        return m.trans_cap[prod, sink, source] <= 100*m.linkage_x[prod, sink, source]
    m.linkage_loc_cons = Constraint(m.prod, m.sink, m.source,  rule=linkage_loc_rule,
                                    doc='decides whether to set up facility for prod (z) at source')

    def facility_cap_rule(m, prod, source):
        return m.source_prod[prod, source] <= m.source_cap[prod, source]
    m.facility_cap_cons = Constraint(
        m.prod, m.source, rule=facility_cap_rule, doc='keeps production under capacity')

    def linkage_cap_rule(m, prod, sink, source):
        return m.source_prod_trans[prod, sink, source] <= m.trans_cap[prod, sink, source]
    m.linkage_cap_cons = Constraint(
        m.prod, m.sink, m.source,  rule=linkage_cap_rule, doc='keeps prod transport under capacity')

    # m.facility_loc_cons.pprint()
    # m.linkage_loc_cons.pprint()
    # m.facility_cap_cons.pprint()
    # m.linkage_cap_cons.pprint()

    def facility_loc_rule2(m, prod, source):
        return m.source_cap[prod, source] >= (10**(-2))*m.source_x[prod, source]
    m.facility_loc_cons2 = Constraint(m.prod, m.source, rule=facility_loc_rule2,
                                      doc='decides whether to set up facility for prod (z) at source')

    def linkage_loc_rule2(m, prod, sink, source):
        return m.trans_cap[prod, sink, source] >= (10**(-2))*m.linkage_x[prod, sink, source]
    m.linkage_loc_cons2 = Constraint(m.prod, m.sink, m.source,  rule=linkage_loc_rule2,
                                     doc='decides whether to set up facility for prod (z) at source')

    # =================================================================================================================
    # *                                                 Cost constraints
    # =================================================================================================================

    # cost of establishing facility

    def facility_cost_rule(m, prod, source):  # m.source_x
        return m.source_capex[prod, source] == capex_prod_dict[prod]*m.source_cap[prod, source]
    m.facility_cost_cons = Constraint(
        m.prod, m.source, rule=facility_cost_rule, doc='calculates the cost of locating facility')

    def linkage_cost_rule(m, prod, sink, source):  # m.linkage_x
        return m.trans_capex[prod, sink, source] == distances[source][sink]*capex_linkage_cost*m.trans_cap[prod, sink, source]
    m.linkage_cost_cons = Constraint(
        m.prod, m.sink, m.source,  rule=linkage_cost_rule, doc='calculates the cost of locating linkage')

    def source_sale_rule(m, prod, source):
        return m.prod_cost[prod, source] == m.source_prod[prod, source]*cost_prod_dict[prod][source]
    m.source_sale_cons = Constraint(
        m.prod, m.source, rule=source_sale_rule, doc='calculates the cost of production')

    def trans_cost_rule(m, prod, sink, source):
        return m.trans_cost[prod, sink, source] == distances[source][sink]*cost_prod_trans_dict[prod]*m.source_prod_trans[prod, sink, source]
    m.trans_cost_cons = Constraint(
        m.prod, m.sink, m.source,  rule=trans_cost_rule, doc='calculates the cost of transportation')

    # =================================================================================================================
    # *                                                 Cost objective
    # =================================================================================================================

    # Objective should be  (cost of production) + (cost of transport) -#TBF

    def objective_rule(m):
        return sum(sum(m.prod_cost[prod, source] + m.source_capex[prod, source] for prod in m.prod) for source in m.source) \
            + sum(sum(sum(m.trans_cost[prod, sink, source] + m.trans_capex[prod, sink, source]
                  for prod in m.prod) for source in m.source) for sink in m.sink)
    m.obj = Objective(rule=objective_rule, sense=minimize,
                      doc='minimizes cost of operation (facility location, production, transport)')

    solver_ = SolverFactory('gurobi', solver_io='python')
    # results = solver_.solve(m, tee = True)
    results = solver_.solve(m, tee=True)

    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
        result = {'Feed': {k: {j: {i: m.source_feed_cons[i, j, k].value for i in prod_list} for j in prod_list} for k in range(n_sources)},
                  'Prod': {j: {i: m.source_prod[i, j].value for i in prod_list} for j in range(n_sources)},
                  'Trans': {k: {j: {i: m.source_prod_trans[i, j, k].value for i in prod_list} for j in range(n_sinks)} for k in range(n_sources)},
                  'Prod_cost': {j: {i: m.prod_cost[i, j].value for i in prod_list} for j in range(n_sources)},
                  'Fac': {j: {i: m.source_x[i, j].value for i in prod_list} for j in range(n_sources)},
                  'Link': {k: {j: {i: m.linkage_x[i, j, k].value for i in prod_list} for j in range(n_sinks)} for k in range(n_sources)},
                  'Prod_cap': {j: {i: m.source_cap[i, j].value for i in prod_list} for j in range(n_sources)},
                  'Trans_cap': {k: {j: {i: m.trans_cap[i, j, k].value for i in prod_list} for j in range(n_sinks)} for k in range(n_sources)},
                  'Comp':  time.time() - start_time,
                  'sources': n_sources,
                  'sinks': n_sinks,
                  'Objective': m.obj()
                  }

        # for prod in prod_list:
        # plot_link(result_dict = result, prod = prod, heuristic= heuristic)

    else:
        print('Solution Infeasible')
        result = {'Feed': {k: {j: {i: 0 for i in prod_list} for j in prod_list} for k in range(n_sources)},
                  'Prod': {j: {i: 0 for i in prod_list} for j in range(n_sources)},
                  'Trans': {k: {j: {i: 0 for i in prod_list} for j in range(n_sinks)} for k in range(n_sources)},
                  'Prod_cost': {j: {i: 0 for i in prod_list} for j in range(n_sources)},
                  'Fac': {j: {i: 0 for i in prod_list} for j in range(n_sources)},
                  'Link': {k: {j: {i: 0 for i in prod_list} for j in range(n_sinks)} for k in range(n_sources)},
                  'Prod_cap': {j: {i: 0 for i in prod_list} for j in range(n_sources)},
                  'Trans_cap': {k: {j: {i: 0 for i in prod_list} for j in range(n_sinks)} for k in range(n_sources)},
                  'Comp':  time.time() - start_time,
                  'sources': n_sources,
                  'sinks': n_sinks,
                  'Objective': 10**10  # set objective to bigM if infeasible
                  }

    # m.source_capex.pprint()
    # m.trans_capex.pprint()

    # m.linkage_x.pprint()
    # m.source_x.pprint()
    # m.source_prod.pprint()
    # m.source_prod_trans.pprint()

    # dict for readjusting sources

    for i, j in product(range(n_sources), prod_list):
        toll_fac = 1
        toll_link = 1
        # gurobi gives very small values instead of 0.0 for binaries sometime, this just fixes that [good for plotting]
        if result['Fac'][i][j] <= 10**(-5):
            result['Fac'][i][j] = 0.0

        # if facility is not utilized [within a certain tolerance]
        if result['Prod'][i][j] <= toll_fac:
            source_re_dict[i][j] = 0

    for i, j, k in product(range(n_sources), range(n_sinks), prod_list):
        # if linkage is not utilized [within a certain tolerance]
        if result['Trans'][i][j][k] <= toll_link:
            linkage_re_dict[i][j][k] = 0

    # plot_fac(result_dict = result, prod_list= prod_list, heuristic = heuristic)
    # keep the list of objectives to compare
    objective.append(result['Objective'])
    # print(objective[iter_])

    return result, source_re_dict, linkage_re_dict

# %%for single instances
# =================================================================================================================
# *                                                 Generate graph
# =================================================================================================================


n_sources = 5
n_sinks = 12
n_facilities = 7

sources, sinks, facilities, distances_feed, distances_prod = make_graph(
    n_sources=n_sources, n_sinks=n_sinks, n_facilities= n_facilities, method='euclidean')
# plot_graph(source_dict= sources, sink_dict= sinks)

# =================================================================================================================
# *                                                 Parameters - randomized
# =================================================================================================================
# uniform/randrange for float/int between (a,b)
# currently set costs to float, rest to int (easy to differentiate)
prod_list = ['z']
feed_list = ['a']

conversion_dict = {i: {j: random.uniform(50, 100) for j in feed_list} for i in prod_list}

# # dictionary with the feed available for prod (z) at each source
# prod_feed_dict = {j: {i: random.randrange(
#     0, 100) for i in range(n_sources)} for j in prod_list}
# sink_demand_dict = {j: {i: random.uniform(
#     0, 100) for i in range(n_sinks)} for j in prod_list}

source_feed_dict = {j: {i: random.randrange(
    0, 100) for i in range(n_sources)} for j in feed_list}

sink_prod_dict = {j: {i: random.randrange(
    0, 100) for i in range(n_sinks)} for j in prod_list}
#%%
# can keep constant capacity
# prod_cap_dict = {j: {i: random.randrange(0, 100) for i in range(n_sources)} for j in prod_list}

capex_linkage_cost = random.uniform(50, 100)

capex_prod_dict = {j: random.uniform(500, 1000) for j in prod_list}
cost_prod_trans_dict = {j: random.uniform(50, 100) for j in prod_list}


# trans_cap = {i: random.randrange(0, 100) for i in range(n_transport)}

# trans_loss = {i: random.uniform(0, 100) for i in range(n_transport)}


cost_feed_dict = {j: {i: random.uniform(
    50, 100) for i in range(n_sources)} for j in prod_list}
cost_prod_dict = {j: {i: random.uniform(
    50, 100) for i in range(n_sources)} for j in prod_list}
# dictionary with the demand for prod (z) at each sink
prod_demand_dict = {j: {i: random.randrange(
    0, 50) for i in range(n_sinks)} for j in prod_list}

# this will depend on the distance between sources and sink
cost_prod_trans = random.uniform(50, 100)

# cost_util_dict = {i: random.randrange(0, 100) for i in range(n_utility)}

# the utility required to produce prod (z) on a nominal basis
# prod_util_dict = {j: {i: random.randrange(0, 100) for i in range(n_utility)} for j in prod_list}
# carbon_util_dict = {i: random.randrange(0, 100) for i in range(n_utility)}
# carbon_trans_dict = {i: random.randrange(0, 100) for i in range(n_transport)}
# accident_risk = {i: random.randrange(0, 100) for i in range(n_transport)}


conversion_dict = {i: {j: random.uniform(50, 100) for j in feed_list} for i in prod_list}

# production potential = (conversion)*(feed availability)
prod_pot_dict = {i: {j: prod_feed_dict[i][j]*conversion_dict[i]
                     for j in prod_feed_dict[i].keys()} for i in prod_list}
source_re_dict = {j: {i: 1 for i in prod_list} for j in range(n_sources)}
linkage_re_dict = {k: {j: {i: 1 for i in prod_list}
                       for j in range(n_sinks)} for k in range(n_sources)}

objective = []
iter_ = 0
tolerance = 0.01
while iter_ < 2:  # solve with and without heuristics to compare
    if iter_ == 0:
        heuristic = False
    else:
        heuristic = True
    result, source_re_dict, linkage_re_dict = solve(sources=sources, sinks=sinks, distances=distances,
                                                    prod_pot_dict=prod_pot_dict, sink_demand_dict=sink_demand_dict, conversion_dict=conversion_dict,
                                                    capex_linkage_cost=capex_linkage_cost, capex_prod_dict=capex_prod_dict, cost_prod_dict=cost_prod_dict, cost_prod_trans_dict=cost_prod_trans_dict, source_re_dict=source_re_dict, linkage_re_dict=linkage_re_dict,
                                                    iteration=iter_, objective=objective, prod_list=prod_list, heuristic=heuristic)
    # print(source_re_dict)
    # print(linkage_re_dict)

    # print(result['Prod'])
    # print(objective)
    if iter_ > 0:
        if (objective[iter_] <= objective[0]) or (objective[iter_] <= (1 + tolerance)*objective[0]):
            print(objective)
            break

    iter_ += 1


# %%for initialization

n_source_list = [1 + int(round(random.uniform(5, 10))*i*5) for i in range(2)]
n_sinks_list = [1 + int(round(random.uniform(5, 10))*i*5) for i in range(2)]
iter2_ = 0
# heuristic = True
comp_ = []
comp_h = []
comp_m = []
obj_h = []
obj_m = []
for n_sources in n_source_list:

    n_sinks = n_sinks_list[iter2_]

    sources, sinks, distances = make_graph(
        n_sources=n_sources, n_sinks=n_sinks, method='euclidean')
# plot_graph(source_dict= sources, sink_dict= sinks)

    # =================================================================================================================
    # *                                                 Parameters - randomized
    # =================================================================================================================
    # uniform/randrange for float/int between (a,b)
    # currently set costs to float, rest to int (easy to differentiate)

    prod_list = ['a', 'b', 'c', 'd']

    # dictionary with the feed available for prod (z) at each source
    prod_feed_dict = {j: {i: random.randrange(
        0, 100) for i in range(n_sources)} for j in prod_list}
    sink_demand_dict = {j: {i: random.uniform(
        0, 100) for i in range(n_sinks)} for j in prod_list}

    # can keep constant capacity
    # prod_cap_dict = {j: {i: random.randrange(0, 100) for i in range(n_sources)} for j in prod_list}

    capex_linkage_cost = random.uniform(50, 100)

    capex_prod_dict = {j: random.uniform(500, 1000) for j in prod_list}
    cost_prod_trans_dict = {j: random.uniform(50, 100) for j in prod_list}

    # trans_cap = {i: random.randrange(0, 100) for i in range(n_transport)}

    # trans_loss = {i: random.uniform(0, 100) for i in range(n_transport)}

    cost_feed_dict = {j: {i: random.uniform(
        50, 100) for i in range(n_sources)} for j in prod_list}
    cost_prod_dict = {j: {i: random.uniform(
        50, 100) for i in range(n_sources)} for j in prod_list}
    # dictionary with the demand for prod (z) at each sink
    prod_demand_dict = {j: {i: random.randrange(
        0, 50) for i in range(n_sinks)} for j in prod_list}

    # this will depend on the distance between sources and sink
    cost_prod_trans = random.uniform(50, 100)

    # cost_util_dict = {i: random.randrange(0, 100) for i in range(n_utility)}

    # the utility required to produce prod (z) on a nominal basis
    # prod_util_dict = {j: {i: random.randrange(0, 100) for i in range(n_utility)} for j in prod_list}
    # carbon_util_dict = {i: random.randrange(0, 100) for i in range(n_utility)}
    # carbon_trans_dict = {i: random.randrange(0, 100) for i in range(n_transport)}
    # accident_risk = {i: random.randrange(0, 100) for i in range(n_transport)}

    conversion_dict = {i: random.uniform(50, 100) for i in prod_list}

    # production potential = (conversion)*(feed availability)
    prod_pot_dict = {i: {j: prod_feed_dict[i][j]*conversion_dict[i]
                         for j in prod_feed_dict[i].keys()} for i in prod_list}
    source_re_dict = {j: {i: 1 for i in prod_list}
                      for j in range(n_sources)}
    linkage_re_dict = {k: {j: {i: 1 for i in prod_list}
                           for j in range(n_sinks)} for k in range(n_sources)}

    objective = []
    iter_ = 0
    tolerance = 0.01

    while iter_ < 2:  # solve with and without heuristics to compare
        if iter_ == 0:
            heuristic = False
        else:
            heuristic = True
        result, source_re_dict, linkage_re_dict = solve(sources=sources, sinks=sinks, distances=distances,
                                                        prod_pot_dict=prod_pot_dict, sink_demand_dict=sink_demand_dict, conversion_dict=conversion_dict,
                                                        capex_linkage_cost=capex_linkage_cost, capex_prod_dict=capex_prod_dict, cost_prod_dict=cost_prod_dict, cost_prod_trans_dict=cost_prod_trans_dict, source_re_dict=source_re_dict, linkage_re_dict=linkage_re_dict,
                                                        iteration=iter_, objective=objective, prod_list=prod_list, heuristic=heuristic)
        # print(source_re_dict)
        # print(linkage_re_dict)

        # print(result['Prod'])
        # print(objective)
        # if iter_ > 0:
        #     if (objective[iter_] <= objective[0]) or (objective[iter_] <= (1 + tolerance)*objective[0]):
        #         print(objective)
        #         break
        if heuristic == False:
            comp_m.append(result['Comp'])
            obj_m.append(result['Objective'])

        if heuristic == True:
            comp_h.append(result['Comp'])
            obj_h.append(result['Objective'])

        iter_ += 1

    iter2_ += 1


# %%for computational studies

# =================================================================================================================
# *                                                 Generate graph
# =================================================================================================================
n_source_list = [1 + int(round(random.uniform(5, 10))*i*5) for i in range(2)]
n_sinks_list = [1 + int(round(random.uniform(5, 10))*i*5) for i in range(2)]
iter2_ = 0
# heuristic = True
comp_ = []
for n_sources in n_source_list:

    n_sinks = n_sinks_list[iter2_]

    sources, sinks, distances = make_graph(
        n_sources=n_sources, n_sinks=n_sinks, method='euclidean')
    iter2_ += 1
    # plot_graph(source_dict= sources, sink_dict= sinks)
    # =================================================================================================================
    # *                                                 Parameters - randomized
    # =================================================================================================================
    # uniform/randrange for float/int between (a,b)
    # currently set costs to float, rest to int (easy to differentiate)

    prod_list = ['a', 'b', 'c', 'd']

    # dictionary with the feed available for prod (z) at each source
    prod_feed_dict = {j: {i: random.randrange(
        0, 100) for i in range(n_sources)} for j in prod_list}
    sink_demand_dict = {j: {i: random.uniform(
        0, 100) for i in range(n_sinks)} for j in prod_list}

    # can keep constant capacity
    # prod_cap_dict = {j: {i: random.randrange(0, 100) for i in range(n_sources)} for j in prod_list}

    capex_linkage_cost = random.uniform(50, 100)

    capex_prod_dict = {j: random.uniform(500, 1000) for j in prod_list}
    cost_prod_trans_dict = {j: random.uniform(50, 100) for j in prod_list}

    # trans_cap = {i: random.randrange(0, 100) for i in range(n_transport)}

    # trans_loss = {i: random.uniform(0, 100) for i in range(n_transport)}

    cost_feed_dict = {j: {i: random.uniform(
        50, 100) for i in range(n_sources)} for j in prod_list}
    cost_prod_dict = {j: {i: random.uniform(
        50, 100) for i in range(n_sources)} for j in prod_list}
    # dictionary with the demand for prod (z) at each sink
    prod_demand_dict = {j: {i: random.randrange(
        0, 50) for i in range(n_sinks)} for j in prod_list}

    # this will depend on the distance between sources and sink
    cost_prod_trans = random.uniform(50, 100)

    # cost_util_dict = {i: random.randrange(0, 100) for i in range(n_utility)}

    # the utility required to produce prod (z) on a nominal basis
    # prod_util_dict = {j: {i: random.randrange(0, 100) for i in range(n_utility)} for j in prod_list}
    # carbon_util_dict = {i: random.randrange(0, 100) for i in range(n_utility)}
    # carbon_trans_dict = {i: random.randrange(0, 100) for i in range(n_transport)}
    # accident_risk = {i: random.randrange(0, 100) for i in range(n_transport)}

    conversion_dict = {i: random.uniform(50, 100) for i in prod_list}

    # production potential = (conversion)*(feed availability)
    prod_pot_dict = {i: {j: prod_feed_dict[i][j]*conversion_dict[i]
                         for j in prod_feed_dict[i].keys()} for i in prod_list}
    source_re_dict = {j: {i: 1 for i in prod_list}
                      for j in range(n_sources)}
    linkage_re_dict = {k: {j: {i: 1 for i in prod_list}
                           for j in range(n_sinks)} for k in range(n_sources)}

    objective = [0]
    iter_ = 0
    tolerance = 0.01
    # solve with and without heuristics to compare
    # solve with and without heuristics to compare
    if heuristic == False:
        iter_max = 1
    else:
        iter_max = 5
    while iter_ < iter_max:
        compp_ = []
        result, source_re_dict, linkage_re_dict = solve(sources=sources, sinks=sinks, distances=distances,
                                                        prod_pot_dict=prod_pot_dict, sink_demand_dict=sink_demand_dict, conversion_dict=conversion_dict,
                                                        capex_linkage_cost=capex_linkage_cost, capex_prod_dict=capex_prod_dict, cost_prod_dict=cost_prod_dict, cost_prod_trans_dict=cost_prod_trans_dict, source_re_dict=source_re_dict, linkage_re_dict=linkage_re_dict,
                                                        iteration=iter_, objective=objective, prod_list=prod_list, heuristic=heuristic)
        # compp_.append(result['Comp'])
        # print(source_re_dict)
        # print(linkage_re_dict)

        # print(result['Prod'])
        # print(objective)
        if iter_ > 0:
            if (objective[iter_] <= objective[0]) or (objective[iter_] <= (1 + tolerance)*objective[0]):
                print(objective)
                break

        iter_ += 1

    # comp_.append(sum(compp_))
    comp_.append(result['Comp'])

# %%

# %%for computational studies
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': 16})
fig, ax = plt.subplots(figsize=(12, 6))
ax.scatter(n_source_list, comp_h, label='heuristic')
ax.scatter(n_source_list, comp_m, label='MIP')
val_annot = [100*(i - j)/j for i, j in zip(obj_h, obj_m)]
for i in range(len(val_annot)):
    ax.annotate(str("{0:.2g}".format(val_annot[i])) + '%', (n_source_list[i], 0),
                verticalalignment='top', horizontalalignment='center', fontsize=11)

plt.legend()
plt.xlabel('# of sources')
plt.ylabel('time (s)')
plt.title('Scaling of computational time')
# plt.ylim(-100, 700)
plt.show()
plt.rcdefaults()

# %%for computational studies
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': 16})
plt.figure(figsize=(6, 6))
plt.scatter(n_source_list, comp_)
plt.xlabel('# of sources')
plt.ylabel('time (s)')
plt.title('Scaling of computational time')
# plt.legend(loc = 'best')
plt.rcdefaults()
# %%

objective_plot = [0 if i == 10**10 else i for i in objective]
x_ = [int(j) for j in range(len(objective))]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': 16})
fig, ax = plt.subplots(figsize=(12, 6))
# plt.figure(figsize=(10,8))
ax.bar(x_[1:], objective_plot[1:])
val_annot = objective_plot[1:]
x_annot = x_[1:]
for i in range(len(val_annot)):
    if val_annot[i] > 0:
        ax.annotate(str("{0:.5g}".format(100*(val_annot[i] - objective[0])/objective[0])) + '%', (x_annot[i], max(objective_plot)*1.03),
                    verticalalignment='top', horizontalalignment='center', fontsize=11)
    else:
        ax.annotate(str('inf'), (x_annot[i], max(objective_plot)/2), fontsize=12,
                    verticalalignment='top', horizontalalignment='center')
plt.hlines(objective_plot[0], x_[1], x_[-1], color='maroon', linestyles='--')
plt.xlabel('Run')
plt.xticks(x_[1:])
plt.ylabel('Objective Value')
plt.title('Progression of objective value')
# plt.legend(loc = 'best')
plt.rcdefaults()


# %%
n_source_list = [1 + int(round(random.uniform(5, 10))*i*5) for i in range(10)]
n_sinks_list = [1 + int(round(random.uniform(5, 10))*i*5) for i in range(10)]
iter_ = 0

comp_ = []
for n_sources in n_source_list:
    print('\n==========================================================================================================')
    print('Solving model for ' + str(n_sources) +
          ' sources and ' + str(n_sinks_list[iter_]) + ' sinks')
    print('\n==========================================================================================================')
    result = solve(n_sources=n_sources,
                   n_sinks=n_sinks_list[iter_], n_utility=4, n_transport=5)
    # y_ = [result['Prod'][i]['a'] for i in range(n_sources)]
    # print(result['Prod'][4]['a'])
    # print(y_)
    # x_ = [i for i in range(n_sources)]
    print(result['Comp'])
    comp_.append(result['Comp'])

    iter_ += 1


# %%


# def plot_comp()
plt.scatter(n_source_list, comp_)
plt.xlabel('# of sources')
plt.ylabel('Computational time (s)')
plt.show()

plt.plot(n_source_list, comp_)
plt.xlabel('# of source nodes')
plt.ylabel('computational time (s)')

# %%


# %%

# %%