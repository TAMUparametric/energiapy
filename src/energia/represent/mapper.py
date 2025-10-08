"""Blocks of the Model"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..components.commodity.resource import Resource
    from ..components.impact.categories import Economic, Environ, Social
    from ..components.operation.process import Process
    from ..components.operation.storage import Storage
    from ..components.operation.transport import Transport
    from ..components.spatial.linkage import Linkage
    from ..components.spatial.location import Location
    from ..components.temporal.modes import Modes
    from ..components.temporal.periods import Periods
    from ..modeling.indices.domain import Domain
    from ..modeling.variables.aspect import Aspect
    from ..modeling.variables.control import Control
    from ..modeling.variables.states import Impact, State, Stream


@dataclass
class Mapper:
    """Defines the representation of the model

    :param update_map: Mapping used for updating internal structures (if applicable).
    :type update_map: dict
    :param time: Time representation of the Model (set during post-initialization).
    :type time: Time
    :param space: Spatial representation of the Model (set during post-initialization).
    :type space: Space
    """

    # meshes of space and time to denote whether a constraint is written
    # general resource balance

    def __post_init__(self):

        # Dictionary which tells you what aspects of resource
        # have grb {loc: time: []} and {time: loc: []}
        self.grb: dict[
            Resource,
            dict[Location | Linkage, dict[Periods, list[Aspect]]],
        ] = {}

        # Dictionary which tells you what aspects of what component
        # have been bound at what location and time
        self.dispositions: dict[
            Aspect,
            dict[
                Resource | Process | Storage | Transport,
                dict[Location | Linkage, dict[Periods, list[Aspect]]],
            ],
        ] = {}

        self.maps: dict[Aspect, dict[Domain, dict[str, list[Domain]]]] = {}
        self.maps_report: dict[Aspect, dict[Domain, dict[str, list[Domain]]]] = {}

    def update_dispositions(
        self,
        aspect: Aspect,
        domain: Domain,
    ):
        """Updates the spatiotemporal dispositions for an aspect pertaining to a component"""

        def merge_trees(d1, d2):
            """Recursively merge two tree-like dicts (values always dicts)."""
            result = dict(d1)  # shallow copy of d1
            for k, v in d2.items():
                if k in result:
                    result[k] = merge_trees(
                        result[k],
                        v,
                    )  # recurse since v must also be a dict
                else:
                    result[k] = v
            return result

        self.dispositions = merge_trees(self.dispositions, {aspect: domain.tree})

    def update_grb(self, resource: Resource, space: Location | Linkage, time: Periods):
        """Creates a mesh for grb dict"""

        if resource not in self.grb:
            # update resource if needed
            self.grb[resource] = {}

        if space not in self.grb[resource]:
            # update space if needed
            self.grb[resource][space] = {}

        if time not in self.grb[resource][space]:
            self.grb[resource][space][time] = []
