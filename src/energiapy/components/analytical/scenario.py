"""The main object in energiapy. Everything else is defined as a scenario attribute.
"""

from dataclasses import dataclass, field

from ...components.spatial.linkage import Linkage
from ...components.spatial.location import Location
from ...components.spatial.network import Network
from ...components.temporal.horizon import Horizon
from ...core.inits.scenario import ScnInit
from ...funcs.add_to.component import add_component
from ...funcs.update.name import update_name

# if TYPE_CHECKING:
# from ..types.alias import IsComponent
# from .player import Player


@dataclass
class Scenario(ScnInit):
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

    name: str = r'\m/>'
    basis_land: str = 'Acres'
    basis_cash: str = '$'
    default_players: bool = field(default=True)

    def __post_init__(self):
        ScnInit.__post_init__(self)

    def __setattr__(self, name, value):

        if hasattr(value, '_named') and not value._named:
            update_name(component=value, name=name, horizon=self.horizon)

            if isinstance(value, Horizon):
                self.horizon, self.scales = value, value.scales
                for i in value.scales:
                    setattr(self, i.name, i)

            elif isinstance(value, Network):
                pass

            elif isinstance(value, (Location, Linkage)):
                add_component(
                    to=self, list_attr=value.collection, add=value)
                add_component(
                    to=self.network, list_attr=value.collection, add=value)
                
                
            else:
                add_component(
                    to=self, list_attr=value.collection, add=value)

        super().__setattr__(name, value)
