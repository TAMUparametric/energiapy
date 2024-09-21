"""Mathematical Programming Model
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass, field

from ..core._handy._dunders import _Dunders
from ..core._handy._printers import _Print


if TYPE_CHECKING:
    from ..elements.constraints.bound import Bound
    from ..elements.constraints.boundbound import BoundBound
    from ..elements.constraints.calculate import Calculation
    from .engines.taskmaster import Chanakya
    from .engines.registrar import ChitraGupta
    from .datum import Datum


@dataclass
class Block(_Dunders, _Print):
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

        index = self.registrar.fish(attr=attr, disposition=data.index.args())

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
                index=idx_parent, component=self.component, **cns.varbirth_attrs
            )

        constraint = cns(
            root=self.component, attr=attr, varsym=cns.varsym, prmsym=cns.prmsym
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
class Program(_Dunders, _Print):
    """Mathematical Programming Model"""

    name: str = field(default=None)

    def __post_init__(self):

        self.parameters: list = []
        self.variables: list = []
        self.constraints: list = []
        self.indices: list = []

        self.blocks: list[ProgramBlock] = []

    def __setattr__(self, name: str, block: ProgramBlock):

        if isinstance(block, ProgramBlock):
            self.parameters.extend(block.parameters)
            self.variables.extend(block.variables)
            self.constraints.extend(block.constraints)

            self.blocks.append(block)

        super().__setattr__(name, block)

    def eqns(self, at_cmp: IsDfn = None, at_disp: IsDsp = None):
        """Yields all equations in the Program

        Args:
            at_cmp (IsCmp, optional): Component to search for. Defaults to None.
            at_disp (IsDsp, optional): Index (actually Index) to search for. Defaults to None.
        """
        for block in self.blocks:
            for eqn in block.eqns(at_cmp=at_cmp, at_disp=at_disp):
                yield eqn
