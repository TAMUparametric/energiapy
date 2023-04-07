"""Reduce the scenario with appropriate method
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

from ..aggregation.ahc import agg_hierarchial
from ..aggregation.dtw import dynamic_warping
from ..components.location import Location
from ..components.process import Process
from ..components.resource import Resource
from ..components.scenario import Scenario


class Clustermethod(Enum):
    """
    Which cluster method to use
    """
    AHC = auto()
    """
    Agglomerative Hierarchial Clustering
    """
    DTW = auto()
    """
    Dynamic Time Warping
    """


def reduce_scenario(scenario: Scenario, method: Clustermethod, include: list, scale_level: int = None, source_scenario: Scenario = None, target_scenario: Scenario = None, aspect: Union[Resource, Process] = None, location: Location = None, periods: int = None, reference_dict: dict = None) -> Scenario:
    """reduce scenario using a particular method

    Args:
        scenario (Scenario): full-scale scenario
        method (Clustermethod): cluster method to use
        include (list): list of factors to include
        scale_level (int): the scale level
        source_scenario (Scenario): scenario to warp from
        target_scenario (Scenario): scenario to warp onto
        aspect (Union[Resource, Process]): aspect for dtw to reconcile over
        location (Location): location in scenario to cluster
        periods (int): number of clustering intervals
        reference_dict (dict, optional): dictionary to pull values from. Defaults to None.


    Returns:
        Scenario: reduced scenario
    """

    if method is Clustermethod.AHC:
        rep_dict, reduced_temporal_scale, numpy.info_dict = agg_hierarchial(
            scenario.scales, scale_level=scale_level, periods=periods, price_factor=scenario.price_factor, capacity_factor=scenario.capacity_factor, demand_factor=scenario.demand_factor, include=include)

    if method is Clustermethod.DTW:
        rep_dict, reduced_temporal_scale, numpy.info_dict = dynamic_warping(
            source_scenario=source_scenario, target_scenario=target_scenario, include=include, aspect=aspect, scale_level=scale_level, reference_dict=reference_dict)

    reduced_scenario_scaleiter = list(product(
        *[reduced_temporal_scale.scale[i] for i in reduced_temporal_scale.scale]))

    # cluster_wt = {scale: rep_dict[scale]['cluster_wt'] for scale in reduced_scenario_scaleiter}

    reduced_scenario = Scenario(name=f"{scenario.name}_reduced", scales=reduced_temporal_scale, network=scenario.network, expenditure_scale_level=scenario.expenditure_scale_level, purchase_scale_level = scenario.purchase_scale_level,
                                scheduling_scale_level=scenario.scheduling_scale_level, network_scale_level=scenario.network_scale_level, demand_scale_level=scenario.demand_scale_level, demand=scenario.demand, label=f"{scenario.label}(reduced)")

    for location in scenario.location_set:
        if scenario.price_factor[location.name] is not None:
            len_ = len(
                list(list(scenario.price_factor[location.name].values())[0].keys())[0])
            reduced_scenario.price_factor[location.name] = {i: {j[:len_]: scenario.price_factor[location.name][i][rep_dict[j]['rep_period'][:len_]] for j in list(
                rep_dict.keys())} for i in list(scenario.price_factor[location.name])}

        if scenario.capacity_factor[location.name] is not None:
            len_ = len(
                list(list(scenario.capacity_factor[location.name].values())[0].keys())[0])
            reduced_scenario.capacity_factor[location.name] = {i: {
                j[:len_]: scenario.capacity_factor[location.name][i][rep_dict[j]['rep_period'][:len_]] for j in list(rep_dict.keys())} for i in list(scenario.capacity_factor[location.name])}

        if scenario.demand_factor[location.name] is not None:
            len_ = len(
                list(list(scenario.demand_factor[location.name].values())[0].keys())[0])
            reduced_scenario.demand_factor[location.name] = {i: {
                j[:len_]: scenario.demand_factor[location.name][i][rep_dict[j]['rep_period'][:len_]] for j in list(rep_dict.keys())} for i in list(scenario.demand_factor[location.name])}

    if reference_dict is not None:
        reduced_scenario.cluster_wt = {
            scale: reference_dict[scale]['cluster_wt'] for scale in reduced_scenario_scaleiter}

    else:

        reduced_scenario.cluster_wt = {
            scale: rep_dict[scale]['cluster_wt'] for scale in reduced_scenario_scaleiter}

    return reduced_scenario, rep_dict, numpy.info_dict
