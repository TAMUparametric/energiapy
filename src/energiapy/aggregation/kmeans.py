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

import numpy
import pandas
from sklearn.cluster import KMeans

from ..components.temporal_scale import TemporalScale


class IncludeKmeans(Enum):
    """
    What to include in K-means clustering
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



def kmeans(scales: TemporalScale, scale_level: int, periods: int, include: list, price_factor: dict = None,
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

    if IncludeKmeans.COST in include:
        # price_factor_df = pandas.DataFrame(price_factor)
        price_factor_df = pandas.concat(
            [pandas.DataFrame(price_factor[i]) for i in price_factor.keys()], axis=1)
    else:
        price_factor_df = None

    if IncludeKmeans.CAPACITY in include:
        # capacity_factor_df = pandas.DataFrame(capacity_factor)
        capacity_factor_df = pandas.concat(
            [pandas.DataFrame(capacity_factor[i]) for i in capacity_factor.keys()], axis=1)

    else:
        capacity_factor_df = None

    if IncludeKmeans.DEMAND in include:
        demand_factor_df = pandas.concat(
            [pandas.DataFrame(demand_factor[i]) for i in demand_factor.keys()], axis=1)
        # demand_factor_df = pandas.DataFrame(demand_factor)
    else:
        demand_factor_df = None

    combined_df = pandas.concat([price_factor_df, capacity_factor_df, demand_factor_df],
                                axis=1).reset_index(drop=True)

    data = combined_df.to_numpy()

    if scale_level < scales.scale_levels:
        kmeans = KMeans(n_clusters = periods*scales.discretization_list[scale_level+1], random_state = 0, n_init = 'auto').fit(data)

    # prediction = kmeans.predict(data)

    cluster_centers = kmeans.cluster_centers_

    kmeans_df = pandas.DataFrame(cluster_centers, columns= combined_df.columns)

    # scale = scales.scale[scale_level]

    # creates a new TemporalScale object on the reduced scale
    reduced_dicretization_list = list(scales.discretization_list)
    reduced_dicretization_list[scale_level] = periods
    reduced_temporal_scale = TemporalScale(reduced_dicretization_list)

    numpy.info_dict = {'a': None}


    return kmeans_df, reduced_temporal_scale, numpy.info_dict
