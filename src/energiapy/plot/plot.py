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
    plt.ylabel("Normalized capacity factor")
    plt.xlabel(f"Scheduling Horizon")
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
    plt.ylabel(f"Normalized cost factor")
    plt.xlabel(f"Scheduling Horizon")
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
    plt.title(f'Demand factor for {resource.label} in {location.label}')
    plt.ylabel(f"Normalized demand factor")
    plt.xlabel(f"Scheduling Horizon")
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return


def schedule(results: Result, y_axis:str, component:str, location:str,\
    fig_size:tuple = (12,6), font_size:int = 16, color:str ='blue', usetex:bool = False):
    """generates a plot for scheduling result

    Args:
        result (dict): dictionary that can be taken from result object 
        y_axis (str): the y-axis, can be production (P), inventory (I), sales (S), consumption (C)
        component (str): resource or process name
        location (str): location name
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
        usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
    
    Examples:
        For production the component has to be a process. For the rest use the appropriate resource
        
        Note that results plotting requires the string names to be provided as opposed to energiapy objects
               
        >>> plot.schedule(results= results, component='Power', y_axis= 'S', location= 'Goa')
        
        >>> plot.schedule(results= results, component='PV', y_axis= 'P', location= 'Goa')
        
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
    plt.xlabel(f"Scheduling Horizon")
    x_ = [i for i in range(len(y_))]
    ax.plot(x_, y_, linewidth=0.5, color=color)
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return



def contribution(results: Result, y_axis:str, location:str,\
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
        result (dict): dictionary that can be taken from result object 
        component (str): resource or process name
        location (str): location name
        font_size (int, optional): font size. Defaults to 16.
        fig_size (tuple, optional): figure size. Defaults to (12,6).
        color (str, optional): color of plot. Defaults to 'blue'.
        usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
        
    """
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

def transport(results: Result, source:str, sink:str, resource: str, transport: str, fig_size:tuple = (12,6), font_size:int = 16, color:str ='blue', usetex:bool = False):
    """Plots the transportation schedule from source to sink of choice for resource through a transportation mode

    Args:
        results (Result): results
        source (str): source location
        sink (str): sink location
        resource (str): Resource that is being transported 
        transport (str): Transport being used
        fig_size (tuple, optional): Defaults to (12,6).
        font_size (int, optional): Defaults to 16.
        color (str, optional): Defaults to 'blue'.
        usetex (bool, optional): Defaults to False.
    
    Examples:

        Plotting transport is fairly straight forward. This plots the export from source to sink. 
    
        >>> plot.transport(results= results, source= 'Goa', sink= 'Texas', resource= 'PhDStudents', transport= 'GradSchool')
    
    """
    
    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=usetex)
    fig, ax = plt.subplots(figsize= fig_size)
    y_ = [results.output['Trans_exp'][i] for i in results.output['Trans_exp'].keys() if list(i)[:4] == [source, sink, resource, transport]]
    plt.plot(y_)
    plt.ylabel(f"Amount in unit basis")
    plt.xlabel(f"Scheduling scale")
    plt.title(f"Schedule for {resource} transported on {transport} from {source} to {sink}")
    plt.xticks(rotation = 90)
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return 

#TODO - make bar plots / pie plots for contribution from different components 
#TODO - make layered scheduling plot for comparison 
#TODO - make scenario comparison plots, perhaps use kwargs, allow n number of comparisons 




