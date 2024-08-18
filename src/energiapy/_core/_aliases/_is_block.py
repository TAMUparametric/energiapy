"""Modeling blocks
"""

from typing import TypeAlias, Union, Tuple

from ...blocks.data import Data
from ...blocks.matrix import Matrix
from ...blocks.program import Program
from ...blocks.scenario import Scenario
from ...blocks.system import System
from ...blocks.model import Model
from ...disposition.disposition import Disposition
from ._is_component import IsComponent

IsDisposition: TypeAlias = Disposition
IsIndex: TypeAlias = Tuple[IsComponent]
IsScenario: TypeAlias = Scenario

# submodels
IsData: TypeAlias = Data
IsMatrix: TypeAlias = Matrix
IsProgram: TypeAlias = Program
IsSystem: TypeAlias = System

IsBlock = Union[IsData, IsMatrix, IsProgram, IsSystem]
IsModel: TypeAlias = Model
