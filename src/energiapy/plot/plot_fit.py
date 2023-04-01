"""fit plotting module
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

import matplotlib.pyplot as plt
from matplotlib import rc
import pandas 
import scipy
import numpy


def distribution(fit_summary: pandas.DataFrame, fit_type: 'str', fig_size: tuple = (8, 6), font_size: int = 16, color: str = 'steelblue'):
    """plot a distribution from the fit summary for a chosen fit type

    Args:
        fit_summary (pandas.DataFrame): fit summary from dist module
        fit_type (str): 'norm', 'expon', 'uniform', 'pareto', 'dweibull', 'genextreme', 'loggamma', 'lognorm', 'gamma', 'beta', 't'
        fig_size (tuple, optional): Defaults to (16, 6).
        font_size (int, optional): Defaults to 16.
        color (str, optional): Defaults to 'steelblue'.
    """

    x = numpy.linspace (0, 1, 200) 

    if fit_type == 'norm':
        y = scipy.stats.norm.pdf(x, loc= fit_summary['params'][fit_type][0], scale= fit_summary['params'][fit_type][1])
        
    if fit_type == 'expon':
        y = scipy.stats.expon.pdf(x, loc= fit_summary['params'][fit_type][0], scale= fit_summary['params'][fit_type][1])

    if fit_type == 'uniform':
        y = scipy.stats.uniform.pdf(x, loc= fit_summary['params'][fit_type][0], scale= fit_summary['params'][fit_type][1])

    if fit_type == 'pareto':
        y = scipy.stats.pareto.pdf(x, b = fit_summary['params'][fit_type][0], loc= fit_summary['params'][fit_type][1], scale= fit_summary['params'][fit_type][2])

    if fit_type == 'dweibull':
        y = scipy.stats.dweibull.pdf(x, c = fit_summary['params'][fit_type][0], loc= fit_summary['params'][fit_type][1], scale= fit_summary['params'][fit_type][2])

    if fit_type == 'genextreme':
        y = scipy.stats.genextreme.pdf(x, c = fit_summary['params'][fit_type][0], loc= fit_summary['params'][fit_type][1], scale= fit_summary['params'][fit_type][2])

    if fit_type == 'loggamma':
        y = scipy.stats.loggamma.pdf(x, c = fit_summary['params'][fit_type][0], loc= fit_summary['params'][fit_type][1], scale= fit_summary['params'][fit_type][2])

    if fit_type == 'lognorm':
        y = scipy.stats.lognorm.pdf(x, s= fit_summary['params'][fit_type][0], loc= fit_summary['params'][fit_type][1], scale= fit_summary['params'][fit_type][2])

    if fit_type == 'gamma':
        y = scipy.stats.gamma.pdf(x, a= fit_summary['params'][fit_type][0], loc= fit_summary['params'][fit_type][1], scale= fit_summary['params'][fit_type][2])

    if fit_type == 'beta':
        y = scipy.stats.beta.pdf(x, a= fit_summary['params'][fit_type][0], b = fit_summary['params'][fit_type][1], loc= fit_summary['params'][fit_type][2], scale= fit_summary['params'][fit_type][3])

    if fit_type == 't':
        y = scipy.stats.t.pdf(x, df= fit_summary['params'][fit_type][0], loc= fit_summary['params'][fit_type][1], scale= fit_summary['params'][fit_type][2])

    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})

    fig, ax = plt.subplots(figsize = fig_size)
    ax.plot(x, y, color = color)
    ax.set_title(f"{fit_type} distribution")
    plt.grid(alpha = 0.4)
    plt.rcdefaults()
    
    return
    # fig, ax = plt.subplots(1,2, figsize = fig_size)
    # ax[0].hist(data, edgecolor = 'black', color = color)
    # ax[0].set_xlim([0,1])
    # ax[0].set_title('Histogram')