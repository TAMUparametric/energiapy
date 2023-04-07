"""Clustering with Dynamic Time Warping (DTW)
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
from itertools import product
from typing import Union

import numpy

from ..components.process import Process
from ..components.resource import Resource
from ..components.scenario import Scenario


class IncludeDTW(Enum):
    """
    What aspects to include in dynamic time warping
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


def dynamic_warping_matrix(series1: list, series2: list):
    """clusters time series data with disparate temporal resolution using dynamic time warping (dtw)

    Args:
        series1 (list): time series 1
        series2 (list): time series 2

    Returns:
        matrix: cost matrix for dtw
    """
    matrix = numpy.zeros((len(series1) + 1, len(series2) + 1))
    for i, j in product(range(1, len(series1) + 1), range(1, len(series2) + 1)):
        matrix[i, j] = numpy.inf
    matrix[0, 0] = 0
    for i, j in product(range(1, len(series1) + 1), range(1, len(series2) + 1)):
        cost = abs(series1[i - 1] - series2[j - 1])
        prev = numpy.min([matrix[i - 1, j], matrix[i, j - 1], matrix[i - 1, j - 1]])
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
            [matrix[i - 1, j], matrix[i, j - 1], matrix[i - 1, j - 1]])
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


def dynamic_warping(source_scenario: Scenario, target_scenario: Scenario, scale_level: int, include: list,
                    aspect: Union[Resource, Process], reference_dict: dict = None):
    """Dynamic time warping for scenario reconciliation

    Args:
        source_scenario (Scenario): scenario to warp from
        target_scenario (Scenario): scenario to warp onto
        scale_level (int): the scale level
        include (list): which factors to include
        aspect (Union[Resource, Process]): _description_
        reference_dict (dict, optional): dictionary to pull values from. Defaults to None.

    Returns:
        _type_: _description_
    """

    source_location = list(source_scenario.location_set)[0]
    target_location = list(target_scenario.location_set)[0]

    if IncludeDTW.COST in include:
        source_series = list(
            source_scenario.price_factor[source_location.name][aspect.name].values())
        target_series = list(
            target_scenario.price_factor[target_location.name][aspect.name].values())
        reference_keys = target_scenario.price_factor[target_location.name][aspect.name].keys(
        )

    elif IncludeDTW.CAPACITY in include:
        source_series = list(
            source_scenario.capacity_factor[source_location.name][aspect.name].values())
        target_series = list(
            target_scenario.capacity_factor[target_location.name][aspect.name].values())
        reference_keys = target_scenario.capacity_factor[target_location.name][aspect.name].keys(
        )

    elif IncludeDTW.DEMAND in include:
        source_series = list(
            source_scenario.demand_factor[source_location.name][aspect.name].values())
        target_series = list(
            target_scenario.demand_factor[target_location.name][aspect.name].values())

        reference_keys = target_scenario.demand_factor[target_location.name][aspect.name].keys(
        )

    matrix = dynamic_warping_matrix(
        series1=source_series, series2=target_series)

    path = dynamic_warping_path(matrix=matrix)

    path = [i for i in path if i[0] != 0]  # remove zeroth value

    # collects the x and y coordinates of path as separate lists
    x_ = [path[i][0] - 1 for i in range(len(path))]
    y_ = [path[i][1] - 1 for i in range(len(path))]

    # reverse the coordinates
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

    reduced_scenario_scaleiter = list(product(
        *[reduced_temporal_scale.scale[i] for i in reduced_temporal_scale.scale]))

    counts = {j: y_.count(i) for i, j in zip(i_list, j_list)}

    rep_dict = {j: {'rep_period': reference_dict[j]['rep_period'],
                    'cluster_wt': counts[j[:scale_level]]} for j in reduced_scenario_scaleiter}

    info_dict = {
        'matrix': matrix,
        'path': path,
        'input_data': {'source': source_series, 'target': target_series},
        'output_data': {'source': source_values, 'target': target_values},
    }

    return rep_dict, reduced_temporal_scale, info_dict
