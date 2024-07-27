"""The main object in energiapy. Everything else is defined as a scenario attribute.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from warnings import warn

from ..core.base import Base
from ..core.onset import EmtCol, ScnInit
from ..funcs.component.update import update_element
from .commodity.cash import Cash
from .commodity.emission import Emission
from .commodity.land import Land
from .commodity.material import Material
from .commodity.resource import Resource
from .operation.process import Process
from .operation.storage import Storage
from .operation.transit import Transit
from .spatial.linkage import Linkage
from .spatial.location import Location
from .temporal.horizon import Horizon

# if TYPE_CHECKING:
from ..type.alias import IsComponent


@dataclass
class Scenario(ScnInit, EmtCol, Base):
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
        EmtCol.__post_init__(self)

    def __setattr__(self, name, value):
        # *Would avoid making a general function to update components for the sake of clarity
        super().__setattr__(name, value)

        if isinstance(value, Horizon):
            if not value.name:  # this assigns the name of Horizon
                setattr(value, 'name', name)

            if not self.horizon:
                setattr(self, 'horizon', value)
                setattr(self, 'scales', value.scales)
                for i in value.scales:
                    setattr(self, i.name, i)

        if hasattr(value, '_named') and not value._named:
            value.make_named(name=name, horizon=self.horizon)

        if isinstance(value, IsComponent):
            self.update_component_list(
                list_attr=f'{value.cname().lower()}_all', component=value)

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

        update_element(component=self, aspect=value)

    # * ---------Methods-----------------

    def update_component_list(self, list_attr, component: IsComponent):
        """Updates the lists of components in the scenario.

        Args:
            list_attr (str): The name of the attribute representing the list of components.
            component (IsComponent): The component to be added to the list.

        Returns:
            None

        Raises:
            None

        """
        list_curr = getattr(self, list_attr)
        if component in list_curr:
            warn(f'{component.name} is being replaced in Scenario')
        # add component to list
        setattr(self, list_attr, list(set(list_curr) | {component}))
