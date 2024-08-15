from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._core._handy._dunders import _Dunders
from ..constraints.taskmaster import taskmaster
from ..constraints.rulebook import rulebook
from ..constraints.constraint import Constraint
from .data import DataBlock

if TYPE_CHECKING:
    from .._core._aliases._is_component import IsComponent
    from .._core._aliases._is_variable import IsTask


@dataclass
class ProgramBlock(_Dunders):
    """Block of Program"""

    component: str = field(default=None)

    def __post_init__(self):
        self.name = f'Program|{self.component}|'
        self.variables, self.constraints, self.parameters = ([] for _ in range(3))

    def __setattr__(self, name, value):

        if isinstance(value, DataBlock):
            for attr in value.attrs:
                
                    variable = taskmaster[type(self.component)][attr](disposition = getattr())
                    
                    self.variables.append(variable)
                    rules = rulebook.find(variable)

                for rule in self.rules: 
                    constraint = Constraint(condition=rule.condition, variable=self.)
                
            
        super().__setattr__(name, value)


@dataclass
class Program(_Dunders):
    """Mathematical Programming Model"""

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Progam|{self.name}|'
        # self.variables, self.constraints, self.parameters = ([] for _ in range(3))
