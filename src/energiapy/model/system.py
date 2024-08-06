from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from warnings import warn

from ..components._component import _Component, _Spatial, _Scope  # , _Analytical
from ..components.scope.horizon import Horizon
from ..components.scope.network import Network
from .._core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from .._core._aliases._is_component import IsComponent


@dataclass
class System(_Dunders):
    """Collects System Components"""

    name: str = field(default=None)

    def __post_init__(self):

        self.name = f'System|{self.name}|'

        # Scope
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

        if issubclass(type(value), _Component):
            self.add(value)

        if issubclass(type(value), _Spatial):
            # keeping scopes as a list and horizon and network as properties
            # avoids recursion
            setattr(self.scopes[1], name, value)

        super().__setattr__(name, value)

    def add(self, add: IsComponent):
        """Updates the lists of components in the scenario.

        Args:
            add (IsComponent): The component to be added to a particular collection
        """

        if issubclass(type(add), _Scope):
            if isinstance(add, Horizon):
                self.scopes[0] = add
            elif isinstance(add, Network):
                self.scopes[1] = add
        else:
            list_curr = getattr(self, add.collection())
            if add in list_curr:
                warn(f'{add} is being replaced')
            setattr(self, add.collection(), sorted(set(list_curr) | {add}))

    @property
    def horizon(self):
        return self.scopes[0]

    @property
    def network(self):
        return self.scopes[1]
