"""Utilities to perform mathematical operations"""

from itertools import batched
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
    """Normalize a series of values or (lower, upper) intervals.

    The ``max`` method divides by the series maximum. If the maximum is
    zero, it uses the largest magnitude, leaving an all-zero series at zero.
    The ``min_max`` method maps the extrema to 0 and 1, or a constant to 0.
    Interval endpoints share one scale. Nested lists are independent series.

    :param data: Time-series values or (lower, upper) pairs.
    :param how: Normalization method, either ``max`` or ``min_max``.
    :return: Normalized values in the same grouping as the input.
    """
    if how not in ("max", "min_max"):
        message = f"Unknown normalization method {how!r}"
        raise ValueError(message)
    if len(data) == 0:
        return []
    first = next(iter(data))
    if isinstance(first, list):
        return [normalize(series, how) for series in data]
    if isinstance(first, tuple):
        if any(lower > upper for lower, upper in data):
            message = "The lower bound must not exceed the upper bound"
            raise ValueError(message)
        endpoints = [value for interval in data for value in interval]
        scaled = normalize(endpoints, how)
        return [(min(pair), max(pair)) for pair in batched(scaled, 2)]

    offset = min(data) if how == "min_max" else 0
    divisor = max(data) - offset
    if divisor == 0:
        divisor = abs(min(data) - offset) or 1
    return [(value - offset) / divisor for value in data]
