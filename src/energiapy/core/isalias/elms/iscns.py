"""Aliases for Program Constraint Elements 
"""

from typing import TypeAlias

from ....elements.constraints.rules.bind import Bind
from ....elements.constraints.rules.calculation import Calculate
from ....elements.constraints.rules.summation import SumOver

IsCns: TypeAlias = Bind | Calculate | SumOver
