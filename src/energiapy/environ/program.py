"""Mathematical Programming Model
"""

from dataclasses import dataclass, field

from ..core._handy._dunders import _Dunders
from ..core._handy._printers import _Print

from .blocks.progblock import ProgramBlock


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
