#%%
"""Math utilities  
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

import pandas
import numpy
from sklearn.preprocessing import StandardScaler

def scaler(input_df: pandas.DataFrame, process: str) -> pandas.DataFrame:
    """creates a scaled list from a df column for a process
    useful as input for functions such as reduce_scenario

    Args:
        input_df (pandas.DataFrame): df with values to be scaled
        process (str): process object

    Returns:
        list: scaled list
    """
    rng = range(0, 24)
    col = [process[0:2] + str(i) for i in rng]
    reshaped_df = numpy.reshape(input_df[process].values, (365, 24))
    scale = StandardScaler().fit(reshaped_df)
    scaled_df = pandas.DataFrame(scale.transform(reshaped_df), columns=col)
    return scaled_df


def find_euclidean_distance(cluster_node_a: list, cluster_node_b: list) -> float:
    """finds euclidean distances between two cluster nodes

    Args:
        cluster_node_a (float): index tag for cluster node a
        cluster_node_b (float): index tag for cluster node b

    Returns:
        float: euclidean distance 
    """
    euclidean_distance_ = [
        (a - b)**2 for a, b in zip(cluster_node_a, cluster_node_b)]
    euclidean_distance_ = sum(euclidean_distance_)
    return euclidean_distance_


def generate_connectivity_matrix():
    """generates a connectivity matrixto maintain chronology [..1,0,1..]

    Returns:
        array: matrix with connectivity relations
    """
    connect_ = numpy.zeros((365, 365), dtype=int)
    for i_ in range(len(connect_)):

        if i_ == 0:
            # connect_[i,364] = 1 #uncomment these to generate a cyclic matrix
            connect_[i_, 1] = 1
        elif i_ == 364:
            connect_[i_, 363] = 1
            # connect_[i,0] = 1
        else:
            connect_[i_, i_-1] = 1
            connect_[i_, i_+1] = 1
    return connect_

# %%
