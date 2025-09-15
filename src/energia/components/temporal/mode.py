"""Operational Mode attached to a Parameter"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gana.sets.index import I
    from ...modeling.indices.domain import Domain
    from ...modeling.variables.aspect import Aspect


@dataclass
class Mode:
    """Represents a discrete choice to be taken within a
    spatiotemporal disposition.
    Modes can split you
    Mode of Operation, can be used for Conversion, Use, etc.

    Attributes:
        name (str, float, int]): The name of the mode, usually a number.
    """

    name: int | str
    of: int | str

    def __post_init__(self):

        self.name = str(self.name)
        self.parent_set: I = None
        self.pos: int = None

        self.domains: list[Domain] = []
        self.constraints: list[str] = []
        self.aspects: list[Aspect] = {}

    @property
    def I(self) -> I:
        """Index set"""
        return self.parent_set[self.pos]

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
