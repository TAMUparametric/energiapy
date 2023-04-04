"""Clustering with Agglomerative Hierarchial Clustering (AHC)
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"


from enum import Enum, auto
from typing import Tuple

import matplotlib.pyplot as plt
import numpy
import pandas
from sklearn.cluster import AgglomerativeClustering
from sklearn.neighbors import NearestCentroid

from ..components.scenario import Scenario
from ..components.temporal_scale import TemporalScale
from ..utils.math_utils import (
    find_euclidean_distance,
    generate_connectivity_matrix,
    scaler,
)


class IncludeAHC(Enum):
    """
    What to include in agglomerative hierarchial clustering
    """
    COST = auto()
    """
    Include cost factors (varying resource price)
    """
    DEMAND = auto()
    """
    Include demand factors (varying resource demand)
    """
    CAPACITY = auto()
    """
    Include capacity factors (varying process capacities)
    """


class Fit(Enum):
    """
    Fit a spline
    """
    POLY2 = auto()
    """
    2nd order fit
    """
    POLY3 = auto()
    """
    3rd order fit
    """


def agg_hierarchial(scales: TemporalScale, scale_level: int, periods: int, include: list, price_factor: dict = None,
                    capacity_factor: dict = None, demand_factor: dict = None):
    """perform agglomerative hierarchial clustering over time-series data

    Args:
        scales (TemporalScale): scales of the problme
        scale_level (int): scale level to cluster at
        periods (int): number of clustering periods
        price_factor (dict, optional): factor for varying cost factors. Defaults to None.
        capacity_factor (dict, optional): factor for varying production capacity. Defaults to None.
        demand_factor (dict, optional): factor for varying resource demand. Defaults to None.

    Returns:
        _type_: _description_
    """

    if IncludeAHC.COST in include:
        # price_factor_df = pandas.DataFrame(price_factor)
        price_factor_df = pandas.concat(
            [pandas.DataFrame(price_factor[i]) for i in price_factor.keys()], axis=1)
    else:
        price_factor_df = None

    if IncludeAHC.CAPACITY in include:
        # capacity_factor_df = pandas.DataFrame(capacity_factor)
        capacity_factor_df = pandas.concat(
            [pandas.DataFrame(capacity_factor[i]) for i in capacity_factor.keys()], axis=1)

    else:
        capacity_factor_df = None

    if IncludeAHC.DEMAND in include:
        demand_factor_df = pandas.concat(
            [pandas.DataFrame(demand_factor[i]) for i in demand_factor.keys()], axis=1)
        # demand_factor_df = pandas.DataFrame(demand_factor)
    else:
        demand_factor_df = None

    combined_df = pandas.concat([price_factor_df, capacity_factor_df, demand_factor_df],
                                axis=1).reset_index(drop=True)
    # makes a common data frame with all different data sets
    combined_df.columns = numpy.arange(len(combined_df.columns))
    parent_scale = scales.scale[scale_level-1]
    # the scale for which to cluster, e.g.: day
    scale = scales.scale[scale_level]

    # the lower scale which is nested under the parent scale, e.g. : hour
    child_scale = scales.scale[scale_level+1]

    split_df = numpy.array_split(combined_df, len(parent_scale))
    # output_df = pandas.DataFrame()
    # rep_dict_iter = {i: 0 for i in range(len(parent_scale))}

    rep_dict_iter = {}

    # creates a new TemporalScale object on the reduced scale
    reduced_dicretization_list = list(scales.discretization_list)
    reduced_dicretization_list[scale_level] = periods
    reduced_temporal_scale = TemporalScale(reduced_dicretization_list)

    reduced_scenario_scaleiter = numpy.array_split(
        reduced_temporal_scale.scale_iter(scale_level=scale_level + 1), len(parent_scale))
    for parent_iter in range(len(parent_scale)):

        if len(combined_df) == len(parent_scale)*len(scale):
            scaled_df = scaler(input_df=split_df[parent_iter], scale=scale)
        else:
            scaled_df = scaler(input_df=split_df[parent_iter], scale=scale,
                               child_scale=child_scale)
        # reshapes the data frame, e.g. instead of 8760 linear data points, creates a 365x24 matrix

        # makes an array instead of a dataframe, as raw data is better handled in other libraries,
        # removes dependencies
        scaled_array = scaled_df.to_numpy()

        # make a matrix to ensure that chronology is maintained
        connectivity_matrix = generate_connectivity_matrix(
            scale_len=len(scale))
        ahc = AgglomerativeClustering(n_clusters=periods, metric='euclidean', connectivity=connectivity_matrix,
                                      linkage='ward', compute_full_tree=True)
        clustered_array = ahc.fit_predict(scaled_array)
        cluster_labels = ahc.labels_  # get list of representative days

        nearest_centroid_array = NearestCentroid().fit(
            scaled_array, clustered_array).centroids_  # get the centroids of the clusters
        nearest_centroid_df = pandas.DataFrame(
            data=nearest_centroid_array, columns=list(scaled_df))
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
            for cluster in cluster_array:
                # finding euclidean distance from each data point to centroid
                cluster_point = list(cluster)
                euclidean_distance = find_euclidean_distance(
                    cluster_point, centroid)
                euclidean_distance_list.append(euclidean_distance)

        # find the actual day closest to centroid
        scaled_df['ED'] = euclidean_distance_list
        closest_to_centroid_df['period'] = (
            scaled_df['cluster_no'].value_counts().index.values)
        cluster_wts = list(scaled_df['cluster_no'].value_counts())
        closest_to_centroid_df['cluster_wt'] = cluster_wts

        list_ = []
        for i in closest_to_centroid_df['period']:
            list_.append(
                scaled_df.index.values[scaled_df['ED'] == scaled_df['ED'][scaled_df['cluster_no'] == i].min()][0])
        # find the actual day closest to centroid
        closest_to_centroid_df['rep_period'] = list_
        closest_to_centroid_df = closest_to_centroid_df.sort_values(
            by=['rep_period']).reset_index(drop=True)
        closest_to_centroid_df['period'] = list(
            range(len(closest_to_centroid_df['period'])))

        current_iter = [tuple(i)
                        for i in reduced_scenario_scaleiter[parent_iter]]

        output_dict = {scale: {'rep_period': (parent_iter,
                                              closest_to_centroid_df['rep_period'][closest_to_centroid_df['period'] == scale[scale_level]].values[0], *scale[scale_level+1:]),
                               'cluster_wt': closest_to_centroid_df['cluster_wt'][closest_to_centroid_df['period'] == scale[scale_level]].values[0]}
                       for scale in current_iter}

        # V. important: clusters each index in the parent scale individually and combines dict
        rep_dict_iter = {**rep_dict_iter, **output_dict}
    # rep_dict = {rep_dict_iter[i].values() for i}

    # puts all relevant data in a dictionary

    # collects the error data
    wcss_sum = sum(i for i in scaled_df['ED'])/periods

    numpy.info_dict = {
        'wcss_sum': wcss_sum,
    }

    return rep_dict_iter, reduced_temporal_scale, numpy.info_dict

# TODO - call methods as a function
# TODO  - Handle multiple outputs


def agg_hierarchial_elbow(scenario: Scenario, scale_level: int, include: list, range_list: list = None, fit: Fit = None) -> Tuple[list, int]:
    """calculate the error of a particular clustering method over a range of different cluster periods

    Args:
        scales (TemporalScale): scales of the problem
        scale_level (int): scale over which to cluster
        include (list): list of factors to include
        range_list (list, optional): range of clustering days over which to compute error. Defaults to None.
        fit (Fit, optional): a polyfit curve of 2nd or 3rd degree. Defaults to None.

    Returns:
        Tuple(list, int): error for each cluster period returned as a list
    """

    if range_list is None:
        iter_ = scenario.scales.scale[scale_level]
    else:
        iter_ = range_list
    wcss_list = []
    for i in iter_:
        rep_dict_iter, reduced_temporal_scale, numpy.info_dict = agg_hierarchial(scales=scenario.scales, scale_level=scale_level, periods=i,
                                                                                 price_factor=scenario.price_factor, capacity_factor=scenario.capacity_factor,
                                                                                 demand_factor=scenario.demand_factor, include=include)
        wcss_list.append(numpy.info_dict['wcss_sum'])

    if fit == Fit.POLY2:
        theta = numpy.polyfit(x=range_list,  y=wcss_list, deg=2)
        y_line = [theta[2] + theta[1] *
                  pow(x, 1) + theta[0] * pow(x, 2) for x in range_list]
        # y_slope = [theta[1] + 2*theta[0] * pow(x, 1) for x in range_list]

    if fit == Fit.POLY3:
        theta = numpy.polyfit(x=range_list,  y=wcss_list, deg=3)
        y_line = [theta[3] + theta[2] * pow(x, 1) + theta[1] * pow(
            x, 2) + theta[0] * pow(x, 3) for x in range_list]
        # y_slope = [theta[2] + 2*theta[1] *
                #    pow(x, 1) + 3*theta[0] * pow(x, 2) for x in range_list]

    fig, ax = plt.subplots(figsize=(8, 6))
    x = range_list

    ax.plot(x, y_line, label='MARS fit', color='steelblue', alpha=0.6)

    ax.scatter(x, wcss_list, color='indianred')

    included = ''.join([str(i).split('IncludeAHC.')[1] + str(' ')
                       for i in include])

    plt.title(f'Clustering using AHC for Houston for {included}')
    plt.xlabel('Cluster Size')
    plt.ylabel('WCSS')
    plt.grid(alpha=0.3)

    plt.legend()

    return wcss_list
