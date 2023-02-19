#%%
"""plotting module
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
from ..utils.plot_utils import axis_formatter
from ..components.process import Process
from ..components.resource import Resource
from ..components.result import Result
from ..components.location import Location
from typing import Union




def capacity_factor(process: Process, location: Location, \
    fig_size:tuple = (12,6), font_size:int = 16, color:str ='blue', usetex:bool = False):
    """generates a plot for varying capacity factor of process

    Args:
        process (Process): process data object
        location (Location): location
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
        usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
    """

    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=False)
    fig, ax = plt.subplots(figsize= fig_size)
    y_ = list(location.capacity_factor[process.name].values())
    x_ = [i for i in range(len(y_))]
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes= ax, xcord = x_, axis_labels= 'M')
    plt.title(f'Conversion factor for {process.label} in {location.label}')
    plt.ylabel('Normalized capacity factor')
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return

def cost_factor(resource: Resource, location: Location, \
    fig_size:tuple = (12,6), font_size:int = 16, color:str ='blue', usetex:bool = False):
    """generates a plot for varying cost factor of resource

    Args:
        resource (Resource): resource data object
        location (Location): location data object
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
        usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
    """
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=False)
    fig, ax = plt.subplots(figsize= fig_size)
    y_ = list(location.cost_factor[resource.name].values())
    x_ = [i for i in range(len(y_))]
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes= ax, xcord = x_, axis_labels= 'M')
    plt.title(f'Cost factor for {resource.label} in {location.label}')
    plt.ylabel('Normalized cost factor')
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return

def demand_factor(resource: Resource, location: Location, \
    fig_size:tuple = (12,6), font_size:int = 16, color:str ='blue', usetex:bool = False):
    """generates a plot for varying demand factor of resource

    Args:
        resource (Resource): resource data object
        location (Location): location data object
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
        usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
    """
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=False)
    fig, ax = plt.subplots(figsize= fig_size)
    y_ = list(location.demand_factor[resource.name].values())
    x_ = [i for i in range(len(y_))]
    ax.plot(x_, y_, linewidth=0.5, color=color)
    ax = axis_formatter(axes= ax, xcord = x_, axis_labels= 'M')
    plt.title(f'demand factor for {resource.label} in {location.label}')
    plt.ylabel('Normalized demand factor')
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return


def schedule(results: Result, y_axis:str, component:str, location:str,\
    fig_size:tuple = (12,6), font_size:int = 16, color:str ='blue', usetex:bool = False):
    """generates a plot for scheduling result

    Args:
        result (dict): dictionary that can be taken from result object 
        component (str): resource or process name
        location (str): location name
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
        usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
        
    """
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=usetex)
    fig, ax = plt.subplots(figsize= fig_size)
    results.__dict__['components'].keys()
    y_ = [results.output[y_axis][i] for i in results.output[y_axis].keys() if location in i if component in i]
    
    for i in results.__dict__['components'].keys():
        if component in results.__dict__['components'][i]:
            component_type = i

    title = f"Schedule for {results.components[component_type][component]['label']} in {results.components['locations'][location]['label']}"
    plt.title(title)
    plt.ylabel(results.components[component_type][component]['basis'])
    x_ = [i for i in range(len(y_))]
    ax.plot(x_, y_, linewidth=0.5, color=color)
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    # plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return



def contribution(results: Result, y_axis:str, location:str,\
    fig_size:tuple = (12,6), font_size:int = 16, color:str ='blue', usetex:bool = False):
    """generates a plot for scheduling result

    Args:
    #     result (dict): dictionary that can be taken from result object 
    #     component (str): resource or process name
    #     location (str): location name
    #     font_size (int, optional): font size. Defaults to 16.
    #     fig_size (tuple, optional): figure size. Defaults to (12,6).
    #     color (str, optional): color of plot. Defaults to 'blue'.
    #     usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
        
    # """
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=usetex)
    fig, ax = plt.subplots(figsize= fig_size)
    y_ = [results.output[y_axis][i] for i in results.output[y_axis].keys() if location in i]
    print(y_)

    # title = f"Schedule for {results.components[component_type][component]['label']} in {results.components['locations'][location]['label']}"
    plt.title(f"${y_axis.split('_')[0]}_{{{y_axis.split('_')[1]}}}$")
    # plt.ylabel(results.components[component_type])
    # results.components['processes'][i[1]]['label'] 
    # x_ = [f"${i[1].split('_')[0]}_{{{i[1].split('_')[1]}}}$" for i in results.output[y_axis].keys() if location in i]
    x_ = [i[1] for i in results.output[y_axis].keys() if location in i]
    ax.bar(x_, y_, linewidth=0.5, color=color)
    plt.xticks(rotation = 90)
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return

def capacity_utilization(results: Result, location:str, process:str = None,\
    fig_size:tuple = (12,6), font_size:int = 16, color:str ='blue', usetex:bool = False):
    """generates a plot for scheduling result

    Args:
    #     result (dict): dictionary that can be taken from result object 
    #     component (str): resource or process name
    #     location (str): location name
    #     font_size (int, optional): font size. Defaults to 16.
    #     fig_size (tuple, optional): figure size. Defaults to (12,6).
    #     color (str, optional): color of plot. Defaults to 'blue'.
    #     usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
        
    # """
    if process is not None:
        rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})
        rc('text', usetex=usetex)
        Cap_P = max([results.output['Cap_P'][i] for i in results.output['Cap_P'].keys() if process in i if location in i])
        if Cap_P > 0:
            fig, ax = plt.subplots(figsize= fig_size)
            y_ = [100*results.output['P'][i]/Cap_P \
                for i in results.output['P'].keys() if location in i if process in i]

            title = f"Capacity utilization in {results.components['locations'][location]['label']}"
            plt.ylabel(f"\%")
            # results.components['processes'][i[1]]['label'] 
            # x_ = [f"${i[1].split('_')[0]}_{{{i[1].split('_')[1]}}}$" for i in results.output[y_axis].keys() if location in i]
            
            ax.plot(y_, linewidth=0.5, color=color)
            plt.xticks(rotation = 90)
            plt.grid(alpha=0.3)
            plt.rcdefaults()
        else:
            print('Process not established')
    else:
        rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})
        rc('text', usetex=usetex)
        fig, ax = plt.subplots(figsize= fig_size)
        y_ = [100*results.output['Cap_P'][i]/results.components['processes'][i[1]]['prod_max'] for i in results.output['Cap_P'].keys() if location in i]

        title = f"Capacity utilization in {results.components['locations'][location]['label']}"
        plt.ylabel(f"\%")
        # results.components['processes'][i[1]]['label'] 
        # x_ = [f"${i[1].split('_')[0]}_{{{i[1].split('_')[1]}}}$" for i in results.output[y_axis].keys() if location in i]
        x_ = [i[1] for i in results.output['Cap_P'].keys() if location in i]
        ax.bar(x_, y_, linewidth=0.5, color=color)
        plt.xticks(rotation = 90)
        plt.grid(alpha=0.3)
        plt.rcdefaults()
    return



#TODO - plots are independent of scales, check
#TODO - make bar plots / pie plots for contribution from different components 
#TODO - make layered scheduling plot for comparison 
#TODO - make scenario comparison plots, perhaps use kwargs, allow n number of comparisons 






# %%

# %%