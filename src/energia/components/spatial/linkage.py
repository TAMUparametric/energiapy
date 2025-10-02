"""Linkage links Locations through Transits"""

from __future__ import annotations

from dataclasses import dataclass
from operator import is_
from typing import TYPE_CHECKING, Self

from ..._core._x import _X

if TYPE_CHECKING:
    from ...dimensions.space import Space
    from ..measure.unit import Unit
    from .location import Location


@dataclass
class Linkage(_X):
    """
    Linkage between two Locations.

    :param name: Name of the Linkage. Defaults to None.
    :type name: str, optional
    :param label: Label of the Linkage. Defaults to None.
    :type label: str, optional
    :param source: Source Location.
    :type source: Loc
    :param sink: Sink Location.
    :type sink: Loc
    :param dist: Distance between the two Locations.
    :type dist: float | Unit
    :param bi: Is the Linkage bidirectional? Defaults to False.
    :type bi: bool, optional
    :param auto: Is the Linkage automatically generated? Defaults to False.
    :type auto: bool, optional

    :ivar model: Model to which the Linkage belongs.
    :vartype model: Model
    :ivar space: Space to which the Linkage belongs.
    :vartype space: Space
    :ivar network: Network to which the Linkage belongs.
    :vartype network: Loc
    """

    source: Location = None
    sink: Location = None
    dist: float | Unit = None
    basis: Unit = None
    bi: bool = False
    auto: bool = False

    def __post_init__(self):

        if is_(self.source, self.sink):
            # if the source and sink are the same, throw error
            raise ValueError(f"source and sink can't both be {self.source}")

        _X.__post_init__(self)
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
        if self.sib is not None:
            return self.sib

        if self.label:
            label = self.label + "(-)"
            self.label = self.label + "(+)"
        else:
            label = None

        _link = Linkage(
            source=self.sink,
            sink=self.source,
            dist=self.dist,
            label=label,
        )
        if self.auto:
            _link.name = f"{self.sink.name}-{self.source.name}"
        else:
            _link.name = "-" + self.name
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
                self.name = rf"{self.source.name}_{self.sink.name}"

            setattr(self.model, self.name, self)

            return self

        if is_(self, other):
            return True
        return False
