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

    attr: str = field(default=None)
    balance: IsBlc = field(default=None)
    opn: IsOpn = field(default=None)
    parent: BoundBound = field(default=None)
    prmsym: str = field(default=None)

    def __post_init__(self):
        _Constraint.__post_init__(self)
        self.root = Resource
        self.name = f'Balance|{self.attr}|'
