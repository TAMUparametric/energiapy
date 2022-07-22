#%%
"""Graphing module
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from matplotlib import rc
import matplotlib.pyplot as plt
from ..utils.graph_utils import axis_formatter
from ..components.process import Process
from ..components.resource import Resource
from ..components.result import Result
from ..components.location import Location
from typing import Union




def capacity_factor(process: Process, location: Location, \
    fig_size:tuple = (12,6), font_size:int = 16, color:str ='blue'):
    """generates a graph for varying capacity factor of process

    Args:
        process (Process): process data object
        location (Location): location
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
    """

    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=True)
    fig, ax = plt.subplots(figsize= fig_size)
    y_ = list(location.capacity_factor[process.name].values())
    x_ = [i for i in range(len(y_))]
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes= ax, xcord = x_, axis_labels= 'M')
    plt.title(f'Conversion factor for {process.label} in {location.label}')
    plt.ylabel('Normalized conversion factors')
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return

def cost_factor(resource: Resource, location: Location, \
    fig_size:tuple = (12,6), font_size:int = 16, color:str ='blue'):
    """generates a graph for varying cost factor of resource

    Args:
        resource (Resource): resource data object
        location (Location): location data object
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
    """
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=True)
    fig, ax = plt.subplots(figsize= fig_size)
    y_ = list(location.cost_factor[resource.name].values())
    x_ = [i for i in range(len(y_))]
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes= ax, xcord = x_, axis_labels= 'M')
    plt.title(f'Cost factor for {resource.label} in {location.label}')
    plt.ylabel('Normalized Cost factor')
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return


def schedule(result: dict, component: Union[Resource, Process], location: Location,\
    fig_size:tuple = (12,6), font_size:int = 16, color:str ='blue'):
    """generates a graph for scheduling result

    Args:
        result (dict): dictionary that can be taken from result object 
        component (Union[Resource, Process]): resource or process data object
        location (Location): location data object
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
    """
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=False)
    fig, ax = plt.subplots(figsize= fig_size)
    y_ = [result[i] for i in result.keys() if location.name in i if component.name in i]
    x_ = [i for i in range(len(y_))]
    ax.plot(x_, y_, linewidth=0.5, color=color)
    plt.title(f'Schedule for {component.label} in {location.label}')
    plt.ylabel(component.basis)
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return


# %%

# %%
