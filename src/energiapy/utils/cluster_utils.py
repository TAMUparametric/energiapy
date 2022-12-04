# %%
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
from enum import Enum, auto


class Clustermethod(Enum):
    agg_hierarchial = auto()
    agg_hierarchial_elbow = auto()
    dynamic_warping = auto()
    dynamic_warping_path = auto()
    

def agg_hierarchial(scales: Temporal_scale, scale_level: int, periods: int, cost_factor: dict = None, capacity_factor: dict = None, demand_factor: dict = None):
    """perform agglomerative hierarchial clustering over time-series data

    Args:
        scales (Temporal_scale): scales of the problme
        scale_level (int): scale level to cluster at
        periods (int): number of clustering periods
        cost_factor (dict, optional): factor to account for varying cost factors. Defaults to None.
        capacity_factor (dict, optional): factor to account for varying production capacity. Defaults to None.

    Returns:
        _type_: _description_
    """

    cost_factor_df = pandas.DataFrame(cost_factor)
    capacity_factor_df = pandas.DataFrame(capacity_factor)
    demand_factor_df = pandas.DataFrame(demand_factor)
   
    df = pandas.concat([cost_factor_df, capacity_factor_df, demand_factor_df],
                       axis=1).reset_index(drop=True) # makes a common data frame with all different data sets

    parent_scale = scales.scale[scale_level-1]
    scale = scales.scale[scale_level] # the scale for which to cluster, e.g.: day
    child_scale = scales.scale[scale_level+1] # the lower scale which is nested under the parent scale, e.g. : hour

    split_df = numpy.array_split(df, len(parent_scale))
    # output_df = pandas.DataFrame()
    # rep_dict_iter = {i: 0 for i in range(len(parent_scale))} 
    rep_dict_iter = {}    
       
    
    #creates a new Temporal_scale object on the reduced scale
    reduced_dicretization_list = list(scales.discretization_list)
    reduced_dicretization_list[scale_level] = periods
    reduced_temporal_scale = Temporal_scale(reduced_dicretization_list)
    reduced_scenario_scaleiter = numpy.array_split(reduced_temporal_scale.scale_iter(), len(parent_scale))
    
    for parent_iter in range(len(parent_scale)):
        
        scaled_df = scaler(input_df=split_df[parent_iter], scale = scale,
                        child_scale=child_scale) # reshapes the data frame, e.g. instead of 8760 linear data points, creates a 365x24 matrix
        scaled_array = scaled_df.to_numpy() # makes an array instead of a dataframe, as raw data is better handled in other libraries, removes dependencies 

        connectivity_matrix = generate_connectivity_matrix(scale_len= len(scale)) # make a matrix to ensure that chronology is maintained 
        ahc = AgglomerativeClustering(n_clusters=periods, affinity='euclidean', connectivity=connectivity_matrix,
                                    linkage='ward', compute_full_tree=True)
        clustered_array = ahc.fit_predict(scaled_array)
        cluster_labels = ahc.labels_  # get list of representative days

        nearest_centroid_array = NearestCentroid().fit(
            scaled_array, clustered_array).centroids_  # get the centroids of the clusters
        nearest_centroid_df = pandas.DataFrame(
            data=nearest_centroid_array, columns=[col for col in scaled_df])
        # add cluster numbers to the dataset
        scaled_df['cluster_no'] = cluster_labels
        nearest_centroid_df['cluster_no'] = scaled_df['cluster_no'].unique()

        euclidean_distance_list = []
        closest_to_centroid_df = pandas.DataFrame(
            columns=['period', 'rep_period', 'cluster_wt'])

        for cluster_no in nearest_centroid_df['cluster_no']:
            # -1 skips cluster_no row
            cluster_array = scaled_df[scaled_df['cluster_no']
                                    == cluster_no].iloc[:, :-1].to_numpy()
            centroid_array = nearest_centroid_df[nearest_centroid_df['cluster_no']
                                                == cluster_no].iloc[:, :-1].to_numpy()
            centroid = centroid_array.tolist()[0]
            for cluster in cluster_array: # finding euclidean distance from each data point to centroid 
                cluster_point = [cluster for cluster in cluster]
                euclidean_distance = find_euclidean_distance(
                    cluster_point, centroid)
                euclidean_distance_list.append(euclidean_distance)

        scaled_df['ED'] = euclidean_distance_list #find the actual day closest to centroid
        closest_to_centroid_df['period'] = (
            scaled_df['cluster_no'].value_counts().index.values)
        cluster_wts = [i for i in scaled_df['cluster_no'].value_counts()]
        closest_to_centroid_df['cluster_wt'] = cluster_wts

        list_ = []
        for i in closest_to_centroid_df['period']:
            list_.append(
                scaled_df.index.values[scaled_df['ED'] == scaled_df['ED'][scaled_df['cluster_no'] == i].min()][0])#find the actual day closest to centroid
        closest_to_centroid_df['rep_period'] = list_
        closest_to_centroid_df = closest_to_centroid_df.sort_values(
            by=['rep_period']).reset_index(drop=True)
        closest_to_centroid_df['period'] = list(
            range(len(closest_to_centroid_df['period'])))

        current_iter = [ tuple(i) for i in reduced_scenario_scaleiter[parent_iter]]
        
        output_dict= {scale: {'rep_period': (parent_iter, \
            closest_to_centroid_df['rep_period'][closest_to_centroid_df['period'] == scale[scale_level]].values[0], *scale[scale_level+1:]),
                            'cluster_wt': closest_to_centroid_df['cluster_wt'][closest_to_centroid_df['period'] == scale[scale_level]].values[0]}\
                                for scale in current_iter}

        rep_dict_iter = {**rep_dict_iter, **output_dict}
    # rep_dict = {rep_dict_iter[i].values() for i}

    # puts all relevant data in a dictionary

    
    # wcss_sum = sum(i for i in scaled_df['ED'])/periods # collects the error data

    return rep_dict_iter, reduced_temporal_scale

# TODO - call methods as a function
# TODO  - Handle multiple outputs


def agg_hierarchial_elbow(scales: Temporal_scale, scale_level: int, cost_factor: dict = None, capacity_factor: dict = None, range_list: list = None) -> list:
    """calculate the error of a particular clustering method over a range of different cluster periods

    Args:
        scales (Temporal_scale): scales of the problem
        scale_level (int): scale over which to cluster
        cost_factor (dict, optional): factor for varying resource cost. Defaults to None.
        capacity_factor (dict, optional): factor for varying production capacities. Defaults to None.
        range_list (list, optional): range of clustering days over which to compute error. Defaults to None.

    Returns:
        list: error for each cluster period returned as a list
    """
    if range_list is None:
        iter_ = scales.scale[scale_level]
    else:
        iter_ = range_list
    wcss_list = [agg_hierarchial(scales, scale_level=scale_level, periods=i,
                                 cost_factor=cost_factor, capacity_factor=capacity_factor)[1] for i in iter_]
    return wcss_list


def dynamic_warping(series1: list, series2: list):
    """clusters time series data with disparate temporal resolution 
    using dynamic time warping (dtw)

    Args:
        series1 (list): time series 1
        series2 (list): time series 2

    Returns:
        matrix: cost matrix for dtw
    """
    matrix = numpy.zeros((len(series1) + 1, len(series2) + 1))
    for i, j in product(range(1, len(series1)+1), range(1, len(series2) + 1)):
        matrix[i, j] = numpy.inf
    matrix[0, 0] = 0
    for i, j in product(range(1, len(series1)+1), range(1, len(series2) + 1)):
        cost = abs(series1[i-1] - series2[j-1])
        prev = numpy.min([matrix[i-1, j], matrix[i, j-1], matrix[i-1, j-1]])
        matrix[i, j] = cost + prev
    return matrix


def dynamic_warping_path(matrix: numpy.ndarray) -> list:
    """finds optimal warping path from a dynamic time warping cost matrix 

    Args:
        matrix (numpy.ndarray): cost matrix from application of dtw

    Returns:
        list: optimal path with list of coordinates
    """
    path = []
    i, j = len(matrix) - 1, len(matrix[0]) - 1
    path.append([i, j])
    while i > 0 and j > 0:
        index_min = numpy.argmin(
            [matrix[i-1, j], matrix[i, j-1], matrix[i-1, j-1]])
        if index_min == 0:
            i = i - 1
        if index_min == 1:
            j = j - 1
        if index_min == 2:
            i = i - 1
            j = j - 1
        path.append([i, j])
    # path.append([0,0])
    return path



def reduce_scenario(scenario: Scenario, location: Location, periods: int, scale_level: int, method: Clustermethod) -> Scenario:
    """reduce scenario using a particular method

    Args:
        scenario (Scenario): full-scale scenario
        location (Location): location in scenario to cluster
        periods (int): number of clustering intervals
        scale_level (int): scale at which to cluster
        method (Clustermethod): available clustering methods

    Returns:
        Scenario: reduced scenario
    """

    if method is Clustermethod.agg_hierarchial:
        rep_dict, reduced_temporal_scale= agg_hierarchial(scenario.scales, scale_level=scale_level, periods=periods,
                                                                     cost_factor=scenario.cost_factor[location.name], capacity_factor=scenario.capacity_factor[location.name],
                                                                     demand_factor = scenario.demand_factor[location.name])

    reduced_scenario = Scenario(name=f"{scenario.name}_reduced", scales=reduced_temporal_scale,
                                network=scenario.network, expenditure_scale_level=scenario.expenditure_scale_level,
                                scheduling_scale_level=scenario.scheduling_scale_level, network_scale_level=scenario.network_scale_level,
                                demand_scale_level=scenario.demand_scale_level, label=f"{scenario.label}(reduced)")

    reduced_scenario_scaleiter = [(i) for i in product(
        *[reduced_temporal_scale.scale[i] for i in reduced_temporal_scale.scale])]
    reduced_scenario.capacity_factor = {location.name: {i: {
        j: scenario.capacity_factor[location.name][i][rep_dict[j]['rep_period']] for j in rep_dict.keys()} for i in list(scenario.capacity_factor[location.name])}}
    reduced_scenario.cost_factor = {location.name: {i: {
        j: scenario.cost_factor[location.name][i][rep_dict[j]['rep_period']] for j in rep_dict.keys()} for i in list(scenario.cost_factor[location.name])}}
    reduced_scenario.demand_factor = {location.name: {i: {
        j: scenario.demand_factor[location.name][i][rep_dict[j]['rep_period']] for j in rep_dict.keys()} for i in list(scenario.demand_factor[location.name])}}
    reduced_scenario.cluster_wt = {
        scale: rep_dict[scale]['cluster_wt'] for scale in reduced_scenario_scaleiter}
    
    return reduced_scenario
# %%


# %%
