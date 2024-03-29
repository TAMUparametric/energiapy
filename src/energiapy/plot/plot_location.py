"""plotting module for location
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.8"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

import matplotlib.pyplot as plt
from matplotlib import rc

from ..components.location import Location
from ..components.process import Process
from ..components.resource import Resource
from ..utils.plot_utils import axis_formatter


def capacity_factor(location: Location, process: Process, fig_size: tuple = (12, 6), font_size: int = 16, color: str = 'blue', usetex: bool = False):
    """generates a plot for varying capacity factor of process

    Args:
        process (Process): process energiapy object
        location (Location): location energiapy object
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
        usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
    """

    rc('font', **{'family': 'serif',
       'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=False)
    fig, ax = plt.subplots(figsize=fig_size)
    y_ = list(location.capacity_factor[process.name].values())
    x_ = list(range(len(y_)))
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes=ax, xcord=x_, axis_labels='M')
    plt.title(f'Conversion factor for {process.label} in {location.label}')
    plt.ylabel("Normalized capacity factor")
    plt.xlabel("Scheduling Horizon")
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return


def price_factor(resource: Resource, location: Location, fig_size: tuple = (12, 6), font_size: int = 16, color: str = 'blue', usetex: bool = False):
    """generates a plot for varying price factor for purchase of resource

    Args:
        resource (Resource): resource energiapy object
        location (Location): location energiapy object
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
        usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
    """
    rc('font', **{'family': 'serif',
       'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=False)
    fig, ax = plt.subplots(figsize=fig_size)
    y_ = list(location.price_factor[resource.name].values())
    x_ = list(range(len(y_)))
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes=ax, xcord=x_, axis_labels='M')
    plt.title(f'Price factor for {resource.label} in {location.label}')
    plt.ylabel("Normalized cost factor")
    plt.xlabel("Scheduling Horizon")
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return




def demand_factor(resource: Resource, location: Location,
                  fig_size: tuple = (12, 6), font_size: int = 16, color: str = 'blue', usetex: bool = False):
    """generates a plot for varying demand factor of resource

    Args:
        resource (Resource): resource energiapy object
        location (Location): location energiapy object
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
        usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
    """
    rc('font', **{'family': 'serif',
       'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=False)
    fig, ax = plt.subplots(figsize=fig_size)
    y_ = list(location.demand_factor[resource.name].values())
    x_ = list(range(len(y_)))
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes=ax, xcord=x_, axis_labels='M')
    plt.title(f'Demand factor for {resource.label} in {location.label}')
    plt.ylabel("Normalized demand factor")
    plt.xlabel("Scheduling Horizon")
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return


def capex_factor(process: Process, location: Location,
                 fig_size: tuple = (12, 6), font_size: int = 16, color: str = 'blue'):
    """generates a plot for varying technology capital expenditure

    Args:
        process (Process): process energiapy object
        location (Location): location energiapy object
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
        usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
    """
    rc('font', **{'family': 'serif',
       'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=False)
    fig, ax = plt.subplots(figsize=fig_size)
    y_ = list(location.capex_factor[process.name].values())
    x_ = list(range(len(y_)))
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes=ax, xcord=x_, axis_labels='M')
    plt.title(f'Capex factor for {process.label} in {location.label}')
    plt.ylabel("Normalized capex factor")
    plt.xlabel("Scheduling Horizon")
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return


def vopex_factor(process: Process, location: Location,
                 fig_size: tuple = (12, 6), font_size: int = 16, color: str = 'blue'):
    """generates a plot for varying technology variable operational expenditure

    Args:
        process (Process): process energiapy object
        location (Location): location energiapy object
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
        usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
    """
    rc('font', **{'family': 'serif',
       'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=False)
    fig, ax = plt.subplots(figsize=fig_size)
    y_ = list(location.vopex_factor[process.name].values())
    x_ = list(range(len(y_)))
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes=ax, xcord=x_, axis_labels='M')
    plt.title(f'Vopex factor for {process.label} in {location.label}')
    plt.ylabel("Normalized vopex factor")
    plt.xlabel("Scheduling Horizon")
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return


def fopex_factor(process: Process, location: Location,
                 fig_size: tuple = (12, 6), font_size: int = 16, color: str = 'blue'):
    """generates a plot for varying technology fixed operational expenditure

    Args:
        process (Process): process energiapy object
        location (Location): location energiapy object
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
        usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
    """
    rc('font', **{'family': 'serif',
       'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=False)
    fig, ax = plt.subplots(figsize=fig_size)
    y_ = list(location.fopex_factor[process.name].values())
    x_ = list(range(len(y_)))
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes=ax, xcord=x_, axis_labels='M')
    plt.title(f'Fopex factor for {process.label} in {location.label}')
    plt.ylabel("Normalized fopex factor")
    plt.xlabel("Scheduling Horizon")
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return


def availability_factor(resource: Resource, location: Location,
                        fig_size: tuple = (12, 6), font_size: int = 16, color: str = 'blue', usetex: bool = False):
    """generates a plot for varying availability factor of resource

    Args:

        resource (Resource): resource energiapy object
        location (Location): location energiapy object
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
        usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
    """
    rc('font', **{'family': 'serif',
       'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=False)
    fig, ax = plt.subplots(figsize=fig_size)
    y_ = list(
        location.availability_factor[resource.name].values())
    x_ = list(range(len(y_)))
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes=ax, xcord=x_, axis_labels='M')
    plt.title(f'Demand factor for {resource.label} in {location.label}')
    plt.ylabel("Normalized availability factor")
    plt.xlabel("Scheduling Horizon")
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return


def revenue_factor(resource: Resource, location: Location,
                   fig_size: tuple = (12, 6), font_size: int = 16, color: str = 'blue', usetex: bool = False):
    """generates a plot for varying revenue factor of resource

    Args:

        resource (Resource): resource energiapy object
        location (Location): location energiapy object
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
        usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
    """
    rc('font', **{'family': 'serif',
       'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=False)
    fig, ax = plt.subplots(figsize=fig_size)
    y_ = list(
        location.revenue_factor[resource.name].values())
    x_ = list(range(len(y_)))
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes=ax, xcord=x_, axis_labels='M')
    plt.title(f'Demand factor for {resource.label} in {location.label}')
    plt.ylabel("Normalized revenue factor")
    plt.xlabel("Scheduling Horizon")
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return
