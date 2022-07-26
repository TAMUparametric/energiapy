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

results = load_results(filename = 'trial.pkl')
graph.schedule(results = results, y_axis = 'P', component= 'WF', location= 'C', usetex = False)

# %%
