"""Mathematical Programming Model
"""

from __future__ import annotations

from dataclasses import dataclass, field

from typing import TYPE_CHECKING

from ...core._handy._dunders import _Dunders
from ...core._handy._printers import _Print
from ...core.isalias.cmps.iscmp import IsDsp
from ...core.isalias.cmps.isdfn import IsDfn
from ...core.isalias.elms.isval import IsVal
from ...core.isalias.elms.isvar import IsVar
from ...core.nirop.errors import CacodcarError
from ...elements.disposition.index import Index
from ._block import _Block
from .blocks.datablock import DataBlock


if TYPE_CHECKING:
    from ...elements.constraints.bound import Bound
    from ...elements.constraints.boundbound import BoundBound
    from ...elements.constraints.calculate import Calculation
    from ..engines.taskmaster import Chanakya
    from ..engines.registrar import ChitraGupta
    from ..datum import Datum


@dataclass
class ProgramBlock(_Dunders, _Print):
    """Block of Program
    The Parameters, Variables, Constraints are defined here

    Attributes:
        component (IsCmp): Component to which the ProgramBlock belongs
    """

    component: IsDfn = field(default=None)

    def __post_init__(self):
        self.name = f'Program|{self.component}|'

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

    def birth_elements(self, data: IsVal, attr: str):
        """Births the elements of the ProgramBlock"""

        index = self.registrar.fish(attr=attr, disposition=data.index.disposition)

        cns = self.taskmaster.cns(attr)

        rule = cns.rule()
        var = cns.var()
        prm = cns.prm()
        varbirth_attrs = cns.varbirth_attrs

        variable = var(index=index, component=self.component, **varbirth_attrs)
        paramter = prm(value=data, symbol=cns.prmsym)

        if cns.parent:
            idx_parent = self.registrar.fish(
                attr=cns.parent.attr, disposition=index.childless(cns.root)
            )
            parent = rule.parent.var()(
                index=idx_parent, component=self.component, **rule.parent.birth_attrs()
            )

    @property
    def taskmaster(self) -> Chanakya:
        """Returns the Taskmaster"""
        return self.component.taskmaster

    @property
    def registrar(self) -> ChitraGupta:
        """Returns the Registrar"""
        return self.component.registrar

    def eqns(self, at_cmp: IsDfn = None, at_disp: IsDsp = None):
        """Yields all equations in the ProgramBlock

        Args:
            at_cmp (IsCmp, optional): Component to search for. Defaults to None.
            at_disp (IsDsp, optional): Disposition to search for. Defaults to None.
        """
        if at_cmp:
            constraints = self.at_cmp(at_cmp)

        if at_disp:
            constraints = self.at_disp(at_disp)

        if not any([at_cmp, at_disp]):
            constraints = self.constraints

        for constraint in constraints:
            yield constraint.equation

    def at_disp(self, disposition: IsDsp):
        """Returns constraints defined for disposition throughout the program

        Args:
            disposition (IsDsp): disposition to be searched for
        """
        return [
            cons for cons in self.constraints if cons.index.disposition == disposition
        ]

    def at_cmp(self, component: IsDfn):
        """Returns constraints defined for component throughout the program

        Args:
            component (IsCmp): component to be searched for
        """

        return [
            cons for cons in self.constraints if component in cons.index.disposition
        ]


@dataclass
class Program(_Block, _Print):
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

    def eqns(self, at_cmp: IsDfn = None, at_disp: IsDsp = None):
        """Yields all equations in the Program

        Args:
            at_cmp (IsCmp, optional): Component to search for. Defaults to None.
            at_disp (IsDsp, optional): Index (actually Index) to search for. Defaults to None.
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
