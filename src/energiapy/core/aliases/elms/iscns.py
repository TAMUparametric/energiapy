"""Aliases for Program Constraint Elements 
"""

from typing import TypeAlias

from ....elements.constraints.bind import Bind
from ....elements.constraints.calculate import Calculate
from ....elements.constraints.sumover import SumOver

IsCns: TypeAlias = Bind | Calculate | SumOver
