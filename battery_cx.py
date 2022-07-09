#%%
"""Example case study on battery optimization
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "1.0.0"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"



import energia
import graph #energia's graphing module
import pandas as pd
import numpy as np
import random
import pickle as pkl
import csv
from itertools import product
from functools import reduce 
from pyomo.environ import *
from pyomo.opt import SolverStatus, TerminationCondition
import time
from subprocess import call
from datetime import datetime, date
from collections import defaultdict
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import json as json
import matplotlib.pyplot as plt
import os 
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)


day_list = [int(i) for i in range(1,366)] #list of days/seasons 
hour_list = [int(i) for i in range(0,24)] #list of hours


cost_metrics_list = ['CAPEX', 'Fixed O&M', 'Variable O&M', 'units', 'source']

bigM= 10**6

LiI_c= energia.process(name= 'LiI_c', prod_max= bigM, trl= 'nrel', block= 'power_storage', label= 'Lithium-ion battery')
LiI_d= energia.process(name= 'LiI_d', prod_max= bigM, trl= 'discharge', block= 'power_storage', label= 'Lithium-ion battery discharge')
PV= energia.process(name= 'PV', year= 0, prod_max= bigM, gwp= 53, land= 13320/1800, trl= 'nrel', block= 'power_generation', label= 'Solar photovoltaics (PV) array')




#%%
conversion_dict  = energia.get_data('conversion')

m.Cap_P = Var(m.locations, m.processes, m.years, within = NonNegativeReals, doc = 'production (MW or kg/h) capacity of process at location') 





# %%
