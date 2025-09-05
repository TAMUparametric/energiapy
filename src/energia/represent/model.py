"""A Model"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Type

from dill import dump

from ..components.commodity.misc import Cash, Emission, Land, Material
from ..components.commodity.resource import Resource
from ..components.game.player import Player
from ..components.impact.categories import Economic, Environ, Social
from ..components.measure.unit import Unit
from ..components.operation.process import Process
from ..components.operation.storage import Storage
from ..components.operation.transport import Transport
from ..components.spatial.linkage import Link
from ..components.spatial.location import Loc
from ..components.temporal.period import Period
from ..core.x import X
from ..dimensions.decisionspace import DecisionSpace
from ..modeling.parameters.conversion import Conv
from ..modeling.variables.control import Control
from ..modeling.variables.impact import Impact
from ..modeling.variables.state import State
from ..modeling.variables.stream import Stream
from .blocks import _Init

if TYPE_CHECKING:
    from gana.sets.index import I

    from ..modeling.constraints.bind import Bind
    from ..modeling.variables.aspect import Aspect


@dataclass
class Model(DecisionSpace, _Init):
    """An abstract representation of an energy system

    Args:
        name (str) = m 
        default (bool): True if want some default objects to be declared
        capacitate (bool): True if want to determine process capacities to bound operations

    

    Attributes:
        name (str): Name of the Model
        default (bool): True if want some default objects to be declared
        added (list[str]): List of added objects to the Model
        update_map (dict): Map of what representation and collection by type
        time (Time): Temporal Scope of the Model
        space (Space): Spatial Scope of the Model
        impact (Impact): Impact on the exterior of the Model
        tree (Tree): Feasible region (Decision-Making) of the Model
        graph (Graph): Graph (Network) of the Model
        system (System): System (Resource Task Network) of the Model
        program (Program): Mathematical (mixed integer) program of the Model
        conversions (list[Conversion]): List of Balances in the Model
        convmatrix (dict[Process, dict[Resource, int | float | list]]): Conversion matrix of the Model


    Raises:
        ValueError: If an attribute name already exists in the Model
    """

    name: str = 'm'
    default: bool = True
    capacitate: bool = False

    def __post_init__(self):

        # what components have been added to the model
        self.added: list[str] = []
        # map of what representation and collection within that representation
        # an object of a particular type belongs to

        # the structure of components:
        # I Temporal representation (Time):
        # 1.  Period (Period) generates a bespoke discretization.
        # II Spatial representation (Space):
        # 1. Spatial representation (Space). Location (Loc) generate a bespoke discretization.
        # III Streams (System):
        # 1. Commodity (Resource) of any kind
        # 2. Emission (Emission) resource
        # 3. Land (Land) resource
        # 4. Money (Cash)
        # 5. Material (Material) used to setup processes
        # 6. etc. societal (Jobs), etc (Etc).
        # IV Operations (System):
        # 1. A production operation (Process) which describes a task in the system that involves conversion of resources
        # 2. A storage operation (Storage) which describes a task in the system that involves storing (charge) resources
        # and retrieving (discharge) them at later times.
        # 3. A transport operation (Transport) which describes a task in the system that involves transporting resources from
        #    one location to another.
        # V Impact, scales a stream and projects onto a common metric
        #   1. Impact (Impact) categories include Eco, Soc

        self.update_map = {
            Period: [('time', 'periods')],
            Loc: [('space', 'locs')],
            Link: [
                ('space', 'links'),
            ],
            Environ: [('impact', 'envs')],
            Social: [('impact', 'socs')],
            Economic: [('impact', 'ecos')],
            Resource: [('system', 'resources')],
            Process: [('system', 'processes')],
            Storage: [('system', 'storages')],
            Transport: [('system', 'transits')],
            Player: [('tree', 'players')],
            Cash: [('system', 'currencies', True)],
            Land: [('system', 'lands', True)],
            Emission: [('system', 'emissions', True)],
            Material: [('system', 'materials', True)],
            State: [('tree', 'states')],
            Control: [('tree', 'controls')],
            Stream: [('tree', 'streams')],
            Impact: [('tree', 'impacts')],
        }
        # ---- Different representations of the model ---
        _Init.__post_init__(self)

        # measuring units
        self.units: list[Unit] = []
        self.conversions: list[Conv] = []  # not added to program
        self.convmatrix: dict[Process, dict[Resource, int | float | list]] = {}

        # introduce the dimensions of the model
        DecisionSpace.__post_init__(self)
        

    def update(
        self,
        name: str,
        value: X,
        represent: str,
        collection: str,
        subset: bool = False,
    ):
        """Update the Model with a new value

        Args:
            name (str): Name of the value to be added
            value (X): Value to be added
            represent (str): Representation to which the value belongs
            collection (str): Collection within the representation to which the value belongs
            subset (bool, optional): If True, the value is not added to the Model's
        """

        if not subset:
            # ignore subsets
            value.name = name
            # every component is handed the model
            value.model = self

            if name in self.added:
                # do not allow overriding of components
                # throw error if name already exists
                raise ValueError(f'{name} already defined')
                # added is the list of all components that have been added to the model
            self.added.append(name)

        model_set: list = getattr(getattr(self, represent), collection)
        # the set that needs to be updated
        model_set.append(value)

        # update the index set for index elements
        if collection in [
            'resources',
            'currencies',
            'lands',
            'emissions',
            'materials',
            'processes',
            'storages',
            'transits',
        ]:
            index_set: I = getattr(self.program, collection)
            setattr(self.program, collection, index_set | value.I)

    def declare(self, what: Type[X], names: list[str]):
        """Declares objects conveniently"""
        for i in names:
            setattr(self, i, what())

    def Link(self, source: Loc, sink: Loc, dist: float | Unit = None, bi: bool = False):
        """Link two Locations"""
        if source - sink:
            # if source and sink are already linked
            raise ValueError(
                f'A link already defined between {source} and {sink}.\n'
                'For multiple links with different attributes, use model.named_link = Link(...)'
            )

        link = Link(source=source, sink=sink, dist=dist, bi=bi, auto=True)
        setattr(self, f'{source.name}-{sink.name}', link)

    def __setattr__(self, name, value):

        if isinstance(value, (str, dict, list, bool)):
            # if value is a string, dict, list or bool
            # set the attribute to the value
            super().__setattr__(name, value)
            return

        if isinstance(value, Unit):
            value.name = name
            self.units.append(value)

        # map to representation and collection
        for cls, updates in self.update_map.items():
            if isinstance(value, cls):
                for args in updates:
                    self.update(name, value, *args)
                break

        # Locations also belong to spaces
        if isinstance(value, Loc):

            self.program.spaces |= value.I

        # Linkages also belong to spaces
        elif isinstance(value, Link):
            self.program.spaces |= value.I
            self.program.sources |= value.source.I
            self.program.sinks |= value.sink.I
            self.space.sources.append(value.source)
            self.space.sinks.append(value.sink)
            if value.bi:
                # if bidirectional, set the reverse linkage
                # also ensures that all linakges go in one direction only
                rev = value.rev()
                setattr(self, rev.name, rev)

        elif isinstance(value, Conv):
            # Cash can be declared through their exchange with other Cash
            if value.balance and isinstance(list(value.balance)[0], Cash):
                cash, task = Cash(), Conv()
                cash.name = name
                task.name = list(value.balance)[0].name
                task.balance = {cash: list(value.balance.values())[0]}
                setattr(cash, task.name, task)
                setattr(self, name, cash)
                return
            else:
                setattr(self.tree, name, value)
                self.conversions.append(value)

        super().__setattr__(name, value)

    def show(self, descriptive: bool = False, categorical: bool = True):
        """Pretty print the Model"""
        self.program.show(descriptive, categorical=categorical)

    def sol(self, slack: bool = True):
        """Solution"""
        return self.program.sol(slack)

    def save(self, as_type: str = 'dill'):
        """Save the Model to a file"""
        if as_type == 'dill':
            with open(self.name + '.energia', 'wb') as f:
                dump(self.solution, f)
        else:
            raise ValueError(f'Unknown type {as_type} for saving the model')

    def draw(self, variable: Aspect | Bind):
        """Draw the solution for a variable"""
        self.program.draw(variable.V())

    def default_period(self, size: int = None) -> Period:
        """Return a default period"""

        if size:
            # if size is passed,
            # make a new temporal scale
            new_period = Period(f'Time/{size}', periods=size, of=self.horizon)
            setattr(self, f't{len(self.time.periods)}', new_period)

            # return the newly created period
            return self.time.periods[-1]

        # or create a default period

        self.t0 = Period('Time')
        return self.t0

    def default_loc(self) -> Loc:
        """Return a default location"""
        self.l = Loc(label='l')
        return self.l

    # -----------------------------------------------------
    #                    Hashing
    # -----------------------------------------------------

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
