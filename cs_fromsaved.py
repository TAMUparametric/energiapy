#%%

"""
To demonstrate how to load saved results
"""


__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"


from src.energiapy.utils.data_utils import load_results
from src.energiapy.graph import graph

# results = load_results(filename = 'trial.pkl')
results = load_results(filename = 'trial.pkl')
#%%

graph.contribution(results = results, y_axis = 'Capex_process', location= 'A', usetex = True)
graph.contribution(results = results, y_axis = 'Cap_P', location= 'A', usetex = True)

#%%consumption amounts of consumable processes

for i in results.fetch_components(component_type= 'resources', condition = ('cons_max', 'g', 0)):
    graph.schedule(results = results, y_axis = 'C', component= i, location= 'HO', usetex = False)


#%%expenditure on consumable resources
for i in results.fetch_components(component_type= 'resources', condition = ('cons_max', 'g', 0)):
    graph.schedule(results = results, y_axis = 'B', component= i, location= 'HO', usetex = False)    


#%%inventory levels of storable processes
for i in results.fetch_components(component_type= 'resources', condition = ('store_max','g', 0)):
    graph.schedule(results = results, y_axis = 'Inv', component= i, location= 'HO', usetex = True)    


#%%Production on per basis level for processes with varying capacities

for i in results.fetch_components(component_type= 'processes', condition = ('varying', True)):
    graph.schedule(results = results, y_axis = 'P', component= i, location= 'HO', usetex = True)
   

#%%Delta Cap of process with varying capacities 

for i in results.fetch_components(component_type= 'processes', condition = ('varying', True)):
    graph.schedule(results = results, y_axis = 'Delta_Cap_P', component= i, location= 'A', usetex = False)    


# %%


# %%
