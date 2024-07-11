
from .horizon import Horizon
from .resource import Resource
# from .process import Process
# from .location import Location
# from .temporal_scale import TemporalScale

from dataclasses import dataclass


@dataclass
class Scenario:
    """
    A scenario for a considered system. It collects all the components of the model.

    Attributes:
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

    name: str = 'energia'

    def __post_init__(self):

        # create empty attributes to collect components
        self.horizon, self.network = None, None

        for comps in ['resources', 'processes', 'locations', 'transports', 'linkages']:
            setattr(self, comps, list())

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if isinstance(value, Horizon):
            if not value.name:
                setattr(value, 'name', name)
            if not self.horizon:
                setattr(self, 'horizon', value)
                setattr(self, 'scales', value.scales)
                for i in value.scales:
                    setattr(self, i.name, i)

        if isinstance(value, Resource):
            if not value.name:
                setattr(value, 'name', name)
                setattr(value, 'horizon', self.horizon)
            getattr(self, 'resources').append(value)

        #     # if getattr(self, name).scales is None:
            # getattr(self, name).scales = self.scales
            # self.resources.append(getattr(self, name))
        # if isinstance(getattr(self, name), Process):
        #     setattr(getattr(self, name), 'name', name)
        #     self.processes.append(getattr(self, name))

    # * ---------Methods-----------------

    @staticmethod
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
