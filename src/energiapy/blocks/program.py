from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._core._handy._dunders import _Dunders
from ..constraints.rulebook import rulebook
from ..constraints.taskmaster import taskmaster
from ..disposition.disposition import Disposition
from .data import DataBlock

if TYPE_CHECKING:
    from .._core._aliases._is_component import IsComponent
    from .._core._aliases._is_data import IsData
    from .._core._aliases._is_element import IsElement


@dataclass
class ProgramBlock(_Dunders):
    """Block of Program"""

    component: IsComponent = field(default=None)

    def __post_init__(self):
        self.name = f'Program|{self.component}|'
        self.variables, self.constraints, self.parameters = ([] for _ in range(3))

    def __setattr__(self, name, value):

        if isinstance(value, DataBlock):
            for attr in value.attrs:
                for data in getattr(value, attr):

                    if isinstance(data, list):
                        for d in data:
                            self.make_constraints(d, attr)
                    else:
                        self.make_constraints(data, attr)

        super().__setattr__(name, value)

    def make_constraints(self, data: IsData, attr: str):
        """Makes ass, kicks constraints"""
        if isinstance(data, set):
            for i in data:
                self.make_constraints(data=i, attr=attr)

        else:
            if data.incdntl:
                var = taskmaster[type(self.component)][f'{attr}_i']
            else:
                var = taskmaster[type(self.component)][attr]

            variable = var(disposition=data.disposition)
            self.add(variable)

            if var.parent():

                if var.child():
                    disposition_par = Disposition(
                        **variable.disposition.childless(var.child())
                    )
                else:
                    disposition_par = variable.disposition
                print(variable)
                parent = var.parent()(disposition=disposition_par)
                self.add(parent)

            else:
                parent = None

            rules = rulebook.find(var)

            for rule in rules:

                if rule.parameter:
                    parameter = rule.parameter(data)
                    self.add(parameter)

                else:
                    parameter = None

                constraint = rule.constraint(
                    variable=variable,
                    parent=parent,
                    parameter=parameter,
                    varbnd=data.varbnd,
                )

                self.add(constraint)

    def add(self, element: IsElement):
        """Updates the collection lists of elements in the program block

        Args:
            element (IsElement): Variable, Constraint, or Parameter to be added to a particular collection
        """

        list_curr = getattr(self, element.collection())
        setattr(self, element.collection(), sorted(set(list_curr) | {element}))


@dataclass
class Program(_Dunders):
    """Mathematical Programming Model"""

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Progam|{self.name}|'
        self.variables, self.constraints, self.parameters = ([] for _ in range(3))

    def __setattr__(self, name, value):

        if isinstance(value, ProgramBlock):

            self.parameters = sorted(set(self.parameters) | set(value.parameters))
            self.variables = sorted(set(self.variables) | set(value.variables))
            self.constraints = sorted(set(self.constraints) | set(value.constraints))

        super().__setattr__(name, value)
