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
from ..components.process import process
from ..components.resource import resource
from ..components.location import location

#%%

def capacity_factor(process: process, location: location = None, \
    fig_size:tuple = (12,6), font_size:int = 16, color:str ='black'):

    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=True)
    fig, ax = plt.subplots(figsize= fig_size)
    y_ = list(location.capacity_factor[process.name].values())
    x_ = [i for i in range(len(y_))]
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes= ax, xcord = x_, axis_labels= 'M')
    plt.title('Conversion factor for ' + process.label)
    plt.ylabel('Normalized conversion factors')
    plt.grid(alpha=0.3)
    fig.show()
    plt.rcdefaults()
    return

def cost_factor(resource: resource, location: location = None, \
    fig_size:tuple = (12,6), font_size:int = 16, color:str ='black'):
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=True)
    fig, ax = plt.subplots(figsize= fig_size)
    y_ = list(location.cost_factor[resource.name].values())
    x_ = [i for i in range(len(y_))]
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes= ax, xcord = x_, axis_labels= 'M')
    plt.title('Conversion factor for ' + resource.label)
    plt.ylabel('Normalized conversion factors')
    plt.grid(alpha=0.3)
    fig.show()
    plt.rcdefaults()
    return




    
#%%


# %%

# %%
