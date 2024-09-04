"""Balances Resource flow in Operations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from ._task import _Task

from ...core.isalias.inps.isblc import IsBlc
from ...core.isalias.cmps.isdfn import IsOpn
from ...components.commodity.resource import Resource

if TYPE_CHECKING:
    from .bound import BoundBound


@dataclass
class Balancing(_Task):
    """Balances the flow of Resource in Operations"""

    balance: IsBlc = field(default=None)
    opn: IsOpn = field(default=None)
    parent: BoundBound = field(default=None)

    def __post_init__(self):
        _Task.__post_init__(self)
        self.root = Resource
        self.name = f'Balancing|{self.name}|'
