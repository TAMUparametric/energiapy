"""Keeps a track of what elements are defined at what dispostions  
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..core._handy._dunders import _Dunders
from ..core.nirop.errors import CacodcarError

if TYPE_CHECKING:
    from ..core.aliases.isblk import IsIndex, IsRuleBook
    from ..core.aliases.iselm import IsElement


@dataclass
class ChitraGupta(_Dunders):
    """Keeps a track of what elements are defined at what indices

    Attributes:
        name (str): name, takes from the name of the Scenario
        rulebook: IsRuleBook = field(default_factory=rulebook)

    """

    name: str = field(default=None)
    rulebook: IsRuleBook = field(default=None)

    def __post_init__(self):

        self.name = f'ChitraGupta|{self.name}|'

        for var in self.rulebook.vars():
            setattr(self, var.cname(), [])

        for param in self.rulebook.params():
            setattr(self, param.cname(), [])

    def add(self, elm: IsElement, disp: IsIndex):
        """Add a disposition to a Variable or Parameter

        Args:
            elm (str): Element to add to the ChitraGupta
            disp (IsIndex): Rule to add to the ChitraGupta
        """

        # Only unique instances of indices are allowed
        if disp in getattr(self, elm.cname()):
            raise CacodcarError(f'{elm} already has {disp} in {self.name}')

        getattr(self, elm.cname()).append(disp)
