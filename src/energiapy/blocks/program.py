"""Mathematical Programming Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._core._handy._dunders import _Dunders
from ..constraints.rulebook import rulebook
from ..constraints.taskmaster import taskmaster
from ..disposition.disposition import Disposition
from .data import DataBlock
from ._base._block import _Block


if TYPE_CHECKING:
    from .._core._aliases._is_component import IsComponent
    from .._core._aliases._is_data import IsData
    from .._core._aliases._is_element import IsElement
    from .._core._aliases._is_block import IsIndex


@dataclass
class ProgramBlock(_Dunders):
    """Block of Program"""

    component: IsComponent = field(default=None)

    def __post_init__(self):
        self.name = f'Program|{self.component}|'
        self.variables, self.constraints, self.parameters, self.dispositions = (
            [] for _ in range(4)
        )

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

            self.add(variable.disposition)

            if var.parent():

                if var.child():

                    index_childless = variable.disposition.childless(var.child())

                    par_index = tuple([i for i in index_childless.values() if i])

                    # If Disposition exists already, get the existing and use it for child
                    # If does not exist, make a new one

                    if par_index in self.indices:
                        disposition_par = self.dispositions[
                            self.indices.index(par_index)
                        ]
                    else:
                        disposition_par = Disposition(**index_childless)
                        self.add(disposition_par)

                else:
                    disposition_par = variable.disposition

                parent_var = var.parent()

                samevars = [
                    var_ for var_ in self.variables if isinstance(var_, parent_var)
                ]

                samevars_indices = [var_.disposition.index for var_ in samevars]

                # If Variable needed for parent exists with the same index, do not create a new one
                # If does not exist, make a new one
                if disposition_par.index in samevars_indices:
                    parent = samevars[samevars_indices.index(disposition_par.index)]

                else:
                    parent = parent_var(disposition=disposition_par)
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

    def eqns(self, at_cmp: IsComponent = None, at_disp: IsIndex = None):
        """Prints all equations in the program

        Args:
            at_cmp (IsComponent, optional): Component to search for. Defaults to None.
            at_disp (IsDisposition, optional): Disposition to search for. Defaults to None.
        """
        if at_cmp:
            constraints = self.at_cmp(at_cmp)

        elif at_disp:
            constraints = self.at_disp(at_disp)

        if not any([at_cmp, at_disp]):
            constraints = self.constraints

        for constraint in constraints:
            print(constraint.equation)

    def at_disp(self, disposition: IsIndex):
        """Returns constraints defined for disposition throughout the program

        Args:
            disposition (IsIndex): disposition (actually index) to be searched for
        """
        return [
            cons for cons in self.constraints if cons.disposition.index == disposition
        ]

    def at_cmp(self, component: IsComponent):
        """Returns constraints defined for component throughout the program

        Args:
            component (IsComponent): component to be searched for
        """

        return [
            cons for cons in self.constraints if component in cons.disposition.index
        ]

    @property
    def indices(self):
        """Returns all indices in the ProgramBlock"""
        return [i.index for i in self.dispositions]

    @property
    def var_types(self):
        """Returns all variables types already declared in the ProgramBlock"""
        return [type(i) for i in self.variables]


@dataclass
class Program(_Block):
    """Mathematical Programming Model"""

    name: str = field(default=None)

    def __post_init__(self):
        _Block.__post_init__(self)
        self.name = f'Program|{self.name}|'

    @property
    def variables(self):
        """Returns all variables in the program"""
        return [block.variables for block in self.blocks if block.variables]

    @property
    def constraints(self):
        """Returns all constraints in the program"""
        constraints = [block.constraints for block in self.blocks if block.constraints]
        return sum(constraints, [])

    @property
    def parameters(self):
        """Returns all parameters in the program"""
        return [block.parameters for block in self.blocks if block.parameters]

    @property
    def dispositions(self):
        """Returns all dispositions in the program"""
        disps = [block.dispositions for block in self.blocks if block.parameters]
        return sum(disps, [])

    @property
    def blocks(self):
        """Returns all blocks in the program"""
        return [getattr(self, i) for i in self.components()]

    def eqns(self, at_cmp: IsComponent = None, at_disp: IsIndex = None):
        """Prints all equations in the Program

        Args:
            at_cmp (IsComponent, optional): Component to search for. Defaults to None.
            at_disp (IsIndex, optional): Disposition (actually Index) to search for. Defaults to None.
        """

        if at_cmp:
            print(f'-----------{at_cmp} Constraints -----------')

        if at_disp:
            print(f'-----------Constraints at Disposition:{at_disp}-----------')

        for block in self.blocks:

            if not any([at_cmp, at_disp]):
                print(f'-----------{block.component} Constraints -----------')

            block.eqns(at_cmp=at_cmp, at_disp=at_disp)

            if not any([at_cmp, at_disp]):
                print('')
