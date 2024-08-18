"""Combined Model of the Scenario

Includes: 
    System Representation Model (System)
    Mathematical Programming Model (Program)
    Data Model (Data)
    Matrix Model (Matrix) which is a matrix representation of the Program
"""

from dataclasses import dataclass, field
from .system import System
from .program import Program
from .data import Data
from .matrix import Matrix

from .._core._handy._dunders import _Dunders


@dataclass
class Model(_Dunders):
    """Modeling Blocks of the Scenario"""

    name: str = field(default=None)

    def __post_init__(self):
        self.system = System(self.name)
        self.data = Data(self.name)
        self.matrix = Matrix(self.name)
        self.program = Program(self.name)
