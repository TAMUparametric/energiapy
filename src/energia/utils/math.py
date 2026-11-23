"""Utilities to perform mathematical operations."""

from itertools import batched
from math import erf, exp, pi, sqrt


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


def normalize(data: list, how: str = "max") -> list:
    """
    Normalize a series of values or (lower, upper) intervals.

    The ``max`` method divides by the series maximum. If the maximum is
    zero, it uses the largest magnitude, leaving an all-zero series at zero.
    The ``min_max`` method maps the extrema to 0 and 1, or a constant to 0.
    Interval endpoints share one scale. Nested lists are independent series.

    :param data: Time-series values or (lower, upper) pairs.
    :param how: Normalization method, either ``max`` or ``min_max``.
    :return: Normalized values in the same grouping as the input.
    :raises ValueError: If the method is unknown or interval bounds are reversed.

    .. admonition:: Example

        .. code-block:: python

            from energia.utils.math import normalize

            prices = [(2, 4), (6, 8)]
            assert normalize(prices, how="max") == [(0.25, 0.5), (0.75, 1.0)]
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
