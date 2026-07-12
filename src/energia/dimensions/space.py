"""Space"""

from dataclasses import dataclass

from .._core._dimension import _Dimension
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location


@dataclass
class Space(_Dimension):
    """
    Spatial representation of the system.

    All spatial components are attached to this object.


    :param model: Model to which the representation belongs.
    :type model: Model

    :ivar name: Name of the dimension, auto generated
    :vartype name: str
    :ivar locations: List of locations in the space.
    :vartype locations: list[Loc]
    :ivar sources: List of source locations.
    :vartype sources: list[Loc]
    :ivar sinks: List of sink locations.
    :vartype sinks: list[Loc]
    :ivar linkages: List of linkages in the space.
    :vartype linkages: list[Link]
    :ivar label: Label for the space.
    :vartype label: str
    :ivar default: Default location for the space. Defaults to None.
    :vartype default: Loc
    :ivar network: The encompassing region (network) of the space.
    :vartype network: Loc
    :ivar s: List of spatial components (locations and linkages).
    :vartype s: list[Loc | Link]
    :ivar tree: Nested dictionary of locations.
    :vartype tree: dict
    :ivar hierarchy: position on tree.
    :vartype hierarchy: dict[int, list[Loc]]


    .. note::
        - name is self generated
        - locations, sources, sinks, and linkages are populated as model is defined
        - label is fixed
        - default is set to None initially and is updated when needed (see network property)
    """

    def __post_init__(self):
        self.locations: list[Location] = []
        self.sources: list[Location] = []
        self.sinks: list[Location] = []
        self.linkages: list[Linkage] = []

        _Dimension.__post_init__(self)

    # -----------------------------------------------------
    #                    Helpers
    # -----------------------------------------------------

    @property
    def tree(self) -> dict:
        """creates a nested dictionary of locations"""
        tree_ = {self.network: {}}

        for loc in self.network.has:
            tree_[self.network][loc] = loc.tree

        return tree_

    @property
    def hierarchy(self) -> dict[int, list[Location]]:
        """gives position in tree"""
        self.network.update_hierarchy()
        hierarchy_ = {}
        for spc in self.s:
            if spc.hierarchy not in hierarchy_:
                hierarchy_[spc.hierarchy] = []
            hierarchy_[spc.hierarchy].append(spc)
        return hierarchy_

    @property
    def not_nested(self) -> list[Location]:
        """List of locations that are not nested under another location"""
        return [loc for loc in self.locations if not loc.isin]

    # -----------------------------------------------------
    #                    Superlative
    # -----------------------------------------------------

    def _ntw_from_not_nested(self) -> Location:
        """
        Make a location to be held as network
        Using all existing non-nested locations
        """
        # property, make it do the work only once
        not_nested = self.not_nested
        if len(not_nested) == 1:
            # only one implies that all locations are nested under the one location
            return not_nested[0]

        # sum up all not nested locations to make a network
        ntw = sum(not_nested)
        setattr(self.model, "ntw", ntw)
        return ntw

    @property
    def network(self) -> Location:
        """An encompassing location"""

        # if no location is available, create a default one
        if not self.locations:
            return self.model._l0()

        # if only one location is available, return it
        if len(self.locations) == 1:
            return self.locations[0]

        return self._ntw_from_not_nested()

    @property
    def s(self) -> list[Location | Linkage]:
        """List of spatial components"""
        return self.locations + self.linkages

    def _lower(
        self, loc: Location, hierarchy: dict[int, list[Location]]
    ) -> list[Location]:
        """Return all locations at lower hierarchy than loc"""
        if loc.hierarchy + 1 in hierarchy:
            return [lc for lc in hierarchy[loc.hierarchy + 1] if lc in loc.has]
        return []

    def _upper(
        self, loc: Location, hierarchy: dict[int, list[Location]]
    ) -> Location | None:
        """Return Location at higher hierarchy than loc"""
        try:
            return [lc for lc in hierarchy[loc.hierarchy - 1] if loc in lc.has][0]
        except IndexError:
            return None

    def split(self, loc: Location) -> tuple[list[Location], Location | None]:
        """Gives a list of locations at a higher and lower hierarchy than loc"""
        # hierarchy is a property
        # we want it at this stage
        hierarchy = self.hierarchy
        return self._lower(loc, hierarchy), self._upper(loc, hierarchy)
