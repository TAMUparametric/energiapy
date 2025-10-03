"""Location where Operations can reside"""

from __future__ import annotations

from functools import cached_property
from operator import is_
from typing import TYPE_CHECKING, Self
from warnings import warn

from gana import I as Idx

from ..._core._x import _X
from ...utils.dictionary import get_depth
from .linkage import Linkage

if TYPE_CHECKING:
    from ...dimensions.space import Space
    from ..commodity.currency import Currency
    from ..operation.process import Process
    from ..operation.storage import Storage


class Location(_X):
    """A discretization of Space
    A location can be inclusive of other locations


    :param has: Locations contained in this Location.
    :type has: tuple[IsLocation]
    :param label: Label of the Location. Defaults to None.
    :type label: str, optional

    :ivar model: Model to which the Location belongs.
    :vartype model: Model
    :ivar name: Name of the Location. Set when the Location is assigned as a Model attribute.
    :vartype name: str

    :ivar constraints: List of constraints associated with the Location.
    :vartype constraints: list[str]
    :ivar domains: List of domains associated with the Location.
    :vartype domains: list[Domain]
    :ivar aspects: Aspects associated with the Location with domains.
    :vartype aspects: dict[Aspect, list[Domain]]
    :ivar isin: Location in which this Location is contained. Defaults to None.
    :vartype isin: IsLocation, optional
    :ivar currency: Currency used in the Location. Defaults to None.
    :vartype currency: Currency, optional
    :ivar alsohas: Locations contained in this Location, but not directly. Defaults to ()
    :vartype alsohas: tuple[IsLocation]
    :ivar hierarchy: Level of hierarchy of the Location. Defaults to None.
    :vartype hierarchy: int, optional
    """

    def __init__(self, *has: tuple[Self], label=None):

        # it is an indexed component
        _X.__init__(self, label=label)

        # the other locations contained in this location
        self.has: tuple[Self] = has
        # if the location is a part of another
        self.isin = None
        # the currency used in the location
        self.currency: Currency = None
        # goes down another level of hierarchy
        # to find locations within the locations contained in this location
        self.alsohas: tuple[Self] = ()

        """Hierarchy in the space tree"""
        self.hierarchy: int = None

        for loc in self.has:
            if loc.name:
                # if the location has been set on the program
                # set the location as a part of this location
                loc.isin = self
                # set the location on to itself
                setattr(self, loc.name, loc)
                for locin in loc.has:
                    # if not already notified
                    # update alsohas
                    if locin not in self.has:
                        self.alsohas += (locin,)

    def __setattr__(self, name, value):

        if name == "currency" and value:
            # all locations within a location have the same currency
            for loc in self.has + self.alsohas:
                loc.currency = value

        super().__setattr__(name, value)

    def locate(self, *operations: Process | Storage):
        """Locates the Operations"""
        # locates an operation
        # which leads to the conversion balances being written
        for opr in operations:
            opr.locate(self)

    @property
    def tree(self) -> dict[Self, dict]:
        """Prints the tree of Locations"""
        # a tree visualizing the hierarchy of locations
        if self.has:
            return {loc: loc.tree for loc in self.has}
        # lowest level of the hierarchy locations
        # return an empty dictionary (set)
        return {}

    @property
    def depth(self):
        """Finds the depth of the Location"""
        # gets the level of hierarchy of the Location
        return get_depth(self.tree)

    def update_hierarchy(self, hierarchy: int = 0):
        """Updates the hierarchy of the locations"""

        self.hierarchy = hierarchy
        for loc in self.has:
            loc.update_hierarchy(hierarchy + 1)

    @property
    def space(self) -> Space:
        """Space to which the Location belongs"""
        return self.model.space

    @property
    def network(self) -> Self:
        """Network to which the Location belongs"""
        return self.model.network

    @property
    def isnetwork(self) -> bool:
        """Is this the network of the model?"""
        return self == self.model.network

    @cached_property
    def I(self) -> Idx:
        """gana index set"""
        if self.has:
            # if component has a nested locations
            _index = Idx(*[loc.name for loc in self.has], tag=self.label or "")

        else:
            # if component has no nested locations
            _index = Idx(self.name, tag=self.label or "")
        setattr(self.program, self.name, _index)
        return _index

    def sink(self):
        """Tells whether the location is a sink"""
        if self in self.space.sinks:
            return True
        return False

    def source(self):
        """Tells whether the location is a source"""
        if self in self.space.sources:
            return True
        return False

    def links(self, location, print_link: bool = True) -> list[Linkage]:
        """Finds the links between two Locations

        Args:
            location (IsLocation): Location to find links with
            print_link (bool, optional): Whether the links are to be printed. Defaults to True.

        Returns:
            list: Provides the links between the locations
        """
        # this prints out all the links between the two locations
        links = []
        for link in self.space.linkages:
            source, sink = False, False

            if is_(self, link.source) and is_(location, link.sink):
                source, sink = self, location

            if is_(self, link.sink) and is_(location, link.source):
                source, sink = location, self

            if source and sink:
                links.append(link)
                if print_link:
                    print(f"{source} is source and {sink} is sink in {link}")
                continue
        return links

    def connected(self, location, print_link: bool = False) -> bool:
        """Finds whether the Locations are connected
        Args:
            location (IsLocation): Location to verify Links with
            print_link (bool, optional): Whether to print the Links. Defaults to False.

        Returns:
            bool: True if Locations are connection
        """
        # this lets you know whether the two locations are connected
        if self.links(location, print_link=print_link):
            return True
        return False

    def all(self):
        """gives locations within"""
        # yeilds all locations within the location and all locations within those locations
        if self.has:
            for loc in self.has:
                yield loc
                yield from loc.all()

    def __add__(self, location: Self):
        """Creates another location which consists of self and other"""
        if not self.name:
            # this handles when adding multiple locations
            return Location(*self.has, location)
        return Location(location, self)

    def __radd__(self, number: int):
        """For allowing sum([Loc])"""
        if isinstance(number, int) and number == 0:
            return self

    def __sub__(self, location: Self):
        """Creates a linkage"""
        # subtracting a location creates a link
        # alternatively Model.Link can be used
        # for multiple links across the same two locations
        # declare Link() objects
        links = self.links(location, print_link=False)
        links = [link for link in links if link.source == self]
        if len(links) > 1:
            warn(
                f"Multiple links found between ({self}, {location})\n"
                "Suggest using model.named_link = Link(...)\n"
                f"Currently, taking {links[0]}, with distance {links[0].dist}",
                UserWarning,
            )
        if links:
            return links[0]

    def __eq__(self, other: Self):
        # the objects need to be the same
        return is_(self, other)

    def __lt__(self, other: Self):
        # if a location is nested within another
        return self in other.has or self in other.alsohas

    def __leq__(self, other: Self):
        # same as less than & equality
        return self < other or self == other

    def __gt__(self, other: Self):
        # reverse check
        return other < self

    def __geq__(self, other: Self):
        # reverse check
        return other <= self

    def __iter__(self):
        yield self.has

    def __contains__(self, item: Self):
        if item in self.has:
            return True
