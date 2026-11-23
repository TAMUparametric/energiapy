"""Utilities to perform mathematical operations."""

from math import erf, exp, pi, sqrt

from vaelchi import normalize

__all__ = ["norm_constant", "normalize"]


def norm_constant(p, mu, sigma) -> float:
    """
    Calculates the normal constant.

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
