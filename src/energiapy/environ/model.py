"""Combined Model of the Scenario

Includes: 
    System Representation Model (System)
    Mathematical Programming Model (Program)
    Data Model (Data)
    Matrix Model (Matrix) which is a matrix representation of the Program
"""

from dataclasses import dataclass, field

from ..core._handy._dunders import _Dunders
from .engines.registrar import ChitraGupta
from .engines.taskmaster import Chanakya
from .renditions.data import Data
from .renditions.matrix import Matrix
from .renditions.program import Program
from .renditions.system import System


@dataclass
class Renditions(_Dunders):
    """Individual Renditions of the Model

    Attributes:
        name (str): name, takes from the name of the Scenario
    """

    name: str = field(default=None)

    def __post_init__(self):
        self.system = System(name=self.name)
        self.data = Data(name=self.name)
        self.matrix = Matrix(name=self.name)
        self.program = Program(name=self.name)
        # Update name after setting the rest
        # The name of the scenario is taken as is
        self.name = f'{self.cname()}|{self.name}|'


@dataclass
class Engines(_Dunders):
    """Engines of the Model

    Attributes:
        name (str): name, takes from the name of the Scenario
    """

    name: str = field(default=None)

    def __post_init__(self):
        self.taskmaster = Chanakya(name=self.name)
        self.registrar = ChitraGupta(name=self.name, taskmaster=self.taskmaster)
        # Update name after setting the rest
        # The name of the scenario is taken as is
        self.name = f'{self.cname()}|{self.name}|'


@dataclass
class Model(_Dunders):
    """The Model of the Scenario

    Attributes:
        name (str): name, takes from the name of the Scenario
    """

    name: str = field(default=None)

    def __post_init__(self):

        self.blocks = Renditions(name=self.name)
        self.engines = Engines(name=self.name)
        # Update name after setting the rest
        # The name of the scenario is taken as is
        self.name = f'{self.cname()}|{self.name}|'

    @property
    def system(self):
        """System Block"""
        return self.blocks.system

    @property
    def data(self):
        """Data Block"""
        return self.blocks.data

    @property
    def matrix(self):
        """Matrix Block"""
        return self.blocks.matrix

    @property
    def program(self):
        """Program Block"""
        return self.blocks.program

    @property
    def taskmaster(self):
        """Taskmaster Engine"""
        return self.engines.taskmaster

    @property
    def registrar(self):
        """Registrar Engine"""
        return self.engines.registrar
