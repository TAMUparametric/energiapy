"""Operational Mode attached to a Parameter"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from gana.sets.index import I

from ...core.x import X

if TYPE_CHECKING:
    from gana.block.program import Prg

    from ...modeling.constraints.bind import Bind
    from ...modeling.indices.domain import Domain
    from ...modeling.variables.aspect import Aspect
    from ...represent.model import Model


@dataclass
class Modes(X):
    """Represents a discrete choice to be taken within a
    spatiotemporal disposition.
    Modes can split you
    Mode of Operation, can be used for Conversion, Use, etc.

    Attributes:
        name (str, float, int]): The name of the mode, usually a number.
    """

    n_modes: int = 1
    bind: Bind = None
    parent: Self = None
    pos: int = None

    def __post_init__(self):
        X.__post_init__(self)

        if self.pos is not None:
            self.name = f'{self.parent}[{self.pos}]'

    @property
    def I(self) -> I:
        """Index set of modes"""

        if self.parent:
            _ = self.parent.I  # makes sure the parent is indexed
            # do not set a new index set, get from parent
            return getattr(self.parent.program, self.parent.name)[self.pos]

        if not self._indexed:
            # and index element is created for each component
            # with the same name as the component
            # A SELF type set is created
            setattr(
                self.program,
                self.name,
                I(size=self.n_modes, tag=f'Modes of {self.bind.aspect}'),
            )
            self._indexed = True
        # if already indexed, return the index set from the program
        return getattr(self.program, self.name)

    def __eq__(self, other: Modes) -> bool:
        """Equality operator"""
        if other.name == self.name:
            return True
        return False

    def __len__(self) -> int:
        """Length of the modes"""
        return self.n_modes

    def __getitem__(self, key: int) -> X:
        """Get a mode by index"""
        # TODO: allow slicing

        return Modes(bind=self.bind, parent=self, pos=key)

    def __iter__(self):
        """Iterate over modes"""
        for i in range(self.n_modes):
            yield self[i]
