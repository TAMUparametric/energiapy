"""Utilities for plots, manages axes and such"""

from matplotlib import ticker


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
    if axis_labels == "M" and len(xcord) == 8760:
        axes.xaxis.set_major_locator(ticker.FixedLocator((pos_list_8760)))
        axes.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
    if axis_labels == "M" and len(xcord) == 365:
        axes.xaxis.set_major_locator(ticker.FixedLocator((pos_list_365)))
        axes.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))
    if axis_labels == "M" and len(xcord) == 12:
        axes.xaxis.set_major_locator(ticker.FixedLocator((list(range(12)))))
        axes.xaxis.set_major_formatter(ticker.FixedFormatter((name_list)))

    else:
        pass
    return axes
