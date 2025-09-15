"""Linkage links Locations through Transits"""

from __future__ import annotations

from dataclasses import dataclass
from operator import is_
from typing import TYPE_CHECKING, Self

from ...core.x import X
from ..measure.unit import Unit

if TYPE_CHECKING:
    from ...dimensions.loc import Space
    from .location import Location


@dataclass
class Linkage(X):
    """Linkage between two Locations

    Args:
        name (str): Name of the Linkage. Defaults to None.
        label (str): Label of the Linkage. Defaults to None.
        source (Loc): Source Location.
        sink (Loc): Sink Location.
        dist (float | Unit): Distance between the two Locations.
        bi (bool): Is the Linkage bidirectional? Defaults to False.
        auto (bool): Is the Linkage automatically generated? Defaults to False.

    Attributes:
        model (Model): Model to which the Linkage belongs.
        space (Space): Space to which the Linkage belongs.
        network (Loc): Network to which the Linkage belongs.
    """

    source: Location = None
    sink: Location = None
    dist: float | Unit = None
    bi: bool = False
    auto: bool = False

    def __post_init__(self):

        if is_(self.source, self.sink):
            # if the source and sink are the same, throw error
            raise ValueError(f"source and sink can't both be {self.source}")

        X.__post_init__(self)
        self.sib: Self = None

        self.hierarchy = 1

    @property
    def space(self) -> Space:
        """Space to which the Location belongs"""
        return self.model.space

    @property
    def network(self) -> Location:
        """Network to which the Location belongs"""
        return self.model.network

    @property
    def isnetwork(self) -> bool:
        """Is this the network of the model?
        Linkage can never be the network
        """
        return False

    def rev(self):
        """Reversed Link"""
        # locations are all uni directional
        # if bi is True, create another link for the other direction
        # and set self.bi to False
        if self.bi:
            self.bi = False
            return -self

    def __neg__(self):
        # creates a new Link in the opposite direction
        if self.label:
            label = self.label + '(-)'
            self.label = self.label + '(+)'
        else:
            label = None

        _link = Linkage(
            source=self.sink,
            sink=self.source,
            dist=self.dist,
            label=label,
        )
        if self.auto:
            _link.name = f'{self.sink.name}-{self.source.name}'
        else:
            _link.name = '-' + self.name
        _link.sib, self.sib = self, _link
        return _link

    def __eq__(self, other: int | float | Self) -> Self | bool:
        """Sets the distance of a linkage"""
        # sets the distance of a linkage
        # each linkage has a unique distance
        if isinstance(other, (int, float)):

            self.dist = other

            self.model = self.source.model

            if not self.name:
                self.name = rf'{self.source.name}_{self.sink.name}'

            setattr(self.model, self.name, self)

            return self

        if is_(self, other):
            return True
        return False
