"""Operational Mode attached to a Parameter"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Self

from gana import I

from ..._core._x import _X

if TYPE_CHECKING:
    from gana.sets.constraint import C

    from ...modeling.variables.sample import Sample


@dataclass
class Modes(_X):
    """
    Represents a discrete choice to be taken within a spatiotemporal disposition.
    Modes can split usage. A Mode of Operation can be used for Conversion, Use, etc.

    :param n_modes: Number of modes. Defaults to 1.
    :type n_modes: int
    :param bind: The aspect and component which is being 'moded'. Defaults to None.
    :type bind: Bind | None
    :param parent: Parent mode, if any. Defaults to None.
    :type parent: Self | None
    :param pos: Position in the parent mode set. Defaults to None.
    :type pos: int | None

    :ivar name: The name of the mode, usually a number.
    :vartype name: str | float | int
    """

    n_modes: int = 1
    bind: Sample = None
    parent: Self = None
    pos: int = None

    def __post_init__(self):
        _X.__post_init__(self)

        if self.pos is not None:
            self.name = f"{self.parent}[{self.pos}]"

        if self.parent:
            self.model = self.parent.model

        # have child modes been made
        self._birthed = False
        # where child modes are stored
        self._ = []

    @property
    def cons(self) -> list[C]:
        """Constraints"""
        # overwrite X.cons property
        # this gets the actual constraint objects from the program
        # based on the pname (attribute name) in the program
        if self.parent:
            return [getattr(self.program, c) for c in self.constraints]
        return [getattr(self.program, c) for c in self.constraints] + sum(
            [m.cons for m in self],
            [],
        )

    @cached_property
    def I(self) -> I:
        """Index set of modes"""

        if self.parent:
            _ = self.parent.I  # makes sure the parent is indexed
            # do not set a new index set, get from parent
            return getattr(self.parent.program, self.parent.name)[self.pos]

        _index = I(size=self.n_modes, tag=f"Modes of {self.bind.aspect}")

        setattr(
            self.program,
            self.name,
            _index,
        )

        return _index

    def __eq__(self, other: Modes) -> bool:
        """Equality operator"""
        if other.name == self.name:
            return True
        return False

    def __len__(self) -> int:
        """Length of the modes"""
        return self.n_modes

    def __getitem__(self, key: int) -> _X:
        """Get a mode by index"""
        if not self._birthed:
            self._ = [
                Modes(bind=self.bind, parent=self, pos=i) for i in range(self.n_modes)
            ]
            self._birthed = True

        return self._[key]

    def __iter__(self):
        """Iterate over modes"""
        for i in range(self.n_modes):
            yield self[i]
