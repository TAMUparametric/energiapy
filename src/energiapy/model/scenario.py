"""The main object in energiapy. Everything else is defined as a scenario attribute.
"""

from dataclasses import dataclass, field
from ..components._component import _Component
from ..components.scope.horizon import Horizon
from ..components.temporal.scale import Scale
from ..types.element.disposition import TemporalDisp
from ._default import _Default
from .data import Data
from .matrix import Matrix
from .program import Program
from .system import System
from .abstract import Abstract


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

    name: str = field(default=r'\m/>')

    def __post_init__(self):

        # Declare Model
        self.system = System(name=self.name)
        self.program = Program(name=self.name)
        self.data = Data(name=self.name)
        self.matrix = Matrix(name=self.name)
        self.abstract = Abstract(name=self.name)

        self._model = {
            'system': self.system,
            'program': self.program,
            'data': self.data,
            'matrix': self.matrix,
            'abstract': self.abstract,
        }

        self._default()

    def __setattr__(self, name, value):

        if issubclass(type(value), (_Component)):

            value.personalize(name=name, **self._model)

            setattr(self.system, name, value)

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

        super().__setattr__(name, value)

    @property
    def players(self):
        return self.system.players

    @property
    def horizon(self):
        return self.system.horizon

    @property
    def scales(self):
        return self.system.scales

    @property
    def network(self):
        return self.system.network

    @property
    def assets(self):
        return self.system.assets

    @property
    def emissions(self):
        return self.system.emissions

    @property
    def resources(self):
        return self.system.resources

    @property
    def materials(self):
        return self.system.materials

    @property
    def processes(self):
        return self.system.processes

    @property
    def transits(self):
        return self.system.transits

    @property
    def locations(self):
        return self.system.locations

    @property
    def linkages(self):
        return self.system.linkages
