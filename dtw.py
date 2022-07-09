
"""Dynamic time warping (DTW) for clustering of data with disparate temporal resolution
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "1.0.0"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

#%%
from importlib.abc import ResourceReader
import energia
import graph  # energia's graphing module
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
# from matplotlib.ticker import (
#     MultipleLocator, FormatStrFormatter, AutoMinorLocator)
import matplotlib.ticker as ticker
from matplotlib.colors import ListedColormap
from matplotlib import rc
import math

# =================================================================================================================
# *                                                  Time-varying Parameters
# =================================================================================================================
# Time-varying conversion factor
power_output_df = pd.read_csv('power_output_df.csv').drop(columns='datetime')

# Time-varying cost factor
ng_price_df = energia.make_henry_price_df(
    file_name='Henry_Hub_Natural_Gas_Spot_Price_Daily.csv', year=2019, stretch=False)

#%%
series1 = [i for i in power_output_df['WF']]
series2 = [i for i in ng_price_df['CH4']]

def dtw_cluster(series1:list, series2:list):
    """clusters time series data with disparate temporal resolution 
    using dynamic time warping (dtw)

    Args:
        series1 (list): time series 1
        series2 (list): time series 2

    Returns:
        _type_: _description_
    """       
    series1 = [i/max(series1) for i in series1]
    series2 = [i/max(series2) for i in series2]
    # series1 = series1[:36]
    # series2 = series2[:80]
    matrix = [[10**10 for i in range(len(series1) + 1)] for j in range(len(series2) + 1)]
    matrix[0][0] = 0
    for i,j in zip(range(1, len(series1)+1), range(1, len(series2) + 1)):
        cost = abs(series1[i-1] - series2[j-1]) 
        prev = min([matrix[i-1][j], matrix[i][j-1], matrix[i-1][j-1]]) 
        matrix[i][j] = cost + prev
    # for i in range(len(series2)):
    #     print(min(matrix[i]))
    return matrix

matrix = dtw_cluster(series1 = series1, series2= series2)
 ##Call DTW function
# dtw_cost_matrix = fill_dtw_cost_matrix(series1,series2)
# %%

series = [min(matrix[i]) for i in range(365)]

floor = [math.floor(i) for i in series]
#%%
for i in range(max(floor)):
    x = floor.count(i)
    if x > 0: 
        print(i, x)
#%%
