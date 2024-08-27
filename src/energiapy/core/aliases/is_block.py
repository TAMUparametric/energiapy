"""Modeling blocks
"""

from typing import Tuple, TypeAlias, Union

from ...blocks.data import Data, DataBlock
from ...blocks.matrix import Matrix
from ...blocks.model import Model
from ...blocks.program import Program, ProgramBlock
from ...blocks.system import System
from ...indices.disposition import Disposition
from ...model.scenario import Scenario
from .is_component import IsComponent

IsDisposition: TypeAlias = Disposition
IsIndex: TypeAlias = Tuple[IsComponent]
IsScenario: TypeAlias = Scenario

# submodels
IsData: TypeAlias = Data
IsDataBlock: TypeAlias = DataBlock
IsMatrix: TypeAlias = Matrix
IsProgram: TypeAlias = Program
IsProgramBlock: TypeAlias = ProgramBlock
IsSystem: TypeAlias = System

IsBlock = Union[IsData, IsMatrix, IsProgram, IsSystem]
IsModel: TypeAlias = Model
