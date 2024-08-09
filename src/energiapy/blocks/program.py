from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from .._core._aliases._is_component import IsComponent
    from .._core._aliases._is_task import IsTask


@dataclass
class ProgramBlock(_Dunders):
    """Block of Program"""

    component: IsComponent = field(default=None)
    task: IsTask = field(default=None)

    def __post_init__(self):
        if self.component:
            self.name = f'ProgramBlock|{self.component.name}|'
        elif self.task:
            self.name = f'ProgramBlock|{self.task.name}|'

        self.variables, self.constraints, self.parameters = (
            [] for _ in range(3))


@dataclass
class Program(_Dunders):
    """Mathematical Programming Model"""

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Progam|{self.name}|'
        self.variables, self.constraints, self.parameters = (
            [] for _ in range(3))
