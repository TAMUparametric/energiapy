"""Modeling blocks
"""

from typing import TypeAlias, Union

from ...blocks.data import Data, DataBlock
from ...blocks.matrix import Matrix
from ...blocks.model import Model
from ...blocks.program import Program, ProgramBlock
from ...blocks.rulebook import RuleBook
from ...blocks.system import System
from ...blocks.taskmaster import TaskMaster
from ...model.scenario import Scenario

IsScenario: TypeAlias = Scenario

# submodels
IsData: TypeAlias = Data
IsDataBlock: TypeAlias = DataBlock
IsMatrix: TypeAlias = Matrix
IsProgram: TypeAlias = Program
IsProgramBlock: TypeAlias = ProgramBlock
IsSystem: TypeAlias = System
IsTaskMaster: TypeAlias = TaskMaster

IsRuleBook: TypeAlias = RuleBook


IsBlock = Union[IsData, IsMatrix, IsProgram, IsSystem, IsTaskMaster, IsRuleBook]
IsModel: TypeAlias = Model
