from typing import Union

from ...model.data import Data
from ...model.matrix import Matrix
from ...model.program import Program
from ...model.system import System

IsSystem = System
IsProgram = Program
IsData = Data
IsMatrix = Matrix


IsModel = Union[IsSystem, IsProgram, IsData, IsMatrix]
