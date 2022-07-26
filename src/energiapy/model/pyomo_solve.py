#%%
"""pyomo_solve
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, SolverFactory
from ..components.result import Result

def solve(instance:ConcreteModel, solver:str, name:str, saveformat:str = None, tee:bool = True) -> Result:
    output = SolverFactory(solver, solver_io= 'python').solve(instance, tee = True)
    results = Result(name= name, instance= instance, output = output)

    if saveformat is not None:
        results.saveoutputs(name + saveformat)
    
    return results




# %%
