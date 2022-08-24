#%%
"""Clustering utilities
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
from itertools import product

from sklearn.cluster import AgglomerativeClustering
from sklearn.neighbors import NearestCentroid
from ..utils.math_utils import scaler, generate_connectivity_matrix, find_euclidean_distance
from ..components.scenario import Scenario
from ..components.temporal_scale import Temporal_scale
from ..components.network import Network
from ..components.location import Location
from typing import Union


def agg_hierarchial(scales: Temporal_scale, scale_level: int, periods: int, cost_factor: dict = None, capacity_factor: dict = None):
    
    
    cost_factor_df = pandas.DataFrame.from_dict(cost_factor)
    capacity_factor_df = pandas.DataFrame.from_dict(capacity_factor)

    df = pandas.concat([cost_factor_df, capacity_factor_df], axis = 1).reset_index(drop=True)

    parent_scale = scales.scale[scale_level]
    child_scale = scales.scale[scale_level+1]
    scaled_df = scaler(input_df= df, parent_scale = parent_scale, child_scale = child_scale)
    scaled_array = scaled_df.to_numpy()

    connectivity_matrix = generate_connectivity_matrix(parent_scale)
    ahc = AgglomerativeClustering(n_clusters = periods, affinity='euclidean', connectivity=connectivity_matrix,
                                    linkage='ward', compute_full_tree = True)
    clustered_array = ahc.fit_predict(scaled_array)
    cluster_labels = ahc.labels_  # get list of representative days

    nearest_centroid_array = NearestCentroid().fit(scaled_array, clustered_array).centroids_  # get the centroids of the clusters
    nearest_centroid_df = pandas.DataFrame(data=nearest_centroid_array, columns=[col for col in scaled_df])
    scaled_df['cluster_no'] = cluster_labels # add cluster numbers to the dataset
    nearest_centroid_df['cluster_no'] = scaled_df['cluster_no'].unique()
    
    euclidean_distance_list = []
    closest_to_centroid_df = pandas.DataFrame(columns=['period', 'rep_period', 'cluster_wt'])

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
    closest_to_centroid_df['period'] = (scaled_df['cluster_no'].value_counts().index.values)
    cluster_wts = [i for i in scaled_df['cluster_no'].value_counts()]
    closest_to_centroid_df['cluster_wt'] = cluster_wts
    
    list_ = []
    for i in closest_to_centroid_df['period']:
        list_.append(
            scaled_df.index.values[scaled_df['ED'] == scaled_df['ED'][scaled_df['cluster_no'] == i].min()][0])
    closest_to_centroid_df['rep_period'] = list_
    closest_to_centroid_df = closest_to_centroid_df.sort_values(
        by=['rep_period']).reset_index(drop=True)
    closest_to_centroid_df['period'] = list(
        range(len(closest_to_centroid_df['period'])))

    
    reduced_dicretization_list = list(scales.discretization_list)
    reduced_dicretization_list[scale_level] = periods
    reduced_temporal_scale = Temporal_scale(reduced_dicretization_list)
    reduced_scenario_scaleiter = [(i) for i in product(*[reduced_temporal_scale.scale[i] for i in reduced_temporal_scale.scale])]

    rep_dict = {scale: {'rep_period': (*scale[:scale_level], closest_to_centroid_df['rep_period'][closest_to_centroid_df['period'] == scale[scale_level]].values[0], *scale[scale_level+1:]) ,\
        'cluster_wt': closest_to_centroid_df['cluster_wt'][closest_to_centroid_df['period'] == scale[scale_level]].values[0]} for scale in reduced_scenario_scaleiter}

    wcss_sum = sum(i for i in scaled_df['ED'])/periods

    return rep_dict, wcss_sum, reduced_temporal_scale  
    
# TODO - call methods as a function 
# TODO - Handle multiple outputs

def reduce_scenario(scenario: Scenario, location: Location, periods:int, scale_level:int, method: str):
    
    if method == 'agg_hierarchial':
        rep_dict, wcss_sum, reduced_temporal_scale = agg_hierarchial(scenario.scales, scale_level= scale_level, periods= periods, \
            cost_factor= scenario.cost_factor[location.name], capacity_factor= scenario.capacity_factor[location.name])   
   
    reduced_scenario = Scenario(name = f"{scenario.name}_reduced", scales = reduced_temporal_scale, \
        network = scenario.network, expenditure_scale_level= scenario.expenditure_scale_level, 
        scheduling_scale_level= scenario.scheduling_scale_level, network_scale_level= scenario.network_scale_level, 
        demand_scale_level= scenario.demand_scale_level, label= f"{scenario.label}(reduced)")

    reduced_scenario_scaleiter = [(i) for i in product(*[reduced_temporal_scale.scale[i] for i in reduced_temporal_scale.scale])]
    reduced_scenario.capacity_factor = {location.name: {i.name: {j: scenario.capacity_factor[location.name][i.name][j] for j in rep_dict.keys()} for i in scenario.process_set if i.varying == True}}
    reduced_scenario.cost_factor = {location.name: {i.name: {j: scenario.cost_factor[location.name][i.name][j] for j in rep_dict.keys()} for i in scenario.resource_set if i.varying == True}}
    reduced_scenario.cluster_wt = {scale: rep_dict[scale]['cluster_wt'] for scale in reduced_scenario_scaleiter}
   
    return reduced_scenario

def agg_hierarchial_elbow(scales: Temporal_scale, scale_level: int, cost_factor: dict = None, capacity_factor: dict = None, range_list:list = None):
    if range_list is None:
        iter_ = scales.scale[scale_level]
    else:
        iter_ = range_list
    wcss_list = [agg_hierarchial(scales, scale_level= scale_level, periods= i,\
            cost_factor= cost_factor, capacity_factor= capacity_factor)[1]  for i in iter_]    
    return wcss_list

def dtw_cluster(series1:list, series2:list):
    """clusters time series data with disparate temporal resolution 
    using dynamic time warping (dtw)

    Args:
        series1 (list): time series 1
        series2 (list): time series 2

    Returns:
        matrix: cost matrix for dtw
    """       
    matrix = numpy.zeros((len(series1) + 1, len(series2) + 1))
    for i,j in product(range(1, len(series1)+1), range(1, len(series2) + 1)):
        matrix[i, j] = numpy.inf
    matrix[0,0] = 0
    for i,j in product(range(1, len(series1)+1), range(1, len(series2) + 1)):
        cost = abs(series1[i-1] - series2[j-1]) 
        prev = numpy.min([matrix[i-1, j], matrix[i, j-1], matrix[i-1, j-1]]) 
        matrix[i,j] = cost + prev
    return matrix


def find_dtw_path(matrix:numpy.ndarray)-> list:
    """finds optimal warping path from a dynamic time warping cost matrix 

    Args:
        matrix (numpy.ndarray): cost matrix from application of dtw

    Returns:
        list: optimal path with list of coordinates
    """
    path  = []
    i,j = len(matrix) -1, len(matrix[0]) -1
    path.append([i,j])
    while i > 0 and j > 0:
        index_min = numpy.argmin([matrix[i-1, j], matrix[i, j-1], matrix[i-1, j-1]])
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
# %%


# %%
