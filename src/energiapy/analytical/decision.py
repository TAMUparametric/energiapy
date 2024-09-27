"""A Decision is a choice made by a Player
"""

from typing import Self

from .impact import Impact
from ..core.energia import Energia


class Decision(Energia):
    """A Player's Decision or Action that causes an Impact"""

    def __init__(self, *impacts: tuple[Impact], name: str = None):
        super().__init__(name)
        self.impacts: tuple[Impact] = impacts

        self.pos: bool | Self = False
        self.neg: bool | Self = False

        for impact in self.impacts:
            setattr(self, impact.name, [impact.pos, impact.neg])
            print(self.pos)
            print(self.neg)
            if self.pos and self.neg:
                impact.decisions.append(self)

    def __pos__(self):
        d = Decision(*self.impacts, name=f'{self.name}[+]')
        d.pos = True
        self.pos = d
        return d

    def __neg__(self):
        d = Decision(*self.impacts, name=f'{self.name}[-]')
        d.neg = True
        self.neg = d
        return d
