"""Balances Resource flow in Operations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from ._constraint import _Constraint

from ...core.isalias.inps.isblc import IsBlc
from ...core.isalias.cmps.isdfn import IsOpn
from ...components.commodity.resource import Resource

if TYPE_CHECKING:
    from .boundbound import BoundBound


@dataclass
class Balance(_Constraint):
    """Balances the flow of Resource in Operations"""

    balance: IsBlc = field(default=None)
    opn: IsOpn = field(default=None)
    parent: BoundBound = field(default=None)
    sym: str = field(default=None)

    def __post_init__(self):
        self.root = Resource

    @staticmethod
    def var():
        """Variable"""

    @staticmethod
    def prm():
        """Parameter"""

    @staticmethod
    def rule():
        """Constraint Rule"""

    @property
    def varbirth_attrs(self):
        """Attributes of the Variable"""

    @property
    def varsym(self):
        """Symbol of the Variable"""

    @property
    def prmsym(self):
        """Symbol of the Parameter"""
        return self.sym
