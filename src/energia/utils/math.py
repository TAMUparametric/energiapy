"""Utilities to perform mathematical operations"""

from math import erf, exp, pi, sqrt

import numpy


def norm_constant(p, mu, sigma) -> float:
    """
    Calculates the normal constant

    :param p: level of compliance
    :type p: float
    :param mu: mean
    :type mu: float
    :param sigma: standard deviation
    :type sigma: float
    :return: normal constant
    :rtype: float
    """
    x = mu + erf(1 / sqrt(2) * p) * sigma * sqrt(2)
    return 1 / (sigma * sqrt(2 * pi)) * exp(-((x - mu) ** 2) / (2 * sigma**2))


def find_euclidean_distance(a: list, b: list) -> float:
    """
    finds euclidean distances between two cluster nodes

    :param a: coordinates of cluster node a
    :type a: list
    :param b: coordinates of cluster node b
    :type b: list

    :returns: euclidean distance
    :rtype: float
    """
    distance_ = [(a - b) ** 2 for a, b in zip(a, b)]
    distance_ = sum(distance_)
    return distance_


def generate_connectivity_matrix(scale_len) -> numpy.array:
    """
    Generates a connectivity matrix to maintain chronology [..1,0,1..]

    :param scale_len: length of the scale
    :type scale_len: int

    :returns: connectivity matrix
    :rtype: numpy.array
    """
    connect_ = numpy.zeros((scale_len, scale_len), dtype=int)
    for i_ in range(len(connect_)):

        if i_ == 0:
            # connect_[i,364] = 1 #uncomment these to generate a cyclic matrix
            connect_[i_, 1] = 1
        elif i_ == scale_len - 1:
            connect_[i_, scale_len - 2] = 1
            # connect_[i,0] = 1
        else:
            connect_[i_, i_ - 1] = 1
            connect_[i_, i_ + 1] = 1
    return connect_


def normalize(data: list, how: str = "max") -> list:
    """
    min max normalization of data

    :param data: time-series data
    :type data: numpy.array | DataFrame
    :param how: min-max or max, defaults to "max"
    :type how: str, optional

    :return: normalized data
    :rtype: numpy.array | DataFrame
    """
    if all(isinstance(i, tuple) for i in data):
        # lower bound
        lb = [i[0] for i in data]
        # upper bound
        ub = [i[1] for i in data]
        # normalize lower and upper bounds individually
        lb_norm = normalize(lb, how=how)
        ub_norm = normalize(ub, how=how)
        return list(zip(lb_norm, ub_norm))

    if how == "min_max":
        min_ = min(data)
        max_ = max(data)
        data = [(i - min_) / (max_ - min_) for i in data]

    if how == "max":
        max_ = max(data)
        data = [i / max(data) for i in data]
    return data
