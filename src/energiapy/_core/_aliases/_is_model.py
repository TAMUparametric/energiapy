from typing import TypeAlias, Union

from ...model.abstract import Abstract
from ...model.data import Data
from ...model.matrix import Matrix
from ...model.program import Program
from ...model.system import System

IsSystem: TypeAlias = System
IsProgram: TypeAlias = Program
IsData: TypeAlias = Data
IsMatrix: TypeAlias = Matrix
IsAbstract: TypeAlias = Abstract

IsModel = Union[IsSystem, IsProgram, IsData, IsMatrix, IsAbstract]
