"""Combined Model of the Scenario

Includes: 
    System Representation Model (System)
    Mathematical Programming Model (Program)
"""

from dataclasses import dataclass, field

from ..core._handy._dunders import _Dunders
from .engines.registrar import ChitraGupta
from .engines.taskmaster import Chanakya
from .program import Program
from .system import System


@dataclass
class Model(_Dunders):
    """The Model of the Scenario

    Attributes:
        name (str): name, takes from the name of the Scenario
    """

    name: str = field(default=None)
    m: float = field(default=None)

    def __post_init__(self):

        self.system = System(self.name)
        self.program = Program(self.name)
        self.taskmaster = Chanakya(self.name)
        self.registrar = ChitraGupta(self.name, self.system, self.taskmaster)
        # Update name after setting the rest
        # The name of the scenario is taken as is
        self.name = f'Model|{self.name}|'
