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

    # -----------------------------------------------------
    #                    Superlative
    # -----------------------------------------------------

    @property
    def network(self) -> Location:
        """An encompassing location"""

        # if no location is available, create a default one
        if not self.locations:
            return self.model.default_loc()

        # if only one location is available, return it
        if len(self.locations) == 1:
            return self.locations[0]

        # check for locations that are not nested
        loc_not_nested = [loc for loc in self.locations if not loc.isin]

        # only one implies that all locations are nested under the one location
        # which is the network
        if len(loc_not_nested) == 1:
            return loc_not_nested[0]

        # if multiple "not nested" locations exist, make a network with them
        if loc_not_nested:
            # l is used as the name for the default network
            self.model.ntw = sum(loc_not_nested)
            return self.model.ntw

        raise ValueError("No network location could be determined")

    @property
    def s(self) -> list[Location | Linkage]:
        """List of spatial components"""
        return self.locations + self.linkages

    def split(self, loc: Location) -> tuple[list[Location], list[Location]]:
        """Gives a list of locations at a higher and lower hierarchy than loc"""
        hierarchy = self.hierarchy

        loc_pos = loc.hierarchy

        if loc_pos + 1 in hierarchy:
            lower = [l for l in hierarchy[loc_pos + 1] if l in loc.has]
        else:
            lower = []

        if loc_pos - 1 in hierarchy:
            upper = [l for l in hierarchy[loc_pos - 1] if loc in l.has]

            upper = upper[0] if upper else None
        else:
            upper = None

        return lower, upper
