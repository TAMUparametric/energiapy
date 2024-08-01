"""The main object in energiapy. Everything else is defined as a scenario attribute.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..core.inits.scenario import ScnInit
from ..funcs.add_to.scenario import add_component
from ..funcs.update.name import update_name
from ..components.temporal.horizon import Horizon

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

            if isinstance(value, Horizon):  
                update_name(component=value, name=name)
                self.horizon, self.scales = value, value.scales
                for i in value.scales:
                    setattr(self, i.name, i)
            else:
                update_name(component=value, name=name, horizon=self.horizon)
                add_component(
                    scenario=self, list_attr=value.collection, component=value)

        super().__setattr__(name, value)
