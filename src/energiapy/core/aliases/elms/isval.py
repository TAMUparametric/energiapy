"""Aliases for Program (Parameter) Value Elements 
"""

from typing import TypeAlias

from ....elements.values.constant import Constant
from ....elements.values.dataset import DataSet
from ....elements.values.m import M
from ....elements.values.theta import Theta

# Parameter Values
IsVal: TypeAlias = Constant | DataSet | M | Theta
