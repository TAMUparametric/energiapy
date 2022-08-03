"""Cost scenario data class  
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from dataclasses import dataclass
from ..components.network import Network
from ..components.temporal_scale import Temporal_scale
from ..model.pyomo_cons import *
from typing import Union

@dataclass
class Scenario:
    """creates a scenario dataclass object
    Args:
        name (str): ID
        network (network): network object with the locations, transport linakges, and processes (with resources and materials)
        scales (temporal_scale): scales of the problem 
        expenditure_scale_level (int, optional): scale for resource purchase. Defaults to 0.
        scheduling_scale_level (int, optional): scale of production and inventory scheduling. Defaults to 0.
        network_scale_level (int, optional): scale for network decisions such as facility location. Defaults to 0.
        demand_scale_level (int, optional): scale for meeting specific demand for resource. Defaults to 0.
        label (str, optional): descriptive label. Defaults to ''.
    """
    name: str 
    scales: Temporal_scale 
    network: Union[Network, Location] = None
    expenditure_scale_level: int = 0
    scheduling_scale_level: int = 0
    network_scale_level: int = 0
    demand_scale_level: int = 0 
    label: str = ''

    def __post_init__(self):    

        if type(self.network) == Location:
            self.transport_set = None
            self.source_locations = None
            self.sink_locations = None
            self.transport_dict = None
            self.transport_avail_dict = None
            self.trans_max = None
            self.trans_loss = None 
            self.trans_cost = None
            self.trans_emit =  None
            self.distance_dict = None
            self.location_set = {self.network}   
            
        else:
            self.transport_set = set().union(*self.network.transport_dict.values())
            self.source_locations = self.network.source_locations
            self.sink_locations = self.network.sink_locations
            self.transport_dict = self.network.transport_dict
            self.transport_avail_dict = self.network.transport_avail_dict
            self.location_set = set(self.source_locations + self.sink_locations)         
            self.trans_max = {j.name: j.trans_max for j in self.transport_set}
            self.trans_loss = {j.name: j.trans_loss for j in self.transport_set} 
            self.trans_cost = {j.name: j.trans_cost for j in self.transport_set}
            self.trans_emit =  {j.name: j.trans_emit for j in self.transport_set} 
            self.distance_dict = self.network.distance_dict
            
        self.process_set = set().union(*[i.processes for i in self.location_set if i.processes is not None])
        self.resource_set = set().union(*[i.resources for i in self.location_set if i.resources is not None])
        self.material_set = set().union(*[i.materials for i in self.location_set if i.materials is not None])
        self.conversion = {i.name: {j.name: i.conversion[j] if j in i.conversion.keys()\
            else 0 for j in self.resource_set} for i in self.process_set}
        self.prod_max = {i.name: {j.name: j.prod_max for j in i.processes} for i in self.location_set}
        self.prod_min = {i.name: {j.name: j.prod_min for j in i.processes} for i in self.location_set}
        self.cons_max = {i.name: {j.name: j.cons_max for j in i.resources} for i in self.location_set}
        self.store_max = {i.name: {j.name: j.store_max for j in i.resources} for i in self.location_set}
        self.store_min = {i.name: {j.name: j.store_min for j in i.resources} for i in self.location_set}
        self.capacity_factor = {i.name: i.capacity_factor for i in self.location_set}  
        self.loc_res_dict =  {i.name: {j.name for j in i.resources} for i in self.location_set}
        self.loc_pro_dict =  {i.name: {j.name for j in i.processes} for i in self.location_set}
        self.cost_factor =  {i.name: i.cost_factor for i in self.location_set}
        self.price = {i.name: i.resource_price for i in self.location_set}
        self.capex_dict = {i.name: i.capex for i in self.process_set}
        self.fopex_dict = {i.name: i.fopex for i in self.process_set}
        self.vopex_dict = {i.name: i.vopex for i in self.process_set}
        self.demand_dict = {i.name: {j.name: i.demand[j] for j in i.demand} for i in self.location_set}
        self.land_dict = {i.name: i.land for i in self.process_set}

    def reduce_scenario(self, periods:int, method:str = 'agg_hierarchial'):
        
        if periods == 


        return reduced_scenario
        
    def __repr__(self):
        return self.name



    

#%%




def reduce_scenario(varying_process_df: pandas.DataFrame, varying_cost_df: pandas.DataFrame, red_scn_method: str, rep_days_no: int) -> dict:
    """Reduces scenario to set of representative days
    days closest to the cluster centroids are chosen
    red_scn_methods available: Agglomorative Hierarchial Clustering (AHC)
    output dictionary contains representative days and their corresponding cluster weights

    Args:
        varying_process_df (pandas.DataFrame): contains varying process paramters (e.g.: conversion factors)
        varying_resource_df (pandas.DataFrame): contains varying resource paramters (e.g.: cost)
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

        scaled_df = pandas.DataFrame()

        # standardize the values for all process and resources
        for var in varying_process:
            scaled_iter = scaler(varying_process_df, var)
            scaled_df = pandas.concat([scaled_df, scaled_iter], axis=1)

        for var in varying_resource:
            scaled_iter = scaler(varying_resource_df, var)
            scaled_df = pandas.concat([scaled_df, scaled_iter], axis=1)

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
            nearest_centroid_df = pandas.DataFrame(data=nearest_centroid_array, columns=[
                                               col for col in scaled_df])

            # add cluster numbers to the dataset
            scaled_df['cluster_no'] = cluster_labels
            # add cluster numbers to the dataset
            nearest_centroid_df['cluster_no'] = scaled_df['cluster_no'].unique()
            euclidean_distance_list = []
            # closest actual days to the cluster centroids
            closest_to_centroid_df = pandas.DataFrame(
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


def ahc_elbow(varying_process_df: pandas.DataFrame, varying_resource_df: pandas.DataFrame, red_scn_method: str, rep_days_no: int) -> dict:
    """Reduces scenario to set of representative days
    days closest to the cluster centroids are chosen
    red_scn_methods available: Agglomorative Hierarchial Clustering (AHC)
    output dictionary contains representative days and their corresponding cluster weights

    Args:
        varying_process_df (pandas.DataFrame): contains varying process paramters (e.g.: conversion factors)
        varying_resource_df (pandas.DataFrame): contains varying resource paramters (e.g.: cost)
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

        scaled_df = pandas.DataFrame()

        # standardize the values for all process and resources
        for var in varying_process:
            scaled_iter = scaler(varying_process_df, var)
            scaled_df = pandas.concat([scaled_df, scaled_iter], axis=1)

        for var in varying_resource:
            scaled_iter = scaler(varying_resource_df, var)
            scaled_df = pandas.concat([scaled_df, scaled_iter], axis=1)

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
            nearest_centroid_df = pandas.DataFrame(data=nearest_centroid_array, columns=[
                                               col for col in scaled_df])

            # add cluster numbers to the dataset
            scaled_df['cluster_no'] = cluster_labels
            # add cluster numbers to the dataset
            nearest_centroid_df['cluster_no'] = scaled_df['cluster_no'].unique()
            euclidean_distance_list = []
            # closest actual days to the cluster centroids
            closest_to_centroid_df = pandas.DataFrame(
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