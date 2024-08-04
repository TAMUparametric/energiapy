"""The main object in energiapy. Everything else is defined as a scenario attribute.
"""

from dataclasses import dataclass

from ...components.commodity.cash import Cash
from ...components.commodity.emission import Emission
from ...components.commodity.land import Land
from ...components.spatial.linkage import Linkage
from ...components.spatial.location import Location
from ...components.spatial.network import Network
from ...components.temporal.horizon import Horizon
from ...funcs.add_to.component import add_component
# from ...analysis.player import Players
from .._initialize._scenario import _Scenario
from .player import Player

# if TYPE_CHECKING:
# from ..types.alias import IsComponent
# from .player import Player


@dataclass
class Scenario(_Scenario):
    """
    A scenario for a considered system. It collects all the components of the model.

    Input:
        name (str, optional): Name. Defaults to 'energia'.
        horizon (Horizon): Planning horizon of the problem, generated post-initialization.
        scales (List[Scale]): List of Scale objects, generated post-initialization.
        resources (List[Resource]): List of Resource objects, generated post-initialization.
        processes (List[Process]): List of Process objects, generated post-initialization.
        locations (List[Location]): List of Location objects, generated post-initialization.
        transports (List[Transit]): List of Transit objects, generated post-initialization.
        linkages (List[Linkage]): List of Linkage objects, generated post-initialization.
        network (Network): Network

    Examples:

        There is not much to this class, it is just a container for the components of the model.

        >>> from energiapy.components import Scenario
        >>> s = Scenario(name='Current')

    """

    def __post_init__(self):
        _Scenario.__post_init__(self)

    def __setattr__(self, name, value):

        # Avoid making general functions to handle these for the sake of clarity

        # ScopeComponent are have name attributes

        if isinstance(value, Horizon) and not value._named:

            setattr(value, 'name', name)

            self.horizon, self.scales = value, value.scales

            for i in value.scales:
                setattr(self, i.name, i)

            self.system.horizon, self.system.scales = value, value.scales

        if isinstance(value, Network) and not value._named:

            setattr(value, 'name', name)
            self.network = value

            self.system.network = value

        if self._is_scoped and not self._is_initd:

            # these are some initializations, which include:
            # Assets - Land and Cash
            # Emissions if default_emissions is True
            # Players if default_players is True (default)
            # see components._initialize._scenario.py for details
            self._initialize()

        if isinstance(value, Cash) or isinstance(value, Land):

            value.personalize(name, self.horizon, self.network)

            self.add(value)

            self.system.add(value)

        # Players and Emissions can be added by the user as well
        if isinstance(value, Player):

            value.personalize(name, self.horizon, self.network)

            self.add(value)

            self.system.add(value)

        if isinstance(value, Emission):

            value.personalize(name, self.horizon, self.network)

            self.add(value)

            self.system.add(value)

        # These are strictly user defined

        # spatial
        if isinstance(value, (Location, Linkage)):

            value.personalize(name, self.horizon, self.network)

            self.add(value)

            self.network.add(value)

            self.system.add(value)

        # commodities

        # operational

        super().__setattr__(name, value)

    def add(self, component):
        """Add a Component to System
        """
        add_component(self, list_attr=component.collection, add=component)

    @property
    def _is_scoped(self):
        """Return true if the horizon and Network are both defined
        """
        if getattr(self, 'horizon', False) and getattr(self, 'network', False):
            return True

        else:
            return False
