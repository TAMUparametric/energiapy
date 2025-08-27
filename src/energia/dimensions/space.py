"""Space"""

from dataclasses import dataclass

from ..components.spatial.linkage import Link
from ..components.spatial.location import Loc
from ..core.dimension import Dimension


@dataclass
class Space(Dimension):
    """Spatial representation of the system

    All spatial components are attached to this object

    Attributes:
        model (Model): Model to which the representation belongs.
        name (str): Name of the model. Defaults to None.
        locs (list[Loc]): List of locations in the space.
        sources (list[Loc]): List of source locations.
        sinks (list[Loc]): List of sink locations.
        links (list[Link]): List of links in the space.
        label (str): Label for the space.
        default (Loc): Default location for the space. Defaults to None.

    Note:
        - name is self generated
        - locs, sources, sinks, and links are populated as model is defined
        - label is fixed
        - default is set to None initially and is updated when needed (see network property)
    """

    def __post_init__(self):
        self.locs: list[Loc] = []
        self.sources: list[Loc] = []
        self.sinks: list[Loc] = []
        self.links: list[Link] = []

        Dimension.__post_init__(self)

    # -----------------------------------------------------
    #                    Helpers
    # -----------------------------------------------------

    @property
    def tree(self):
        """creates a nested dictionary of locations"""
        tree_ = {self.network: {}}

        for loc in self.network.has:
            tree_[self.network][loc] = loc.tree

        return tree_

    @property
    def hierarchy(self) -> dict[int, list[Loc]]:
        """creates a nested dictionary of locations"""
        self.network.update_hierarchy()
        hierarchy_ = {}
        for loc in self.locs:
            if not loc.hierarchy in hierarchy_:
                hierarchy_[loc.hierarchy] = []
            hierarchy_[loc.hierarchy].append(loc)
        return hierarchy_

    def split(self, loc: Loc) -> tuple[list[Loc], list[Loc]]:
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

    # -----------------------------------------------------
    #                    Superlative
    # -----------------------------------------------------

    @property
    def network(self) -> Loc:
        """An encompassing region"""

        # if no location is available, create a default one
        if not self.locs:
            return self.model.default_loc()

        # if only one location is available, return it
        if len(self.locs) == 1:
            return self.locs[0]

        # check for locations that are not nested
        loc_not_nested = [loc for loc in self.locs if not loc.isin]

        # only one implies that all locations are nested under the one location
        # which is the network
        if len(loc_not_nested) == 1:
            return loc_not_nested[0]

        # if multiple "not nested" locations exist, make a network with them
        if loc_not_nested:
            # l is used as the name for the default network
            self.model.ntw = sum(loc_not_nested)
            return self.model.ntw

    @property
    def s(self) -> list[Loc | Link]:
        """List of spatial components"""
        return self.locs + self.links
