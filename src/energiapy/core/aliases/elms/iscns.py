"""Aliases for Program Constraint Elements 
"""

from ....elements.constraints.bind import Bind
from ....elements.constraints.calculate import Calculate
from ....elements.constraints.sumover import SumOver

type IsCns = Bind | Calculate | SumOver
