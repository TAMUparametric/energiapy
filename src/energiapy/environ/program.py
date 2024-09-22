"""Mathematical Programming Model
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass, field

from ..core._handy._dunders import _Dunders
from ..core._handy._printers import _Print
from ..elements.parameter import Prm
from ..elements.variable import Vrb
from ..elements.constraint import Cns
from ..elements.index import Idx

if TYPE_CHECKING:
    from .datum import Datum
    from ..elements.constraints.bound import Bound
    from ..elements.constraints.boundbound import BoundBound
    from ..elements.constraints.calculate import Calculation
    from .engines.taskmaster import Chanakya
    from .engines.registrar import ChitraGupta

    from ..components.commodity.cash import Cash
    from ..components.commodity.emission import Emission
    from ..components.commodity.land import Land
    from ..components.commodity.resource import Resource
    from ..components.operation.process import Process
    from ..components.operation.storage import Storage
    from ..components.operation.transit import Transit


@dataclass
class Block(_Dunders, _Print):
    """Block of Program
    The Parameters, Variables, Constraints are defined here

    Attributes:
        component (IsCmp): Component to which the ProgramBlock belongs
    """

    component: Emission | Resource | Land | Cash | Process | Storage | Transit = field(
        default=None
    )
    m: float = field(default=None)

    def __post_init__(self):
        self.name = f'Program|{self.component}|'
        self.parameters: list[Prm] = []
        self.variables: list[Vrb] = []
        self.constraints: list[Cns] = []

    def write_constraints(self, datum: Datum, attr: str):
        """Births the elements of the ProgramBlock"""

        index: Idx = self.registrar.fish(attr=attr, disposition=datum.index.args())

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

    def eqns(
        self,
        at_cmp: Emission | Resource | Land | Cash | Process | Storage | Transit = None,
        at_disp: tuple[
            Emission | Resource | Land | Cash | Process | Storage | Transit
        ] = None,
    ):
        """Yields all equations in the ProgramBlock

        Args:
            at_cmp (IsCmp, optional): Component to search for. Defaults to None.
            at_disp (tuple[Emission| Resource | Land | Cash | Process | Storage | Transit], optional): Disposition to search for. Defaults to None.
        """
        if at_cmp:
            constraints = self.at_cmp(at_cmp)

        if at_disp:
            constraints = self.at_disp(at_disp)

        if not any([at_cmp, at_disp]):
            constraints = self.constraints

        for constraint in constraints:
            yield constraint.equation

    def at_disp(
        self,
        disposition: tuple[
            Emission | Resource | Land | Cash | Process | Storage | Transit
        ],
    ):
        """Returns constraints defined for disposition throughout the program

        Args:
            disposition (tuple[Emission| Resource | Land | Cash | Process | Storage | Transit]): disposition to be searched for
        """
        return [
            cons for cons in self.constraints if cons.index.disposition == disposition
        ]

    def at_cmp(
        self, component: Emission | Resource | Land | Cash | Process | Storage | Transit
    ):
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

        self.blocks: list[Block] = []

    def __setattr__(self, name: str, block: Block):

        if isinstance(block, Block):
            self.parameters.extend(block.parameters)
            self.variables.extend(block.variables)
            self.constraints.extend(block.constraints)
            self.blocks.append(block)

        super().__setattr__(name, block)

    def eqns(
        self,
        at_cmp: Emission | Resource | Land | Cash | Process | Storage | Transit = None,
        at_disp: tuple[
            Emission | Resource | Land | Cash | Process | Storage | Transit
        ] = None,
    ):
        """Yields all equations in the Program

        Args:
            at_cmp (IsCmp, optional): Component to search for. Defaults to None.
            at_disp (tuple[Emission| Resource | Land | Cash | Process | Storage | Transit], optional): Idx (actually Idx) to search for. Defaults to None.
        """
        for block in self.blocks:
            for eqn in block.eqns(at_cmp=at_cmp, at_disp=at_disp):
                yield eqn
