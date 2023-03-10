"""Clustering with Dynamic Time Warping (DTW)
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"


import pandas
import numpy
from itertools import product
from typing import Union, Tuple
from ..components.scenario import Scenario
from ..components.resource import Resource
from ..components.process import Process
from ..components.temporal_scale import Temporal_scale
from ..components.network import Network
from ..components.location import Location
import matplotlib.pyplot as plt


def dynamic_warping(source_scenario: Scenario, target_scenario: Scenario, \
    scale_level: int, include: list, aspect: Union[Resource, Process], reference_dict: dict = None):
    
    source_location = list(source_scenario.location_set)[0] 
    target_location = list(target_scenario.location_set)[0]

    if Include.cost in include:
        source_series = list(source_scenario.cost_factor[source_location.name][aspect.name].values())
        target_series = list(target_scenario.cost_factor[target_location.name][aspect.name].values())
        
        reference_keys = target_scenario.cost_factor[target_location.name][aspect.name].keys()
    
    elif Include.capacity in include:    
        source_series = list(source_scenario.capacity_factor[source_location.name][aspect.name].values())
        target_series = list(target_scenario.capacity_factor[target_location.name][aspect.name].values())
        
        reference_keys = target_scenario.capacity_factor[target_location.name][aspect.name].keys()
        

    elif Include.demand in include:
        source_series = list(source_scenario.demand_factor[source_location.name][aspect.name].values())
        target_series = list(target_scenario.demand_factor[target_location.name][aspect.name].values())
        
        reference_keys = target_scenario.demand_factor[target_location.name][aspect.name].keys()
        
    matrix = dynamic_warping_matrix(series1= source_series, series2= target_series)
    
    path = dynamic_warping_path(matrix= matrix)
    
    path = [i for i in path if i[0] != 0] #remove zeroth value
    

    
    #collects the x and y coordinates of path as separate lists
    x_ = [path[i][0] -1 for i in range(len(path))] 
    y_ = [path[i][1] -1 for i in range(len(path))] 
    
    
    #reverse the coordinates 
    x_.reverse() 
    y_.reverse()
    
    # xr = x_[:-1]
    # yr = y_[:-1]
    
    
    i_list = list(range(len(target_series)))
    
    
    j_list = list(reference_keys)
    source_values = [source_series[i] for i in x_]
 
    
    target_values = [target_series[i] for i in y_]

    # print(len(target_values))


    # reduced_temporal_scale = Temporal_scale(discretization_list=[1, len(target_values), 24])
    
    # iter_temporal_scale = target_scenario.scales
    
    reduced_temporal_scale = target_scenario.scales
    
    reduced_scenario_scaleiter = [(i) for i in product(*[reduced_temporal_scale.scale[i] for i in reduced_temporal_scale.scale])]
    
    
    #TODO Check this 
    counts = {j:  y_.count(i) for i,j in zip(i_list, j_list)}
    
    # print(counts)
    
    # #TODO find actual rep_day
    # if reference_dict is not None:
    rep_dict = {j: {'rep_period': reference_dict[j]['rep_period'], 'cluster_wt': counts[j[:scale_level]]} for j in reduced_scenario_scaleiter}
    #     # rep_dict = {j: {'rep_period': j, 'cluster_wt': 1} for j in reduced_scenario_scaleiter}
    # else:
    # rep_dict = {j: {'rep_period': j, 'cluster_wt': counts[j[:scale_level]]} for j in reduced_scenario_scaleiter}
            
    
    numpy.info_dict = {
        'matrix': matrix,
        'path': path,
        'input_data': {'source': source_series, 'target': target_series},
        'output_data': {'source': source_values, 'target': target_values}  
    }
    
    return rep_dict, reduced_temporal_scale, numpy.info_dict


