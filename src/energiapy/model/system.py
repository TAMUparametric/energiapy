from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from warnings import warn

from .._core._handy._dunders import _Dunders
from ..components._component import (_Component, _Scope,  # , _Analytical
                                     _Spatial, _Temporal)
from ..components.scope.horizon import Horizon
from ..components.scope.network import Network
from ..components.spatial.linkage import Linkage

if TYPE_CHECKING:
    from .._core._aliases._is_component import IsComponent


@dataclass
class System(_Dunders):
    """Collects System Components"""

    name: str = field(default=None)

    def __post_init__(self):

        self.name = f'System|{self.name}|'

        # SpatioTemporal Scope
        # Is always [Horizon, Network]
        self.scopes = [None, None]

        # Analytical
        self.players = []

        # Temporal
        self.scales = []

        # Commodity
        self.resources, self.materials, self.emissions, self.assets = (
            [] for _ in range(4)
        )
        # Operational
        self.processes, self.storages, self.transits = ([] for _ in range(3))

        # Spatial
        self.locations, self.linkages = ([] for _ in range(2))

    def __setattr__(self, name, value):

        # all Component to collection
        if issubclass(type(value), _Component):
            self.add(value)

        # keeping scopes as a list and horizon and network avoids recursion
        if issubclass(type(value), _Temporal):
            # set Scales to horizon
            setattr(self.scopes[0], name, value)

        if issubclass(type(value), _Spatial):
            # set Location and Linkages in Network
            setattr(self.scopes[1], name, value)

        super().__setattr__(name, value)

    def add(self, component: IsComponent):
        """Updates the collection lists of components in the system.

        Args:
            component (IsComponent): The component to be added to a particular collection
        """

        if issubclass(type(component), _Scope):
            if isinstance(component, Horizon):
                self.scopes[0] = component
            elif isinstance(component, Network):
                self.scopes[1] = component
        else:
            list_curr = getattr(self, component.collection())
            # skip the warnign for Scale because a default scale is already defined with 1 index
            if not issubclass(type(component), _Temporal):
                if component in list_curr:
                    warn(f'{component} is being replaced')
            setattr(self, component.collection(), sorted(set(list_curr) | {component}))

    @property
    def horizon(self):
        return self.scopes[0]

    @property
    def network(self):
        return self.scopes[1]

    @property
    def nodes(self):
        return self.locations

    @property
    def edges(self):
        return self.linkages

    @property
    def pairs(self):
        return [(i.source, i.sink) for i in self.linkages]

    @property
    def sources(self):
        return sorted({i[0] for i in self.pairs})

    @property
    def sinks(self):
        return sorted({i[1] for i in self.pairs})
