"""Combined Model of the Scenario

Includes: 
    System Representation Model (System)
    Mathematical Programming Model (Program)
    Data Model (Data)
    Matrix Model (Matrix) which is a matrix representation of the Program
"""

from dataclasses import dataclass, field

from ..core._handy._dunders import _Dunders
from .attr import Attr
from .data import Data
from .matrix import Matrix
from .program import Program
from .system import System


@dataclass
class Model(_Dunders):
    """Modeling Blocks of the Scenario

    Attributes:
        name (str): name, takes from the name of the Scenario
    """

    name: str = field(default=None)

    def __post_init__(self):
        self.system = System(name=self.name)
        self.data = Data(name=self.name)
        self.matrix = Matrix(name=self.name)
        self.program = Program(name=self.name)
        self.attr = Attr(name=self.name)
        self.name = f'Model|{self.name}|'
