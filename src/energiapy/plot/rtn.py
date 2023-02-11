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
from graphviz import Digraph


def rtn(location: Location):
    processes = location.processes
    resources = location.resources
    resources_map = location.resources_map
    
    
    
    
    


# def capacity_factor(process: Process, location: Location, \
#     fig_size:tuple = (12,6), font_size:int = 16, color:str ='blue', usetex:bool = False):
#     """generates a plot for varying capacity factor of process

#     Args:
#         process (Process): process data object
#         location (Location): location
#         font_size (int, optional): font size. Defaults to 16.
#         fig_size (tuple, optional): figure size. Defaults to (12,6).
#         color (str, optional): color of plot. Defaults to 'blue'.
#         usetex (bool, optional): False, if using latex font, need Tex set up (prone to errors). Defaults to 'False'.
#     """

#     rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})
#     rc('text', usetex=False)
#     fig, ax = plt.subplots(figsize= fig_size)
#     y_ = list(location.capacity_factor[process.name].values())
#     x_ = [i for i in range(len(y_))]
#     ax.plot(x_, y_, linewidth=0.5, color=color)
#     ax = axis_formatter(axes= ax, xcord = x_, axis_labels= 'M')
#     plt.title(f'Conversion factor for {process.label} in {location.label}')
#     plt.ylabel('Normalized capacity factor')
#     plt.grid(alpha=0.3)
#     plt.rcdefaults()
#     return



# 3 examples - Without time (steam utility system) - With time (distribution system) - Alternative distribution visualization
# Without time (steam utility system):

## Visualization of the solution ##
# nrg_viz = ['EP','Eq_s']
# def draw_solution(model, results):    
#     dot = Digraph(graph_attr={'rankdir': 'LR'}, node_attr={'fontcolor':'blue', 'shape' : 'box'})
#     # Mass
#     for steam in model.steam:
#         dot.node(steam, "{:s}".format(steam), shape='doublecircle')
#     for IntEq in model.eq:
#         dot.node(IntEq, "{:s}".format(IntEq), shape='diamond')
#     for nonsteam in model.res_nonSteam:
#         dot.node(nonsteam, "{:s}".format(nonsteam), shape='circle')
#     for sink in model.sinks:
#         dot.node(sink, "{:s}".format(sink), shape='box')
#     for source in model.steamproducers:
#         dot.node(source, "{:s}".format(source), shape='ellipse')
#     for es in model.ES:
#         dot.node(es,"{:s}".format(es), shape='polygon')
#     for connection1 in model.toRes:
#         if model.toRes[connection1].value != 0 and model.toRes[connection1].value != None:
#             flow = model.toRes[connection1].value
#             dot.edge(*connection1, label=("%g" % (flow)) if flow > 0 else '', 
#                                           color='red' if flow > 0 else 'lightgray', 
#                                           fontname='courier', fontsize='10')
#     for connection2 in model.fromRes:
#         if model.fromRes[connection2].value != 0 and model.fromRes[connection2].value != None:
#             flow = model.fromRes[connection2].value
#             dot.edge(*connection2, label=("%g" % (flow)) if flow > 0 else '', 
#                                           color='red' if flow > 0 else 'lightgray', 
#                                           fontname='courier', fontsize='10')                        
#             #dot.edge(*connection)
#     # Energy
#     for nrg in nrg_viz:
#         dot.node(nrg, "{:s}".format(nrg), shape='diamond',color = 'darkviolet')
#     for ep in model.EP:
#         if model.nrgEP[ep].value != 0 and model.nrgEP[ep].value != None:
#             connection={ep,'EP'}
#             dot.edge(*connection,label=("%g" % (model.nrgEP[ep].value)), color='darkturquoise', fontname='courier', fontsize='10', arrowhead='none')
#     for eq in model.Eq_s:
#         connection={eq,'Eq_s'}
#         if model.nrgEQs[eq].value != 0 and model.nrgEQs[eq].value != None:
#             dot.edge(*connection,label=("%g" % (model.nrgEQs[eq].value)), color='darkgreen', fontname='courier', fontsize='10', arrowhead='none')
#         #if model.nrgEQs[eq].value == 0:
#         #    dot.edge(*connection,label=("%g" % (model.nrgEQs[eq].value)), color='darkolivegreen1', fontname='courier', fontsize='10', arrowhead='none')
#     for es in model.ES:
#         connection={'EP',es}
#         if model.ED_sinks[es] != 0 and model.ED_sinks[es] != None:
#             dot.edge(*connection,label=("%g" % (model.ED_sinks[es])), color='gold', fontname='courier', fontsize='10', arrowhead='none')
#     return dot

# # Draw the actual solution with 
# # draw_solution(model, results)
# draw_solution(model, results).view()

# # With time (distribution system): 

# def draw_solution(model, results, time):    
#     dot = Digraph(graph_attr={'rankdir': 'LR'}, node_attr={'fontcolor':'blue', 'shape' : 'box'})
#     sink_demandVisF = dictio(AvailSinks, Sink_Demand)
#     source_suplyVisF = dictio(AvailSources, Sources_UB)
#     c1 = restr_conno(AvailSources, AvailPools)
#     c2 = restr_conno(AvailPools, AvailPools)
#     c3 = restr_conno(AvailPools, AvailSinks)
#     for pool in model.pools:
#         dot.node(pool, "{:s}".format(pool), shape='doublecircle', xlabel="storage level\n \u003D{:g}".format(model.sl[pool,time].value))
#         #dot.node(pool, "{:s}".format(pool), shape='doublecircle')
#     for sink in model.sinks:
#         dot.node(sink, "{:s}\n demand \u003D{:g}".format(sink, model.demand_sink[sink,time]), shape='box')
#     for source in model.sources:
#         dot.node(source, "{:s}\n supply \u003D{:g}".format(source, model.supply_source[source,time]), shape='ellipse')
#     for connection in c1:
#         if c1[connection] == 1:
#             try:
#                 flow = model.sp[connection,time].value 
#             #dot.edge(*connection, label=("%g" % (flow) if flow > 0 else '', color='red' if flow > 0 else 'lightgray', fontname='courier', fontsize='10')
#             except KeyError:
#                     try:  
#                         flow = model.pp[connection,time].value 
#                     except KeyError:
#                         flow = model.ps[connection,time].value 
#             if flow is None:
#                 flow = 0
#             #print(flow) 
#             dot.edge(*connection, label=("%g" % (flow)) if flow > 0 else '', 
#                                           color='red' if flow > 0 else 'lightgray', 
#                                           fontname='courier', fontsize='10')                   
#     for connection in c2:
#         if c2[connection] == 1:
#             try:
#                 flow = model.sp[connection,time].value 
#             #dot.edge(*connection, label=("%g" % (flow) if flow > 0 else '', color='red' if flow > 0 else 'lightgray', fontname='courier', fontsize='10')
#             except KeyError:
#                     try:  
#                         flow = model.pp[connection,time].value 
#                     except KeyError:
#                         flow = model.ps[connection,time].value 
#             if flow is None:
#                 flow = 0
#             #print(flow) 
#             dot.edge(*connection, label=("%g" % (flow)) if flow > 0 else '', 
#                                           color='red' if flow > 0 else 'lightgray', 
#                                           fontname='courier', fontsize='10')
#     for connection in c3:
#         if c3[connection] == 1:
#             try:
#                 flow = model.sp[connection,time].value 
#             #dot.edge(*connection, label=("%g" % (flow) if flow > 0 else '', color='red' if flow > 0 else 'lightgray', fontname='courier', fontsize='10')
#             except KeyError:
#                     try:  
#                         flow = model.pp[connection,time].value 
#                     except KeyError:
#                         flow = model.ps[connection,time].value 
#             if flow is None:
#                 flow = 0
#             #print(flow) 
#             dot.edge(*connection, label=("%g" % (flow)) if flow > 0 else '', 
#                                           color='red' if flow > 0 else 'lightgray', 
#                                           fontname='courier', fontsize='10')              
#             #dot.edge(*connection)
#     return dot
# # Draw the actual solution with 
# # draw_solution(model, results)
# draw_solution(model, results, 0).view()

# # Alternative distribution visualization:

# # Visualization of the solution
   
# def draw_solution(model, results, time):    
#     dot = Digraph(graph_attr={'rankdir': 'LR'}, node_attr={'fontcolor':'blue', 'shape' : 'box'})
#     sink_demandVisF = dictio(AvailSinks, Sink_Demand)
#     source_suplyVisF = dictio(AvailSources, Sources_UB)
#     for pool in model.pools:
#         dot.node(pool, "{:s}".format(pool), shape='doublecircle', xlabel="storage level\n \u003D{:g}".format(model.sl[pool,time].value))
#     for sink in model.sinks:
#         #dot.node(sink, "{:s}\n demand \u003D{:g}".format(sink, model.demand_sink[sink,time]), shape='box')
#         dot.node(sink, "{:s}".format(sink), shape='box')
#     for source in model.sources:
#         #dot.node(source, "{:s}\n supply \u003D{:g}".format(source, model.supply_source[source,time]), shape='ellipse')
#         dot.node(source, "{:s}".format(source), shape='ellipse')
#     for connection in y:
#         if y[connection] == 1:
#             try:
#                 flow = model.sp[connection,time].value 
#             #dot.edge(*connection, label=("%g" % (flow) if flow > 0 else '', color='red' if flow > 0 else 'lightgray', fontname='courier', fontsize='10')
#             except KeyError:
#                     try:  
#                         flow = model.pp[connection,time].value 
#                     except KeyError:
#                         flow = model.ps[connection,time].value 
#             if flow is None:
#                 flow = 0
#             #print(flow) 
#             dot.edge(*connection, label=("%g" % (flow)) if flow > 0 else '', 
#                                           color='red' if flow > 0 else 'lightgray', 
#                                           fontname='courier', fontsize='10')                   
#             #dot.edge(*connection)
#     return dot
# # Draw the actual solution with 
# # draw_solution(model, results)
# draw_solution(model, results, 0).view()




#TODO - plots are independent of scales, check
#TODO - make bar plots / pie plots for contribution from different components 
#TODO - make layered scheduling plot for comparison 
#TODO - make scenario comparison plots, perhaps use kwargs, allow n number of comparisons 






# %%

# %%