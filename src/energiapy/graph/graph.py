
__author__ = "Rahul Kakodkar, Natasha Chrisandina"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Natasha Chrisandina",
               "Efstratios N. Pistikopoulos", "Mahmoud El-Halwagi", "Sergiy Butenko"]
__license__ = "Open"
__version__ = "1.0.0"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"


import pandas
import numpy 
import random
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)
from matplotlib.colors import ListedColormap
from typing import Tuple
import math

def distance(u_x: float, u_y: float, v_x: float, v_y: float, method: str = 'euclidean'):
    """Finds the distance: rectilinear/chebyshev/euclidean
    Args:
        u_x (float): x-coordinate of node a
        u_y (float): y-coordinate of node a
        v_x (float): x-coordinate of node b
        v_y (float): y-coordinate of node b
        method (str, optional): _description_. Defaults to 'euclidean'.
    Returns:
        float: _description_
    """
    if 'rectilinear':
        distance = abs(u_x-v_x) + abs(u_y-v_y)

    elif 'chebyshev':
        distance = max(abs(u_x-v_x) + abs(u_y-v_y))
    elif 'euclidean':
        distance = math.sqrt((u_x-v_x)**2 + (u_y-v_y)**2)
    return distance


def make_graph(n_sources: int, n_sinks: int, n_facilities: int, method: str = 'euclidean') -> Tuple[dict, dict, dict]:
    """Creates a graph based on number of sources and sink location
    Location co-ordinates are assigned at random
    distance method needs to be specified: euclidean, rectilinear, chebyshev
    Args:
        n_sources (int): number of source nodes
        n_sinks (int): number of sink nodes
        n_facilities (int): number of facility nodes
        method (str, optional): distance method. Defaults to 'euclidean'.
    Returns:
        Tuple[dict, dict, dict]: _description_
    """
    source_list = list(range(n_sources))  # supply node
    sink_list = list(range(n_sinks))  # demand sink
    facility_list = list(range(n_facilities))

    # electricity, gas, water
    criteria_utility_index = [i for i in source_list]
    critera_transport_index = [i for i in source_list]  # car, train

    sink_cost = [random.random() for i in sink_list]

    # locations sink location
    loc_sink_x = [random.random() for i in sink_list]
    loc_sink_y = [random.random() for i in sink_list]

    # locations nodes location
    loc_source_x = [random.random() for i in source_list]
    loc_source_y = [random.random() for i in source_list]

    loc_facility_x = [random.random() for i in facility_list]
    loc_facility_y = [random.random() for i in facility_list]

    # distance_dict = { (i,j) : distance(loc_source_x[i], loc_source_y[i], loc_sink_x[j], loc_sink_y[j], method) for i in source_list for j in sink_list}
    distance_feed_dict = {i: {j: distance(
        loc_source_x[i], loc_source_y[i], loc_facility_x[j], loc_facility_y[j], method) for j in facility_list} for i in source_list}
    distance_prod_dict = {i: {j: distance(
        loc_facility_x[i], loc_facility_y[i], loc_sink_x[j], loc_sink_y[j], method) for j in sink_list} for i in facility_list}

    source_dict = {i: [loc_source_x[i], loc_source_y[i]]for i in source_list}
    sink_dict = {i: [loc_sink_x[i], loc_sink_y[i]]for i in sink_list}
    facility_dict = {i: [loc_facility_x[i], loc_facility_y[i]]
                     for i in facility_list}

    return source_dict, sink_dict, facility_dict, distance_feed_dict, distance_prod_dict
