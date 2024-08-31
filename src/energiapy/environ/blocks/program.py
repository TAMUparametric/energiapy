"""Mathematical Programming Model
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from operator import is_not
from typing import TYPE_CHECKING

from ...core._handy._dunders import _Dunders
from ...core._handy._printers import _Print
from ...core.aliases.cmps.iscmp import IsDsp
from ...core.nirop.errors import CacodcarError
from ...elements.dispositions.index import Index
from ._block import _Block
from .data import DataBlock

if TYPE_CHECKING:
    from ..core.aliases.isblk import IsIndex
    from ..core.aliases.isdef import IsDfn, IsIndex
    from ..core.aliases.iselm import IsVariable
    from ..core.aliases.isval import IsValue


class _Fish(ABC):

    @property
    @abstractmethod
    def variables(self):
        """Variables"""

    @property
    @abstractmethod
    def indices(self):
        """Indexs"""

    def taste_catch(self, catch: list):
        """Tastes the catch, sees if there are multiple fishes (vars)
        If not, returns the only fish (var)

        Args:
            catch (list): list of Variabkes caught
        """
        # number of catches
        n_catch = len(catch)

        # There can only be one
        if n_catch > 1:
            raise CacodcarError(
                'We are going to need a bigger boat. Multiple instances of element found'
            )

        # If found a catch, return it
        if n_catch == 1:
            return catch[0]

        # If no catch, then need to check in the full Program Model Block
        if n_catch == 0:
            return False

    def fish_var(self, var: IsVariable, disposition: IsDsp) -> IsVariable:
        """Fishes for an existing variable at a particular disposition in the Program

        The idea is that we should have a unique instance of any Program element

        Args:
            var (IsVariable): Variable type to fish
            disposition (IsIndex): at this Index

        Returns:
            IsVariable: Variable

        Raises:
            CacodcarError: If more than one variable is found
        """

        # seaches for the disposition in the ProgramBlock and check for multiple instances
        return self.taste_catch(
            [
                e
                for e in self.variables
                if isinstance(e, var) and e.disposition == disposition
            ]
        )

    def fish_disp(self, index: IsIndex) -> IsIndex:
        """Fishes for an exisiting disposition with the given index in the Program

        The idea is that we should have a unique instance of any Program element

        Args:
            index (IsIndex): Index to fish

        Returns:
            IsIndex: Index

        Raises:
            CacodcarError: If more than one disposition is found

        """

        # seaches for the disposition in the ProgramBlock and check for multiple instances
        return self.taste_catch([e for e in self.indices if e.disposition == index])


@dataclass
class ProgramBlock(_Fish, _Dunders, _Print):
    """Block of Program
    The Parameters, Variables, Constraints are defined here

    Attributes:
        component (IsCmp): Component to which the ProgramBlock belongs
    """

    component: IsDfn = field(default=None)

    def __post_init__(self):
        self.name = f'Program|{self.component}|'
        # Declare empty dictionaries to hold the generated elements
        # the keys are the attributes of the components
        (
            self.attr_variables,
            self.attr_constraints,
            self.attr_parameters,
            self.attr_indices,
        ) = ({inp: [] for inp in self.component.inputs()} for _ in range(4))

    def __setattr__(self, name: str, datablock: DataBlock):

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
                # if input value is incidental
                var = getattr(self.component.taskmaster, attr).var_i
            else:
                var = getattr(self.component.taskmaster, attr).var

            # This fishes for an existing Variable
            # if not found births one
            variable = self.birth_var(var=var, disposition=value.disposition, attr=attr)

            # The Variable can have a:
            # 1. Parent Variable: needed to bound or determine this variable
            # Examples: Operate < Capacity; ExpSetUp = CapEx * Capacity
            # 2. Child Component: This is not present in the Parent Variable
            # So the disposition of the Parent Variable needs to be made childless
            # In the CapEx example, ExpSetUp has Cash, but Capacity does not
            # so remove Cash Component in Capacity Dispositio

            if var.parent():
                if var.child():
                    # Fish for an existing Dispostion
                    # if not found, births one
                    disp_parent = self.birth_disp(
                        index=variable.disposition.childless(var.child()), attr=attr
                    )

                else:
                    # if no child then the Parent Index is the same as variable
                    disp_parent = variable.disposition

                # This fishes for an existing Parent Variable
                # if not found births one
                parent = self.birth_var(
                    var=var.parent(), disposition=disp_parent, attr=attr
                )

            else:
                # Bruce Wayne Variable
                parent = None

            # Get the rules to generate the constraint
            # Variables can have multiple rules
            rules = self.component.rulebook.find(var)

            # So iter over them
            for rule in rules:
                if rule.parameter:
                    # If the rule needs a parameter, then make it
                    parameter = rule.parameter(value)
                    self.attr_parameters[attr].append(parameter)

                else:
                    parameter = None

                # Generate the constraint
                constraint = rule.constraint(
                    variable=variable,
                    parent=parent,
                    parameter=parameter,
                    varbnd=value.varbnd,
                )
                # update collection
                self.attr_constraints[attr].append(constraint)

    def birth_var(self, var: IsVariable, disposition: IsIndex, attr: str):
        """Creates a variable in the ProgramBlock
        if not found in the ProgramBlock and full Program Model Block

        Args:
            var (IsVariable): Variable to be created
            disposition (IsIndex): Index of the Variable
            attr (str): Attribute of the Component
        """

        # Fish for an existing variable in the ProgramBlock
        catch = self.fish_var(var=var, disposition=disposition)

        if catch:
            # if found return the existing variable
            return catch

        else:
            # if nothing found look in the full Program Model Block
            catch = self.component.program_full.fish_var(
                var=var, disposition=disposition
            )

            if catch:
                # if found in Program Model Block, return the existing variable
                return catch

            else:
                # if still nothing found, then create a new one
                variable = var(disposition=disposition, component=self.component)
                # Update the collections
                self.attr_variables[attr].append(variable)

                # Update the Registrar with the new Index
                # at which var is defined
                self.component.registrar.add(var, disposition)

                return variable

    def birth_disp(self, index: IsIndex, attr: str):
        """Creates a disposition in the ProgramBlock
        if not found in the ProgramBlock and full Program Model Block

        Args:
            index (IsIndex): Index of the Index
            attr (str): Attribute of the Component
        """

        # Fish for an existing disposition in the ProgramBlock
        catch = self.fish_disp(index=index)

        if catch:
            # if existing disposition found, return it
            return catch

        else:
            # if nothing found look in the full Program Model Block
            catch = self.component.program_full.fish_disp(index=index)

            if catch:
                # if found in Program Model Block, return the existing disposition
                return catch

            else:
                # if still nothing found, then create a new disposition
                disp = Index(**index)

                # Update the collections
                self.attr_indices[attr].append(disp)

                return disp

    @property
    def indices(self):
        """Returns all indices in the ProgramBlock"""
        return [i.disposition for i in self.indices]

    @property
    def var_types(self):
        """Returns all variables types already declared in the ProgramBlock"""
        return [type(i) for i in self.variables]

    @property
    def variables(self):
        """Returns all variables in the ProgramBlock"""
        return sum(list(self.attr_variables.values()), [])

    @property
    def constraints(self):
        """Returns all constraints in the ProgramBlock"""
        return sum(list(self.attr_constraints.values()), [])

    @property
    def parameters(self):
        """Returns all parameters in the ProgramBlock"""
        return sum(list(self.attr_parameters.values()), [])

    @property
    def indices(self):
        """Returns all indices in the ProgramBlock"""
        return sum(list(self.attr_indices.values()), [])

    def eqns(self, at_cmp: IsDfn = None, at_disp: IsIndex = None):
        """Yields all equations in the ProgramBlock

        Args:
            at_cmp (IsCmp, optional): Component to search for. Defaults to None.
            at_disp (IsIndex, optional): Index to search for. Defaults to None.
        """
        if at_cmp:
            constraints = self.at_cmp(at_cmp)

        if at_disp:
            constraints = self.at_disp(at_disp)

        if not any([at_cmp, at_disp]):
            constraints = self.constraints

        for constraint in constraints:
            yield constraint.equation

    def at_disp(self, disposition: IsIndex):
        """Returns constraints defined for disposition throughout the program

        Args:
            disposition (IsIndex): disposition (actually index) to be searched for
        """
        return [
            cons
            for cons in self.constraints
            if cons.disposition.disposition == disposition
        ]

    def at_cmp(self, component: IsDfn):
        """Returns constraints defined for component throughout the program

        Args:
            component (IsCmp): component to be searched for
        """

        return [
            cons
            for cons in self.constraints
            if component in cons.disposition.disposition
        ]


@dataclass
class Program(_Fish, _Block, _Print):
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
    def indices(self):
        """Returns all indices in the program"""
        return self.fetch('indices')

    def eqns(self, at_cmp: IsDfn = None, at_disp: IsIndex = None):
        """Yields all equations in the Program

        Args:
            at_cmp (IsCmp, optional): Component to search for. Defaults to None.
            at_disp (IsIndex, optional): Index (actually Index) to search for. Defaults to None.
        """
        for block in self.blocks:
            for eqn in block.eqns(at_cmp=at_cmp, at_disp=at_disp):
                yield eqn

    def fetch(self, element: str) -> list:
        """Fetches input data of a particular type
        Args:
            element (str): The type of element to fetch parameters, variables, constraints, indices
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
