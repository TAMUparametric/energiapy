"""Keeps a track of what elements are defined at what dispostions  
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from ..core.aliases.is_block import IsDisposition, IsRuleBook
    from ..core.aliases.is_element import IsElement


@dataclass
class ChitraGupta(_Dunders):
    """Keeps a track of what elements are defined at what dispositions

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

    def add(self, elm: IsElement, disp: IsDisposition):
        """Add a disposition to a Variable or Parameter

        Args:
            elm (str): Element to add to the ChitraGupta
            disp (IsDisposition): Rule to add to the ChitraGupta
        """

        getattr(self, elm.cname()).append(disp)
