"""A Decision is a choice made by a Player
"""

from typing import Self

from ..information.dimension import Component


class Decision(Component):
    """A Player's Decision or Action that causes an Impact"""

    def __init__(self, *causes: tuple[Self], name: str = None):
        super().__init__(name)
        self.causes: tuple[Self] = list(causes)
        self.impacts: list[Self] = []
        self.pos: bool | Self = False
        self.neg: bool | Self = False

        for i in self.causes:
            i.impacts.append(self)

    def __pos__(self):
        d = Decision(name=f'{self.name}[+]')
        d.causes = self.causes
        d.pos = True
        self.pos = d
        return d

    def __neg__(self):
        d = Decision(name=f'{self.name}[-]')
        d.causes = self.causes
        d.neg = True
        self.neg = d
        return d
