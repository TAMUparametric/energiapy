"""Mathematical Programming Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._core._handy._dunders import _Dunders
from ..constraints.rulebook import rulebook
from ..constraints.taskmaster import taskmaster
from ..disposition.disposition import Disposition
from ._base._block import _Block
from .data import DataBlock

if TYPE_CHECKING:
    from .._core._aliases._is_block import IsDataBlock, IsIndex
    from .._core._aliases._is_component import IsDefined
    from .._core._aliases._is_value import IsValue
    from .._core._aliases._is_element import IsElement


@dataclass
class ProgramBlock(_Dunders):
    """Block of Program
    The Parameters, Variables, Constraints are defined here

    Attributes:
        component (IsComponent): Component to which the ProgramBlock belongs
    """

    component: IsDefined = field(default=None)

    def __post_init__(self):
        self.name = f'Program|{self.component}|'
        # Declare empty lists to hold the generated elements
        self.variables, self.constraints, self.parameters, self.dispositions = (
            [] for _ in range(4)
        )

    def __setattr__(self, name: str, datablock: IsDataBlock):

        if isinstance(datablock, DataBlock):
            # DataBlocks collect the attrs which have been declared
            for attr in datablock.attrs:
                for data in getattr(datablock, attr):
                    # if list loop over lower bound and upper bound
                    # the VarBnd enums are already set in the DataBlock
                    if isinstance(data, list):
                        for d in data:
                            self.birth_elements(d, attr)
                    else:
                        self.birth_elements(data, attr)

        super().__setattr__(name, datablock)

    def birth_elements(self, value: IsValue, attr: str):
        """Makes ass, kicks elements

        The dispostion determined in the DataBlock is used
        Variable is generated
        Variables know what Parameters or Parent Variable they need
        Those are generated if not already made

        rulebook knows the rule to generate constriant

        Args:
            value(IsValue): Is M, Theta, DataSet, Constant

        """

        if isinstance(value, set):
            # This is only used if one of the Paramters is Incidental
            # capex, opex for example
            for i in value:
                self.birth_elements(value=i, attr=attr)

        else:
            if value.incdntl:
                # if parameter is incidental
                var = taskmaster[type(self.component)][f'{attr}_i']
            else:
                var = taskmaster[type(self.component)][attr]

            # Variable is declared, the Disposition is used
            variable = var(disposition=value.disposition, component=self.component)
            # The collections are updated
            self.add(variable)
            self.add(variable.disposition)

            # The Variable can have a:
            # 1. Parent Variable: needed to bound or determine this variable
            # Examples: Operate < Capacity; ExpCap = CapEx * Capacity
            # 2. Child Component: This is not present in the Parent Variable
            # So the disposition of the Parent Variable needs to be made childless
            # In the CapEx example, ExpCap has Cash, but Capacity does not
            # so remove Cash Component in Capacity Dispositio
            if var.parent():
                if var.child():
                    # This is the index of the Disposition without the child Component
                    index_childless = variable.disposition.childless(var.child())

                    # The index is found, to run existence check
                    par_index = tuple([i for i in index_childless.values() if i])

                    # If Disposition exists already, get the existing and use it for child
                    # If does not exist, make a new one

                    if par_index in self.indices:
                        # Get the existing Disposition
                        disposition_par = self.dispositions[
                            self.indices.index(par_index)
                        ]
                    else:
                        # If not make a new one and update the collection
                        disposition_par = Disposition(**index_childless)
                        self.add(disposition_par)

                else:
                    # if no Parent then the Parameter Disposition is the same as variable
                    disposition_par = variable.disposition

                # This has the object of the Parent Variable
                parent_var = var.parent()

                # Get all the Variables of the same type as the Parent Variable
                # That already exist
                samevars = [
                    var_ for var_ in self.variables if isinstance(var_, parent_var)
                ]

                # Get the indices of the exisiting variables
                samevars_indices = [var_.disposition.index for var_ in samevars]

                if disposition_par.index in samevars_indices:
                    # If Variable needed for parent exists with the same index
                    # Get the existing Variable
                    parent = samevars[samevars_indices.index(disposition_par.index)]

                else:
                    # If does not exist, then make a new one and update the collection
                    parent = parent_var(
                        disposition=disposition_par, component=self.component
                    )
                    self.add(parent)

            else:
                # Bruce Wayne Variable
                parent = None

            # Get the rules to generate the constraint
            # Variables can have multiple rules
            rules = rulebook.find(var)

            # So iter over them
            for rule in rules:
                if rule.parameter:
                    # If the rule needs a parameter, then make it
                    parameter = rule.parameter(value)
                    self.add(parameter)

                else:
                    parameter = None

                # Generate the constraint
                constraint = rule.constraint(
                    variable=variable,
                    parent=parent,
                    parameter=parameter,
                    varbnd=value.varbnd,
                )

                self.add(constraint)

    def add(self, element: IsElement):
        """Updates the collection lists of elements in the program block

        Args:
            element (IsElement): Variable, Constraint, or Parameter to be added to a particular collection
        """

        list_curr = getattr(self, element.collection())
        setattr(self, element.collection(), sorted(set(list_curr) | {element}))

    def eqns(self, at_cmp: IsDefined = None, at_disp: IsIndex = None):
        """Prints all equations in the program

        Args:
            at_cmp (IsComponent, optional): Component to search for. Defaults to None.
            at_disp (IsDisposition, optional): Disposition to search for. Defaults to None.
        """
        if at_cmp:
            constraints = self.at_cmp(at_cmp)

        if at_disp:
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

    def at_cmp(self, component: IsDefined):
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
    def blocks(self):
        """Returns all blocks in the program
        Do not sort this, the order is as defined by the user
        """
        return [getattr(self, i) for i in self.components()]

    @property
    def variables(self):
        """Returns all variables in the program"""
        return self.fetch('variables')

    @property
    def constraints(self):
        """Returns all constraints in the program"""
        return self.fetch('constraints')

    @property
    def parameters(self):
        """Returns all parameters in the program"""
        return self.fetch('parameters')

    @property
    def dispositions(self):
        """Returns all dispositions in the program"""
        return self.fetch('dispositions')

    def eqns(self, at_cmp: IsDefined = None, at_disp: IsIndex = None):
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

    def fetch(self, element: str) -> list:
        """Fetches input data of a particular type
        Args:
            element (str): The type of element to fetch parameters, variables, constraints, dispositions
        """
        return sorted(
            sum(
                [
                    getattr(block, element)
                    for block in self.blocks
                    if getattr(block, element)
                ],
                [],
            )
        )
