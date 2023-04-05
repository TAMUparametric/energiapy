"""results plotting module
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from enum import Enum, auto

import matplotlib.pyplot as plt
from matplotlib import rc
from numpy import array, zeros

from ..components.result import Result


class CostX(Enum):
    """X axis for cost plot

    Args:
        Enum (_type_): location-wise or process-wise
    """
    LOCATION_WISE = auto()
    PROCESS_WISE = auto()


class CostY(Enum):
    """Y axis for cost plot

    Args:
        Enum (_type_): capex, fopex, vopex, or total
    """
    TOTAL = auto()
    CAPEX = auto()
    VOPEX = auto()
    FOPEX = auto()


def schedule(results: Result, y_axis: str, component: str, location: str, fig_size: tuple = (12, 6), font_size: int = 16, color: str = 'blue', usetex: bool = False):
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
    rc('font', **{'family': 'serif',
       'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=usetex)
    fig, ax = plt.subplots(figsize=fig_size)
    results.__dict__['components'].keys()
    y_ = [results.output[y_axis][i]
          for i in results.output[y_axis].keys() if location in i if component in i]

    for i in results.__dict__['components'].keys():
        if component in results.__dict__['components'][i]:
            component_type = i

    title = f"Schedule for {results.components[component_type][component]['label']} in {results.components['locations'][location]['label']}"
    plt.title(title)
    plt.ylabel(results.components[component_type][component]['basis'])
    plt.xlabel("Scheduling Horizon")
    x_ = list(range(len(y_)))
    ax.plot(x_, y_, linewidth=0.5, color=color)
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return


def contribution(results: Result, y_axis: str, location: str, fig_size: tuple = (12, 6), font_size: int = 16, color: str = 'blue', usetex: bool = False):
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
    rc('font', **{'family': 'serif',
       'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=usetex)
    fig, ax = plt.subplots(figsize=fig_size)
    y_ = [results.output[y_axis][i]
          for i in results.output[y_axis].keys() if location in i]
    print(y_)

    # title = f"Schedule for {results.components[component_type][component]['label']} in {results.components['locations'][location]['label']}"
    plt.title(f"${y_axis.split('_')[0]}_{{{y_axis.split('_')[1]}}}$")
    # plt.ylabel(results.components[component_type])
    # results.components['processes'][i[1]]['label']
    # x_ = [f"${i[1].split('_')[0]}_{{{i[1].split('_')[1]}}}$" for i in results.output[y_axis].keys() if location in i]
    x_ = [i[1] for i in results.output[y_axis].keys() if location in i]
    ax.bar(x_, y_, linewidth=0.5, color=color)
    plt.xticks(rotation=90)
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return


def capacity_utilization(results: Result, location: str, process: str = None, fig_size: tuple = (12, 6), font_size: int = 16, color: str = 'blue', usetex: bool = False):
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
        rc('font', **{'family': 'serif',
           'serif': ['Computer Modern'], 'size': font_size})
        rc('text', usetex=usetex)
        Cap_P = max([results.output['Cap_P'][i]
                    for i in results.output['Cap_P'].keys() if process in i if location in i])
        if Cap_P > 0:
            fig, ax = plt.subplots(figsize=fig_size)
            y_ = [100*results.output['P'][i]/Cap_P for i in results.output['P'].keys()
                  if location in i if process in i]

            title = f"Capacity utilization in {results.components['locations'][location]['label']}"
            plt.ylabel("\%")
            # results.components['processes'][i[1]]['label']
            # x_ = [f"${i[1].split('_')[0]}_{{{i[1].split('_')[1]}}}$" for i in results.output[y_axis].keys() if location in i]

            ax.plot(y_, linewidth=0.5, color=color)
            plt.xticks(rotation=90)
            plt.grid(alpha=0.3)
            plt.rcdefaults()
        else:
            print('Process not established')
    else:
        rc('font', **{'family': 'serif',
           'serif': ['Computer Modern'], 'size': font_size})
        rc('text', usetex=usetex)
        fig, ax = plt.subplots(figsize=fig_size)
        y_ = [100*results.output['Cap_P'][i]/results.components['processes'][i[1]]
              ['prod_max'] for i in results.output['Cap_P'].keys() if location in i]

        title = f"Capacity utilization in {results.components['locations'][location]['label']}"
        plt.ylabel("\%")
        # results.components['processes'][i[1]]['label']
        # x_ = [f"${i[1].split('_')[0]}_{{{i[1].split('_')[1]}}}$" for i in results.output[y_axis].keys() if location in i]
        x_ = [i[1] for i in results.output['Cap_P'].keys() if location in i]
        ax.bar(x_, y_, linewidth=0.5, color=color)
        plt.xticks(rotation=90)
        plt.grid(alpha=0.3)
        plt.title(title)
        plt.rcdefaults()
    return


def transport(results: Result, source: str, sink: str, resource: str, transport: str, fig_size: tuple = (12, 6), font_size: int = 16, color: str = 'blue', usetex: bool = False):
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

    rc('font', **{'family': 'serif',
       'serif': ['Computer Modern'], 'size': font_size})
    rc('text', usetex=usetex)
    fig, ax = plt.subplots(figsize=fig_size)
    y_ = [results.output['Trans_exp'][i] for i in results.output['Trans_exp'].keys(
    ) if list(i)[:4] == [source, sink, resource, transport]]
    plt.plot(y_)
    plt.ylabel("Amount in unit basis")
    plt.xlabel("Scheduling scale")
    plt.title(
        f"Schedule for {resource} transported on {transport} from {source} to {sink}")
    plt.xticks(rotation=90)
    plt.grid(alpha=0.3)
    plt.rcdefaults()
    return

# TODO - make bar plots / pie plots for contribution from different components
# TODO - make layered scheduling plot for comparison
# TODO - make scenario comparison plots, perhaps use kwargs, allow n number of comparisons


def cost(results: Result, x: CostX, y: CostY, location: str = None, fig_size: tuple = (12, 6), bar_width: float = 0.5, font_size: int = 16, color: str = 'blue', usetex: bool = False):
    """Plots the cost of processes, such as capex, vopex, fopex, or total

    Args:
        results (Result): results
        x (CostX): one of CostX.LOCATION_WISE, CostX.PROCESS_WISE
        y (CostY): one of CostY.TOTAL, CostY.CAPEX, CostY.FOPEX, CostY.VOPEX
        location (str, optional): location to plot for, applicable for CostX.PROCESS_WISE. Defaults to None.
        fig_size (tuple, optional): Defaults to (12,6).
        bar_width (float, optional): Defaults to 0.5.
        font_size (int, optional): Defaults to 16.
        color (str, optional): Defaults to 'blue'.
        usetex (bool, optional): Defaults to False.
    """

    if y is CostY.CAPEX:
        res_dict = results.output['Capex_process']
    if y is CostY.VOPEX:
        res_dict = results.output['Vopex_process']
    if y is CostY.FOPEX:
        res_dict = results.output['Fopex_process']

    if y is CostY.TOTAL:
        res_dict = {i: results.output['Capex_process'][i] + results.output['Vopex_process'][i] +
                    results.output['Fopex_process'][i] for i in results.output['Capex_process'].keys()}

    if x == CostX.PROCESS_WISE:

        x_, y_, n_ = ([] for _ in range(3))
        for i in res_dict.keys():
            if i[0] == location:
                if res_dict[i] > 0:
                    y_.append(res_dict[i])
                    x_.append(i[1])
                else:
                    n_.append(i[1])

        rc('font', **{'family': 'serif',
           'serif': ['Computer Modern'], 'size': font_size})
        rc('text', usetex=usetex)
        fig, ax = plt.subplots(figsize=fig_size)
        ax.bar(x_, y_, width=bar_width, zorder=3, color = color)
        y_plot = ''.join(str(y).split('CostY.')[1])
        plt.title(f'Process-wise {y_plot} cost at {location}')
        plt.ylabel('Unit Currency')
        plt.xlabel('Processes')
        plt.yscale('log')
        plt.grid(alpha=0.3, zorder=0)
        plt.rcdefaults()

    if x == CostX.LOCATION_WISE:

        locations = tuple(results.components['locations'].keys())

        weight_counts = dict()

        for i in list(results.components['processes'].keys()):
            vals = []
            for j in res_dict.keys():
                if j[1] == i:
                    vals.append(res_dict[j])
            weight_counts[i] = array(vals)

        rc('font', **{'family': 'serif',
           'serif': ['Computer Modern'], 'size': font_size})
        rc('text', usetex=usetex)
        fig, ax = plt.subplots(figsize=fig_size)
        bottom = zeros(len(locations))

        for boolean, weight_count in weight_counts.items():
            p = ax.bar(locations, weight_count,  width=bar_width,
                       label=boolean, bottom=bottom, zorder=3)
            bottom += weight_count
        y_plot = ''.join(str(y).split('CostY.')[1])
        plt.title(f'Location-wise {y_plot}')
        plt.ylabel('Unit Currency')
        plt.xlabel('Locations')
        plt.yscale('log')
        plt.legend()
        plt.grid(alpha=0.3, zorder=0)
        plt.rcdefaults()
        plt.plot()
    return
