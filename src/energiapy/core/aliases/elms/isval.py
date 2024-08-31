"""Aliases for Program (Parameter) Value Elements 
"""

from ....elements.values.constant import Constant
from ....elements.values.dataset import DataSet
from ....elements.values.m import M
from ....elements.values.theta import Theta

# Parameter Values
type IsVal = Constant | DataSet | M | Theta
