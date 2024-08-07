from typing import Union, TypeAlias
from ...model.data import Data
from ...model.matrix import Matrix
from ...model.program import Program
from ...model.system import System
from ...model.abstract import Abstract

IsSystem: TypeAlias = System
IsProgram: TypeAlias = Program
IsData: TypeAlias = Data
IsMatrix: TypeAlias = Matrix
IsAbstract: TypeAlias = Abstract

IsModel = Union[IsSystem, IsProgram, IsData, IsMatrix, IsAbstract]
