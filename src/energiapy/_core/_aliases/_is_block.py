"""Modeling blocks
"""

from typing import TypeAlias, Union

from ...blocks.abstract import Abstract
from ...blocks.data import Data
from ...disposition.disposition import Disposition
from ...blocks.matrix import Matrix
from ...blocks.program import Program
from ...blocks.scenario import Scenario
from ...blocks.system import System

IsDisposition: TypeAlias = Disposition
IsScenario: TypeAlias = Scenario

# submodels
IsAbstract: TypeAlias = Abstract
IsData: TypeAlias = Data
IsMatrix: TypeAlias = Matrix
IsProgram: TypeAlias = Program
IsSystem: TypeAlias = System

IsBlock = Union[IsAbstract, IsData, IsMatrix, IsProgram, IsSystem]
