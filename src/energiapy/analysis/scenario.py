"""The main object in energiapy. Everything else is defined as a scenario attribute.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.operation.process import Process
from ..components.operation.storage import Storage
from ..components.operation.transit import Transit
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.temporal.horizon import Horizon
from ..core.inits.scenario import ScnInit
from ..funcs.add.component import add_component
from ..funcs.add.element import add_element
from ..funcs.update.name import update_name
# if TYPE_CHECKING:
from ..types.alias import IsComponent
from .player import Player


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

    def __post_init__(self):
        ScnInit.__post_init__(self)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

        if isinstance(value, Player):
            if not value.name:
                setattr(value, 'name', name)
                add_component(
                    scenario=self, list_attr='player_all', component=value)

        if isinstance(value, Horizon):
            if not value.name:  # this assigns the name of Horizon
                setattr(value, 'name', name)

            if not self.horizon:
                setattr(self, 'horizon', value)
                setattr(self, 'scales', value.scales)
                for i in value.scales:
                    setattr(self, i.name, i)

        if hasattr(value, '_named') and not value._named:
            update_name(component=value, name=name, horizon=self.horizon)

        # *Would avoid making a general function to update components for the sake of clarity
        if isinstance(value, IsComponent):
            add_component(
                scenario=self, list_attr=f'{value.cname().lower()}_all', component=value)

        # if isinstance(value, Resource):
        #     self.update_component_list(list_attr='resources', component=value)

        # if isinstance(value, Process):
        #     self.update_component_list(list_attr='processes', component=value)

            # if hasattr(value, 'stored_resource'):
            #     r_naav = f'{value.stored_resource.name}_in_{value.name}'
            #     setattr(self, r_naav, value.conversion.produce)
            #     p_naav = f'{value.name}_d'

            #     setattr(self, p_naav, Process(
            #         conversion={value.stored_resource: {i: -j for i, j in value.produce.items()}}, capacity=True))

            #     for i in ['store', 'store_loss', 'store_cost']:
            #         setattr(getattr(self, p_naav), i, {
            #                 getattr(self, r_naav): getattr(value, i)})

            #     setattr(getattr(getattr(self, name), 'conversion'), 'conversion',  {value.conversion.produce: {
            #             value.stored_resource: value.conversion.conversion[value.stored_resource]}})

            # setattr(self, 'resources', list(
            #     set(getattr(self, 'resources')) | {value}))

        add_element(component=self, aspect=value)
