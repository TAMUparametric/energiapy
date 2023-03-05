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
from numpy import polyfit, array_split, zeros, inf, min, argmin, ndarray, arange
from itertools import product
from typing import Union
from sklearn.cluster import AgglomerativeClustering
from sklearn.neighbors import NearestCentroid
from ..utils.math_utils import scaler, generate_connectivity_matrix, find_euclidean_distance
from ..components.scenario import Scenario
from ..components.resource import Resource
from ..components.process import Process
from ..components.temporal_scale import Temporal_scale
from ..components.network import Network
from ..components.location import Location
from enum import Enum, auto
import matplotlib.pyplot as plt

class Clustermethod(Enum):
    agg_hierarchial = auto()
    dynamic_warping = auto()
    
class Include(Enum):
    cost = auto()
    demand = auto()
    capacity = auto()

    

def agg_hierarchial(scales: Temporal_scale, scale_level: int, periods: int, include:list, cost_factor: dict = None, \
    capacity_factor: dict = None, demand_factor: dict = None):
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
    if Include.cost in include:
        # cost_factor_df = pandas.DataFrame(cost_factor)
        cost_factor_df = pandas.concat([pandas.DataFrame(cost_factor[i]) for i in cost_factor.keys()], axis = 1)
    else:
        cost_factor_df = None
    
    if Include.capacity in include:    
        # capacity_factor_df = pandas.DataFrame(capacity_factor)
        capacity_factor_df = pandas.concat([pandas.DataFrame(capacity_factor[i]) for i in capacity_factor.keys()], axis = 1)
        
    else:
        capacity_factor_df = None
    
    if Include.demand in include:
        demand_factor_df = pandas.concat([pandas.DataFrame(demand_factor[i]) for i in demand_factor.keys()], axis = 1)
        # demand_factor_df = pandas.DataFrame(demand_factor)
    else:
        demand_factor_df = None
    
 
    
    df = pandas.concat([cost_factor_df, capacity_factor_df, demand_factor_df],
                       axis=1).reset_index(drop=True) # makes a common data frame with all different data sets
    df.columns = arange(len(df.columns))
    parent_scale = scales.scale[scale_level-1]
    scale = scales.scale[scale_level] # the scale for which to cluster, e.g.: day
    
    child_scale = scales.scale[scale_level+1] # the lower scale which is nested under the parent scale, e.g. : hour
        
    split_df = array_split(df, len(parent_scale))
    # output_df = pandas.DataFrame()
    # rep_dict_iter = {i: 0 for i in range(len(parent_scale))} 
    
    rep_dict_iter = {}    
       
    
    #creates a new Temporal_scale object on the reduced scale
    reduced_dicretization_list = list(scales.discretization_list)
    reduced_dicretization_list[scale_level] = periods
    reduced_temporal_scale = Temporal_scale(reduced_dicretization_list)

    reduced_scenario_scaleiter = array_split(reduced_temporal_scale.scale_iter(scale_level= scale_level +1), len(parent_scale))
    for parent_iter in range(len(parent_scale)):
        
        if len(df) == len(parent_scale)*len(scale):
            scaled_df = scaler(input_df=split_df[parent_iter], scale = scale)
        else:
            scaled_df = scaler(input_df=split_df[parent_iter], scale = scale,
                        child_scale=child_scale) # reshapes the data frame, e.g. instead of 8760 linear data points, creates a 365x24 matrix
        
        scaled_array = scaled_df.to_numpy() # makes an array instead of a dataframe, as raw data is better handled in other libraries, removes dependencies 

        connectivity_matrix = generate_connectivity_matrix(scale_len= len(scale)) # make a matrix to ensure that chronology is maintained 
        ahc = AgglomerativeClustering(n_clusters=periods, metric='euclidean', connectivity=connectivity_matrix,
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

        rep_dict_iter = {**rep_dict_iter, **output_dict} #V. important: clusters each index in the parent scale individually and combines dict
    # rep_dict = {rep_dict_iter[i].values() for i}

    # puts all relevant data in a dictionary

    
    wcss_sum = sum(i for i in scaled_df['ED'])/periods # collects the error data

    info_dict = {
        'wcss_sum': wcss_sum
    }
    
    return rep_dict_iter, reduced_temporal_scale, info_dict

# TODO - call methods as a function
# TODO  - Handle multiple outputs


def agg_hierarchial_elbow(scenario: Scenario, scale_level: int, include: list, range_list: list = None) -> list:
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
        iter_ = scenario.scales.scale[scale_level]
    else:
        iter_ = range_list
    wcss_list  = []
    for i in iter_:
        rep_dict_iter, reduced_temporal_scale, info_dict = agg_hierarchial(scales = scenario.scales, scale_level=scale_level, periods=i,
                                 cost_factor= scenario.cost_factor, capacity_factor= scenario.capacity_factor, \
                                     demand_factor= scenario.demand_factor, include= include)
        wcss_list.append(info_dict['wcss_sum'])
        
        
    # wcss_list = [agg_hierarchial(scales = scenario.scales, scale_level=scale_level, periods=i,
    #                              cost_factor= scenario.cost_factor[location.name], capacity_factor= scenario.capacity_factor[location.name], \
    #                                  demand_factor= scenario.demand_factor[location.name], include= include) for i in iter_]
    
    
    theta  = polyfit(x= range_list,  y= wcss_list, deg=3)
    # theta  = np.polyfit(x=[i+10 for i in range(70)],  y= wcss1, deg=3)

    # y_line = [theta[2] + theta[1] * pow(x, 1) + theta[0] * pow(x, 2) for x in [i+10 for i in range(70)]]
    y_line = [theta[3] + theta[2] * pow(x, 1) + theta[1] * pow(x, 2) + theta[0] * pow(x, 3) for x in range_list]

    # y_line = theta[3] + theta[2] * pow(xdata, 1) + theta[1] * pow(xdata, 2) +  theta[0] * pow(xdata, 3)

    fig, ax = plt.subplots(figsize=(8, 6))
    x = range_list
    ax.plot(x, y_line)
    ax.scatter(x, wcss_list, color = 'indianred')
    included = ''.join([str(i).split('Include.')[1] + str(' ') for i in include])
    
    plt.title(f'Clustering using AHC for Houston for {included}')
    plt.xlabel('Cluster Size')
    plt.ylabel('WCSS')
    plt.grid(alpha=0.3)
    fig.show()
    
    
    return wcss_list


def dynamic_warping_matrix(series1: list, series2: list):
    """clusters time series data with disparate temporal resolution 
    using dynamic time warping (dtw)

    Args:
        series1 (list): time series 1
        series2 (list): time series 2

    Returns:
        matrix: cost matrix for dtw
    """
    matrix = zeros((len(series1) + 1, len(series2) + 1))
    for i, j in product(range(1, len(series1)+1), range(1, len(series2) + 1)):
        matrix[i, j] = inf
    matrix[0, 0] = 0
    for i, j in product(range(1, len(series1)+1), range(1, len(series2) + 1)):
        cost = abs(series1[i-1] - series2[j-1])
        prev = min([matrix[i-1, j], matrix[i, j-1], matrix[i-1, j-1]])
        matrix[i, j] = cost + prev
    return matrix



def dynamic_warping_path(matrix: ndarray) -> list:
    """finds optimal warping path from a dynamic time warping cost matrix 

    Args:
        matrix (ndarray): cost matrix from application of dtw

    Returns:
        list: optimal path with list of coordinates
    """
    path = []
    i, j = len(matrix) - 1, len(matrix[0]) - 1
    path.append([i, j])
    while i > 0 and j > 0:
        index_min = argmin(
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
            
    
    info_dict = {
        'matrix': matrix,
        'path': path,
        'input_data': {'source': source_series, 'target': target_series},
        'output_data': {'source': source_values, 'target': target_values}  
    }
    
    return rep_dict, reduced_temporal_scale, info_dict



def reduce_scenario(scenario: Scenario, method: Clustermethod, include: list, \
    scale_level: int = None, source_scenario: Scenario = None, target_scenario: Scenario= None, aspect: Union[Resource, Process] = None, \
        location: Location = None, periods: int = None, reference_dict: dict = None) -> Scenario:
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
        rep_dict, reduced_temporal_scale, info_dict = agg_hierarchial(scenario.scales, scale_level=scale_level, periods=periods,
                                                                     cost_factor=scenario.cost_factor, capacity_factor=scenario.capacity_factor,
                                                                     demand_factor = scenario.demand_factor, include = include)
        

        
    if method is Clustermethod.dynamic_warping:
        rep_dict, reduced_temporal_scale, info_dict = dynamic_warping(source_scenario = source_scenario, \
            target_scenario= target_scenario, include= include, aspect= aspect, scale_level= scale_level, reference_dict = reference_dict)

    
    reduced_scenario_scaleiter = [(i) for i in product(
        *[reduced_temporal_scale.scale[i] for i in reduced_temporal_scale.scale])]
    
    # cluster_wt = {scale: rep_dict[scale]['cluster_wt'] for scale in reduced_scenario_scaleiter}    
                
        
    reduced_scenario = Scenario(name=f"{scenario.name}_reduced", scales=reduced_temporal_scale,
                                network=scenario.network, expenditure_scale_level=scenario.expenditure_scale_level,
                                scheduling_scale_level=scenario.scheduling_scale_level, network_scale_level=scenario.network_scale_level,
                                demand_scale_level=scenario.demand_scale_level, \
                                    label=f"{scenario.label}(reduced)")

    len_ = len(list(list(scenario.cost_factor[location.name].values())[0].keys())[0])
    reduced_scenario.cost_factor = {location.name: {i: {
        j[:len_]: scenario.cost_factor[location.name][i][rep_dict[j]['rep_period'][:len_]] \
            for j in list(rep_dict.keys())} for i in list(scenario.cost_factor[location.name])}}

    len_ = len(list(list(scenario.capacity_factor[location.name].values())[0].keys())[0])
    reduced_scenario.capacity_factor = {location.name: {i: {
        j[:len_]: scenario.capacity_factor[location.name][i][rep_dict[j]['rep_period'][:len_]] \
            for j in list(rep_dict.keys())} for i in list(scenario.capacity_factor[location.name])}}

    len_ = len(list(list(scenario.demand_factor[location.name].values())[0].keys())[0])
    reduced_scenario.demand_factor = {location.name: {i: {
        j[:len_]: scenario.demand_factor[location.name][i][rep_dict[j]['rep_period'][:len_]] \
            for j in list(rep_dict.keys())} for i in list(scenario.demand_factor[location.name])}}

    # reduced_scenario.
    
    # print(cluster_wt)
   
    
    if reference_dict is not None:
        reduced_scenario.cluster_wt = {scale: reference_dict[scale]['cluster_wt'] for scale in reduced_scenario_scaleiter}
    
    else:    
    
        reduced_scenario.cluster_wt = {scale: rep_dict[scale]['cluster_wt'] for scale in reduced_scenario_scaleiter}

    
    return reduced_scenario, rep_dict, info_dict
# %%


# %%
