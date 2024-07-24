
from dataclasses import dataclass

from ..funcs.print import printer
from .horizon import Horizon
from .process import Process
from .resource import Resource
from ..model.type.alias import IsComponent

from warnings import warn


@dataclass
class Scenario:
    """
    A scenario for a considered system. It collects all the components of the model.

    Input:
        name (str, optional): Name. Defaults to 'energia'.
        horizon (Horizon): Planning horizon of the problem, generated post-initialization.
        scales (List[TemporalScales]): List of TemporalScale objects, generated post-initialization.
        resources (List[Resource]): List of Resource objects, generated post-initialization.
        processes (List[Process]): List of Process objects, generated post-initialization.
        locations (List[Location]): List of Location objects, generated post-initialization.
        transports (List[Transport]): List of Transport objects, generated post-initialization.
        linkages (List[Linkage]): List of Linkage objects, generated post-initialization.
        network (Network): Network

    Examples:

        There is not much to this class, it is just a container for the components of the model.

        >>> from energiapy.components import Scenario
        >>> s = Scenario(name='Current')

    """

    name: str = r'\m/>'

    def __post_init__(self):

        # create empty attributes to collect components
        self.horizon, self.network = None, None

        for comps in ['resources', 'processes', 'locations', 'transports', 'linkages']:
            setattr(self, comps, list())

        for mod in ['parameters', 'variables', 'constraints']:
            setattr(self, mod, list())

    def __setattr__(self, name, value):
        # *Would avoid making a general function to update components for the sake of clarity
        super().__setattr__(name, value)

        if isinstance(value, Horizon):
            if not value.name:  # this assigns the name of component to one declared by user
                setattr(value, 'name', name)

            if not self.horizon:
                setattr(self, 'horizon', value)
                setattr(self, 'scales', value.scales)
                for i in value.scales:
                    setattr(self, i.name, i)

        if hasattr(value, 'named') and not value.named:
            value.make_named(name=name, horizon=self.horizon)

        if isinstance(value, Resource):
            self.update_component_list(list_attr='resources', component=value)

        if isinstance(value, Process):

            if hasattr(value, 'stored_resource'):
                r_naav = f'{value.stored_resource.name}_in_{value.name}'
                setattr(self, r_naav, value.conversion.produce)
                p_naav = f'{value.name}_d'

                setattr(self, p_naav, Process(
                    conversion={value.stored_resource: {i: -j for i, j in value.produce.items()}}, capacity=True))

                for i in ['store', 'store_loss', 'store_cost']:
                    setattr(getattr(self, p_naav), i, {
                            getattr(self, r_naav): getattr(value, i)})

                setattr(getattr(getattr(self, name), 'conversion'), 'conversion',  {value.conversion.produce: {
                        value.stored_resource: value.conversion.conversion[value.stored_resource]}})

            setattr(self, 'resources', list(
                set(getattr(self, 'resources')) | {value}))

        for i in ['parameters', 'variables', 'constraints']:
            if hasattr(value, i):
                getattr(self, i).extend(getattr(value, i))

    # * ---------Methods-----------------

    def params(self):
        printer(component=self, print_collection='parameters')

    def vars(self):
        printer(component=self, print_collection='variables')

    def cons(self):
        printer(component=self, print_collection='constraints')

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

    @ staticmethod
    def cname() -> str:
        """Returns class name"""
        return 'Scenario'

    # * ---------Dunders-----------------

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
