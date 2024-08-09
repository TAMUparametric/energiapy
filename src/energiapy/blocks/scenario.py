"""The main object in energiapy. Everything else is defined as a scenario attribute.
"""

from dataclasses import dataclass, field

from ..components._base._component import _Component
from ..components._base._defined import _Defined
from ..components.scope.horizon import Horizon
from ..components.scope.network import Network
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.temporal.scale import Scale
from ._default import _Default
from .abstract import Abstract
from .data import Data
from .matrix import Matrix
from .program import Program
from .system import System


@dataclass
class Scenario(_Default):
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

    name: str = field(default=':s:')

    def __post_init__(self):

        # Declare Model
        self._system = System(name=self.name)
        self._program = Program(name=self.name)
        self._data = Data(name=self.name)
        self._matrix = Matrix(name=self.name)
        self._abstract = Abstract(name=self.name)

        self._model = {
            'system': self._system,
            'program': self._program,
            'data': self._data,
            'matrix': self._matrix,
            'abstract': self._abstract,
        }

        self._default()

    def __setattr__(self, name, value):

        if issubclass(type(value), (_Component)):

            value.personalize(name=name, **self._model)

            if issubclass(type(value), _Defined):
                value.make_consistent()

            setattr(self._system, name, value)

        if isinstance(value, Horizon):
            for i in range(value.n_scales):

                if value.label_scales:
                    label_scale = value.label_scales[i]
                else:
                    label_scale = value.label_scales

                setattr(
                    self,
                    value._name_scales[i],
                    Scale(
                        index=value.make_index(position=i, nested=value.nested),
                        label=label_scale,
                    ),
                )

        if isinstance(value, Network):
            for i in value.locs:

                if value.label_locs:
                    label_node = value.label_locs[i]
                else:
                    label_node = value.label_locs

                setattr(self, i, Location(label=label_node))

        if isinstance(value, Linkage):
            if value.bi:

                setattr(value, 'bi', False)

                setattr(
                    self,
                    f'{value.name}_',
                    Linkage(
                        source=value.sink,
                        sink=value.source,
                        label=value.label,
                        distance=value.distance,
                        bi=False,
                    ),
                )

        super().__setattr__(name, value)

    @property
    def players(self):
        return self._system.players

    @property
    def horizon(self):
        return self._system.horizon

    @property
    def scales(self):
        return self._system.scales

    @property
    def network(self):
        return self._system.network

    @property
    def assets(self):
        return self._system.assets

    @property
    def emissions(self):
        return self._system.emissions

    @property
    def resources(self):
        return self._system.resources

    @property
    def materials(self):
        return self._system.materials

    @property
    def processes(self):
        return self._system.processes

    @property
    def transits(self):
        return self._system.transits

    # spatial collections
    @property
    def locations(self):
        return self._system.locations

    @property
    def linkages(self):
        return self._system.linkages

    @property
    def nodes(self):
        return self._system.nodes

    @property
    def edges(self):
        return self._system.edges

    @property
    def sources(self):
        return self._system.sources

    @property
    def sinks(self):
        return self._system.sinks

    @property
    def cash(self):
        return self._system.cash

    @property
    def land(self):
        return self._system.land
