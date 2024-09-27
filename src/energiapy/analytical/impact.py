"""The Impact caused by a Player's Decision"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from ..core.energia import Energia

if TYPE_CHECKING:
    from .decision import Decision


class Impact(Energia):
    """An Impact caused by a Player's Decision"""

    def __init__(self, name: str):
        super().__init__(name)

        self.decisions: list[Self] = []
        self.pos: bool | Self = False
        self.neg: bool | Self = False

    def __pos__(self) -> Self:
        i = Impact(f'{self.name}[+]')
        i.pos = True
        self.pos = i
        return i

    def __neg__(self) -> Self:
        i = Impact(f'{self.name}[-]')
        i.neg = True
        self.neg = i
        return i
