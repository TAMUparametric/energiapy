"""Utilities for plots, manages axes and such."""

from matplotlib import ticker

_DAYS_PER_YEAR = 365
_HOURS_PER_YEAR = 24 * _DAYS_PER_YEAR


def axis_formatter(axes, xcord: list, axis_labels: str = "M"):
    pos_list_8760 = [
        0,
        744,
        1344,
        2160,
        2800,
        3624,
        4344,
        5088,
        5832,
        6552,
        7296,
        8016,
    ]  # hours of the year corresponding to month
    pos_list_365 = [
        0,
        31,
        59,
        90,
        120,
        151,
        181,
        212,
        243,
        273,
        304,
        334,
    ]  # hours of the year corresponding to month
    name_list = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    if axis_labels == "M":
        positions = {
            _HOURS_PER_YEAR: pos_list_8760,
            _DAYS_PER_YEAR: pos_list_365,
            len(name_list): range(len(name_list)),
        }.get(len(xcord))
        if positions is not None:
            axes.xaxis.set_major_locator(ticker.FixedLocator(positions))
            axes.xaxis.set_major_formatter(ticker.FixedFormatter(name_list))
    return axes
