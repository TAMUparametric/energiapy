"""Operational Mode attached to a Parameter"""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Self

from gana import I

from ..._core._x import _X

if TYPE_CHECKING:
    from gana.sets.constraint import C

    from ...modeling.indices.sample import Sample


class Modes(_X):
    """
    Represents a discrete choice to be taken within a spatiotemporal disposition.
    Modes can split usage. A Mode of Operation can be used for Conversion, Use, etc.

    :param n_modes: Number of modes. Defaults to 1.
    :type n_modes: int
    :param sample: The aspect and component (sample) which is being 'moded'. Defaults to None.
    :type sample: Sample | None
    :param parent: Parent mode, if any. Defaults to None.
    :type parent: Self | None
    :param n: Position in the parent mode set. Defaults to None.
    :type n: int | None

    :ivar model: The model to which the component belongs.
    :vartype model: Model
    :ivar name: Set when the component is assigned as a Model attribute.
    :vartype name: str
    :ivar constraints: List of constraints associated with the component.
    :vartype constraints: list[str]
    :ivar domains: List of domains associated with the component.
    :vartype domains: list[Domain]
    :ivar aspects: Aspects associated with the component with domains.
    :vartype aspects: dict[Aspect, list[Domain]]
    """

    def __init__(
        self,
        size: int = 1,
        sample: Sample | None = None,
        parent: Self | None = None,
        n: int | None = None,
    ):
        self.size = size
        self.sample = sample
        self.parent = parent
        self.n = n

        _X.__init__(self)

        if self.parent:
            self.name = f"{self.parent}[{self.n}]"
            self.model = self.parent.model

    @cached_property
    def _(self) -> list[Self]:
        """Child modes"""
        return [Modes(sample=self.sample, parent=self, n=i) for i in range(self.size)]

    @cached_property
    def I(self) -> I:
        """Index set of modes"""

        if self.parent:
            _ = self.parent.I  # makes sure the parent is indexed
            # do not set a new index set, get from parent
            return getattr(self.parent.program, self.parent.name)[self.n]

        _index = I(size=self.size, tag=f"Modes of {self.sample.aspect}")

        setattr(
            self.program,
            self.name,
            _index,
        )

        return _index

    @property
    def cons(self) -> list[C]:
        """Constraints"""
        # overwrite X.cons property
        # this gets the actual constraint objects from the program
        # based on the pname (attribute name) in the program
        if self.parent:
            return [getattr(self.program, c) for c in self.constraints]
        return list(
            set(
                [getattr(self.program, c) for c in self.constraints]
                + sum(
                    [m.cons for m in self],
                    [],
                )
            )
        )

    def __eq__(self, other: Modes) -> bool:
        if isinstance(other, Modes):
            if other.name == self.name:
                return True
        return False

    def __len__(self) -> int:
        return self.size

    def __getitem__(self, key: int) -> _X:
        return self._[key]

    def __iter__(self):
        for i in range(self.size):
            yield self[i]
