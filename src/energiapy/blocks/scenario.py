"""The main object in energiapy. Everything else is defined as a scenario attribute.
"""

from dataclasses import dataclass, field

from ..components._base._component import _Component
from ..components._base._defined import _Defined
from ..components.operational.process import Process
from ..components.scope.horizon import Horizon
from ..components.scope.network import Network
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.temporal.scale import Scale
from ._base._default import _Default
from .data import Data, DataBlock
from .matrix import Matrix
from .program import Program, ProgramBlock
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
        self.system = System(name=self.name)
        self.program = Program(name=self.name)
        self.data = Data(name=self.name)
        self.matrix = Matrix(name=self.name)

        self._model = {
            'system': self.system,
            'program': self.program,
            'data': self.data,
            'matrix': self.matrix,
        }

        self._default()

    def __setattr__(self, name, value):

        if issubclass(type(value), (_Component)):

            value.personalize(name=name, **self._model)
            setattr(self.system, name, value)

            if issubclass(type(value), _Defined):

                value.make_consistent()

                datablock = DataBlock(component=value)
                programblock = ProgramBlock(component=value)

                for inp in value.inputs():

                    if getattr(value, inp, False):
                        setattr(datablock, inp, {value: getattr(value, inp)})

                        setattr(value, inp, getattr(datablock, inp))

                setattr(self.data, name, datablock)

                setattr(programblock, name, datablock)

                setattr(self.program, name, programblock)

        if isinstance(value, Horizon):

            if self.system.scales:  # if new horizon is defined, reset scales
                self.system.scales = []

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

        if isinstance(value, Process):

            getattr(self.system, name).conversionize()

        super().__setattr__(name, value)

    @property
    def players(self):
        """Players of the System"""
        return self.system.players

    @property
    def horizon(self):
        """Horizon of the System"""
        return self.system.horizon

    @property
    def scales(self):
        """Temporal Scales of the System"""
        return self.system.scales

    @property
    def network(self):
        """Network of the System"""
        return self.system.network

    @property
    def emissions(self):
        """Emissions of the System"""
        return self.system.emissions

    @property
    def resources(self):
        """Resources of the System"""
        return self.system.resources

    @property
    def materials(self):
        """Materials of the System"""
        return self.system.materials

    @property
    def processes(self):
        """Process Operations of the System"""
        return self.system.processes

    @property
    def storages(self):
        """Storage Operations of the System"""
        return self.system.storages

    @property
    def transits(self):
        """Transit Operations of the System"""
        return self.system.transits

    # spatial collections
    @property
    def locations(self):
        """Locations of the System"""
        return self.system.locations

    @property
    def linkages(self):
        """Linkages of the System"""
        return self.system.linkages

    @property
    def nodes(self):
        """Nodes of the System"""
        return self.system.nodes

    @property
    def edges(self):
        """Edges of the System"""
        return self.system.edges

    @property
    def sources(self):
        """Source Locations of the System"""
        return self.system.sources

    @property
    def sinks(self):
        """Sink Locations of the System"""
        return self.system.sinks

    @property
    def cash(self):
        """Cash of the System"""
        return self.system.cash

    @property
    def land(self):
        """Land of the System"""
        return self.system.land

    @property
    def components(self):
        """All Components of the System"""
        return self.system.components

    @property
    def constraints(self):
        """All Constraints of the System"""
        return self.program.constraints

    @property
    def variables(self):
        """All Variables of the System"""
        return self.program.variables

    @property
    def parameters(self):
        """All Parameters of the System"""
        return self.program.parameters

    def eqns(self):
        """Prints all equations in the program"""
        self.program.eqns()
