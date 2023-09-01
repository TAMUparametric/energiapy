"""Fitting distributions 
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

import numpy
import pandas
from distfit import distfit
from ..utils.math_utils import min_max


def fit(data:numpy.array) -> pandas.DataFrame:
    """fit data to a probability distribution

    Args:
        data (numpy.array): time-series data

    Returns:
        pandas.DataFrame: summary of the fit
    """
    data = min_max(data)

    dist = distfit()
    fit_ = dist.fit_transform(data)

    fit_summary = fit_['summary']

    fit_summary = fit_summary.set_index('name')

    print(f"The best fitting distribution is {fit_['model']}")

    return fit_summary