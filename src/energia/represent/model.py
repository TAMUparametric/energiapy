"""A Model"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self, Type, Optional

from dill import dump

from .._core._x import _X
from ..components.commodity.currency import Currency
from ..components.commodity.emission import Emission
from ..components.commodity.land import Land
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.game.couple import Couple
from ..components.game.player import Player
from ..components.impact.categories import Economic, Environ, Social
from ..components.measure.unit import Unit
from ..components.operation.process import Process
from ..components.operation.storage import Storage
from ..components.operation.transport import Transport
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.temporal.modes import Modes
from ..components.temporal.periods import Periods
from ..components.temporal.scales import TemporalScales
from ..library.recipes import (
    capacity_sizing,
    economic,
    environmental,
    free_movement,
    inventory_sizing,
    operating,
    social,
    trade,
    usage,
)
from ..modeling.parameters.conversion import Conversion
from ..modeling.variables.control import Control
from ..modeling.variables.recipe import Recipe
from ..modeling.variables.states import Impact, State, Stream
from .blocks import _Init

if TYPE_CHECKING:
    from gana.sets.index import I
    from .._core._component import _Component
    from ..modeling.constraints.bind import Bind
    from ..modeling.variables.aspect import Aspect
    from enum import Enum


@dataclass
class Model(_Init):
    """
    An abstract representation of an energy system.

    :param name: Name of the Model. Defaults to m.
    :type name: str
    :param init: List of functions to initialize the Model. Defaults to None.
    :type init: list[Callable], optional
    :param default: True if some default objects should be declared.
    :type default: bool
    :param capacitate: True if process capacities should be determined to bound operations.
    :type capacitate: bool

    :ivar added: List of added objects to the Model.
    :vartype added: list[str]
    :ivar update_map: Map of representation and collection by type.
    :vartype update_map: dict
    :ivar time: Temporal Scope of the Model.
    :vartype time: Time
    :ivar space: Spatial Scope of the Model.
    :vartype space: Space
    :ivar impact: Impact on the exterior of the Model.
    :vartype impact: Impact
    :ivar tree: Feasible region (Decision-Making) of the Model.
    :vartype tree: Tree
    :ivar graph: Graph (Network) of the Model.
    :vartype graph: Graph
    :ivar system: System (Resource Task Network) of the Model.
    :vartype system: System
    :ivar program: Mathematical (mixed integer) program of the Model.
    :vartype program: Program
    :ivar conversions: List of Balances in the Model.
    :vartype conversions: list[Conversion]
    :ivar convmatrix: Conversion matrix of the Model.
    :vartype convmatrix: dict[Process, dict[Resource, int | float | list]]
    :ivar modes_dict: Dictionary mapping Bind objects to Modes.
    :vartype modes_dict: dict[Bind, Modes]
    :siunits_set: True if SI units have been set.
    :vartype siunits_set: bool
    :ivar cookbook: Recipes to create Aspects.
    :vartype cookbook: dict[str, Recipe]
    :ivar attr_map: Map of attribute names to recipes for creating them.
    :vartype attr_map: dict[str, dict[str, Recipe]]
    :ivar classifiers: List of classifiers for the Model.
    :vartype classifiers: list[Enum]


    :raises ValueError: If an attribute name already exists in the Model.
    """

    name: str = "m"
    init: Optional[list[Callable[Self]]] = None
    default: bool = True
    capacitate: bool = False

    def __post_init__(self):

        # what components have been added to the model
        self.added: list[str] = []
        # map of what representation and collection within that representation
        # an object of a particular type belongs to

        # the structure of components:
        # I Temporal representation (Time):
        # 1.  Periods (Periods) generates a bespoke discretization.
        # II Spatial representation (Space):
        # 1. Spatial representation (Space). Location (Loc) generate a bespoke discretization.
        # III Streams (System):
        # 1. Commodity (Resource) of any kind
        # 2. Emission (Emission) resource
        # 3. Land (Land) resource
        # 4. Money (Currency)
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
            Periods: ("time", "periods"),
            Modes: ("time", "modes"),
            Location: ("space", "locations"),
            Linkage: ("space", "linkages"),
            Environ: (
                "consequence",
                "envs",
            ),
            Social: (
                "consequence",
                "socs",
            ),
            Economic: ("consequence", "ecos"),
            Process: ("system", "processes"),
            Storage: ("system", "storages"),
            Transport: ("system", "transits"),
            Player: ("system", "players"),
            Couple: ("system", "couples"),
            Currency: ("system", "currencies"),
            Land: ("system", "lands"),
            Emission: ("system", "emissions"),
            Material: ("system", "materials"),
            Resource: ("system", "resources"),
            Control: ("problem", "controls"),
            Stream: ("problem", "streams"),
            State: ("problem", "states"),
            Impact: ("problem", "impacts"),
        }

        # map of attribute names to recipes for creating them
        self.attr_map: dict[str, dict[str, Recipe]] = {}

        # added attributes mapping to the created Aspect objects
        self._attr_map: dict[str, Aspect] = {}

        # maps to recipes for creating aspects
        self.cookbook: dict[str, Recipe] = {}

        # ---- Different representations of the model ---
        _Init.__post_init__(self)

        # measuring units
        self.units: list[Unit] = []
        self.conversions: list[Conversion] = []  # not added to program
        self.convmatrix: dict[Process, dict[Resource, int | float | list]] = {}

        self.modes_dict: dict[Bind, Modes] = {}

        # if SI units have been set
        self.siunits_set: bool = False

        if not self.init:
            self.init = []

        if self.default:
            self.init += [
                capacity_sizing,
                operating,
                inventory_sizing,
                free_movement,
                trade,
                economic,
                environmental,
                social,
                usage,
            ]

        for func in self.init:
            func(self)

        # # introduce the dimensions of the model
        # Decisions.__post_init__(self)

        self.classifiers: dict[str, list[Enum]] = {
            "uncertainty": [],
            "structure": [],
            "scale": [],
            "paradigm": [],
        }

    # -----------------------------------------------------
    #              Set Component
    # -----------------------------------------------------

    def update(
        self,
        name: str,
        value: _X,
        represent: str,
        collection: str,
        aspects: Optional[list[str]] = None,
    ):
        """Update the Model with a new value

        Args:
            name (str): Name of the value to be added
            value (X): Value to be added
            represent (str): Representation to which the value belongs
            collection (str): Collection within the representation to which the value belongs
            subset (bool, optional): If True, the value is not added to the Model's
        """

        value.name = name
        # every component is handed the model
        value.model = self

        if name in self.added:
            # do not allow overriding of components
            # throw error if name already exists
            raise ValueError(f"{name} already defined")
            # added is the list of all components that have been added to the model
        self.added.append(name)

        # if not subset:
        #     # ignore subsets

        model_set: list = getattr(getattr(self, represent), collection)
        # the set that needs to be updated
        model_set.append(value)

        # update the index set for index elements
        if collection in [
            "resources",
            "currencies",
            "lands",
            "emissions",
            "materials",
            "processes",
            "storages",
            "transits",
        ]:
            index_set: I = getattr(self.program, collection)
            setattr(self.program, collection, index_set | value.I)

        # set aspects (as binds) on the components
        if aspects:
            for asp in aspects:
                aspect = getattr(self, asp)

                setattr(value, asp, aspect(value))

                if aspect.neg is not None:
                    setattr(value, aspect.neg.name, aspect.neg(value))

    def __setattr__(self, name, value):

        if isinstance(value, (str, dict, list, bool)) or value is None:
            # if value is a string, dict, list or bool
            # set the attribute to the value
            super().__setattr__(name, value)
            return

        if isinstance(value, TemporalScales):
            self.TemporalScales(value.discretizations, value.names)

            return

        if isinstance(value, Unit):
            value.name = name
            self.units.append(value)

        # map to representation and collection
        for cls, updates in self.update_map.items():
            if isinstance(value, cls):
                # for args in updates:
                self.update(name, value, *updates)
                break

        # Locations also belong to spaces
        if isinstance(value, Location):

            self.program.spaces |= value.I

        # Linkages also belong to spaces
        elif isinstance(value, Linkage):
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

        super().__setattr__(name, value)

    def __getattr__(self, name):
        # Only called when attribute does not exist
        if name in self._attr_map:
            # if attribute has been called before
            # the next time the created attribute is returned
            return self._attr_map[name]

        if name in self.cookbook:
            recipe = self.cookbook[name]

            aspect = recipe.kind(**recipe.args)
            setattr(self, name, aspect)

            return aspect

        if name in self.attr_map:
            # if this is an attribute being called for the first time
            recipe = self.attr_map[name]
            aspect_name = list(recipe.keys())[0]

            if aspect_name in self.added:
                # if same aspect is called by a different name
                return getattr(self, aspect_name)

            # these are the arguments for the aspect
            recipe = recipe[aspect_name]
            aspect = recipe.kind(**recipe.args)

            setattr(self, aspect_name, aspect)

            self._attr_map[name] = aspect

            return aspect

        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'",
        )

    def aliases(self, *names: str, to: str):
        """Set aspect aliases"""
        _add = dict.fromkeys(list(names), {to: self.cookbook[to]})
        self.attr_map = {**self.attr_map, **_add}

    def Recipe(
        self,
        name: str,
        kind: Type[Aspect],
        primary_type: tuple[Type[_Component]] | Type[_Component],
        label: str = "",
        add: str = "",
        add_latex: str = "",
        add_kind: Type[Aspect] = None,
        sub: str = "",
        sub_latex: str = "",
        sub_kind: Type[Aspect] = None,
        neg: str = "",
        neg_latex: str = "",
        neg_label: str = "",
        bound: str = "",
        ispos: bool = True,
        nn: bool = True,
        latex: str = None,
    ):
        """Creates a Recipe and updates recipes

        Args:
            name (str): name of the aspect
            kind (Type[Aspect]): type of the aspect
            primary_type (tuple[Type[_Component]] | Type[_Component]): type of primary component
            label (str, optional): label for the aspect. Defaults to ''.
            add (str, optional): add control variable. Defaults to ''.
            sub (str, optional): sub control variable. Defaults to ''.
            neg (str, optional): name of the negative aspect. Defaults to ''.
            ispos (bool, optional): whether the aspect is positive. Defaults to True.
            nn (bool, optional): whether the aspect is non-negative. Defaults to True.
            latex (str, optional): LaTeX representation for the aspect. Defaults to None.
        """
        if name in self.cookbook:
            print(f"--- Warning: Overriding existing recipe ---{name}")

        self.cookbook[name] = Recipe(
            name=name,
            kind=kind,
            label=label or name,
            add=add,
            sub=sub,
            bound=bound,
            ispos=ispos,
            nn=nn,
            primary_type=primary_type,
            latex=latex,
        )

        if add:
            if not add_kind:
                if sub_kind:
                    add_kind = sub_kind
            self.Recipe(
                name=add,
                kind=add_kind,
                primary_type=primary_type,
                label=add_latex or add,
                ispos=True,
                nn=True,
                latex=latex or add,
            )

        if sub:
            if not sub_kind:
                if add_kind:
                    sub_kind = add_kind

            self.Recipe(
                name=sub,
                kind=sub_kind,
                primary_type=primary_type,
                label=sub_latex or sub,
                ispos=False,
                nn=True,
                latex=latex or sub,
            )

        if neg:
            neg_recipe = Recipe(
                name=neg,
                kind=kind,
                label=neg_label,
                ispos=not ispos,
                nn=nn,
                primary_type=primary_type,
                latex=neg_latex or neg,
            )
            self.cookbook[neg] = neg_recipe

    # -----------------------------------------------------
    #              Birth Component
    # -----------------------------------------------------

    def declare(self, what: Type[_X], names: list[str]):
        """Declares objects conveniently"""
        for i in names:
            setattr(self, i, what())

    def Link(
        self,
        source: Location,
        sink: Location,
        dist: float | Unit = None,
        bi: bool = False,
    ):
        """Link two Locations"""
        if source - sink:
            # if source and sink are already linked
            raise ValueError(
                f"A link already defined between {source} and {sink}.\n"
                "For multiple linkages with different attributes, use model.named_link = Link(...)",
            )

        link = Linkage(source=source, sink=sink, dist=dist, bi=bi, auto=True)
        setattr(self, f"{source.name}-{sink.name}", link)

    def TemporalScales(self, discretizations: list[int], names: list[str]):
        """
        This is an easy way to define multiple time periods (scales)

        :param discretizations: List of discretizations for the temporal scale.
        :type discretizations: list[int]
        :param names: Names of the discretizations. Defaults to [t<i>] for each discretization.
        :type names: list[str], optional
        """
        # set the root period:
        setattr(self, names[-1], Periods())
        # pick up the period that was just created
        # use it as the root
        root = self.periods[-1]
        discretizations = list(reversed(discretizations))

        names = list(reversed(names[:-1]))

        if discretizations[-1] != 1:
            discretizations.append(1)
            names.append("t0")

        for disc, name in zip(discretizations, names):
            setattr(self, name, disc * root)
            root = self.periods[-1]

    def show(
        self,
        descriptive: bool = False,
        categorical: bool = True,
        category: str = None,
    ):
        """Pretty print the Model"""
        self.program.show(descriptive, categorical=categorical, category=category)

    def sol(self, n_sol: int = 0, slack: bool = True, compare: bool = False):
        """Solution"""
        return self.program.sol(n_sol=n_sol, slack=slack, compare=compare)

    def save(self, as_type: str = "dill"):
        """Save the Model to a file"""
        if as_type == "dill":
            with open(self.name + ".energia", "wb") as f:
                dump(self.solution, f)
        else:
            raise ValueError(f"Unknown type {as_type} for saving the model")

    def draw(self, variable: Aspect | Bind):
        """Draw the solution for a variable"""
        self.program.draw(variable.V())

    def default_period(self, size: int = None) -> Periods:
        """Return a default period"""

        if size:
            # if size is passed,
            # make a new temporal scale
            new_period = Periods(f"Time/{size}", periods=size, of=self.horizon)
            setattr(self, f"t{len(self.time.periods)}", new_period)

            # return the newly created period
            return self.time.periods[-1]

        # or create a default period

        self.t0 = Periods("Time")
        return self.t0

    def default_loc(self) -> Location:
        """Return a default location"""
        self.l = Location(label="l")
        return self.l

    def default_currency(self) -> Currency:
        """Return a default currency"""
        if self.currencies:
            return self.currencies[0]

        self.money = Currency(label="$")
        return self.money

    def locate(self, *operations: Process | Storage):
        """Locate operations in the network"""
        self.network.locate(*operations)

    def __call__(self, *funcs: Callable[Self]):
        """Set functions on the model

        These can include default units

        """

        for f in funcs:
            f(self)

    # -----------------------------------------------------
    #                    Hashing
    # -----------------------------------------------------

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
