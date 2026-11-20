"""A Model."""

from __future__ import annotations

import logging
import os
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any, Literal

from dill import dump

from .._core._x import _X
from ..components.commodities.currency import Currency
from ..components.commodities.emission import Emission
from ..components.commodities.land import Land
from ..components.commodities.material import Material
from ..components.commodities.resource import Resource
from ..components.game.couple import Interact
from ..components.game.player import Player

# from ..components.graph.edge import Edge
# from ..components.graph.node import Node
from ..components.impact.categories import Economic, Environ, Social
from ..components.measure.unit import Unit
from ..components.operations.process import Process
from ..components.operations.storage import Storage
from ..components.operations.transport import Transport
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.temporal.lag import Lag
from ..components.temporal.modes import Modes
from ..components.temporal.periods import Periods
from ..components.temporal.scales import TemporalScales
from ..dimensions.game import Game
from ..dimensions.impact import Impact
from ..dimensions.problem import Problem
from ..dimensions.space import Space
from ..dimensions.system import System
from ..dimensions.time import Time
from ..library.aliases import aspect_aliases
from ..library.instructions import costing_commodity, costing_operation
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
from ..modeling.parameters.instruction import Instruction
from ..modeling.variables.control import Control
from ..modeling.variables.recipe import Recipe
from ..modeling.variables.states import Consequence, State, Stream
from .ations.graph import Graph
from .ations.program import Program
from .ations.scenario import Scenario

logger = logging.getLogger("energia")


if TYPE_CHECKING:
    from enum import Enum
    from typing import DefaultDict

    from gana import V

    from .._core._component import _Component
    from ..components.commodities.commodity import Commodity
    from ..modeling.indices.domain import Domain
    from ..modeling.indices.sample import Sample
    from ..modeling.variables.aspect import Aspect

    BalanceType = DefaultDict[
        Commodity,
        DefaultDict[Location | Linkage, DefaultDict[Periods | Lag, list[Aspect]]],
    ]


@dataclass
class Model:
    """
    An abstract representation of an energy system.

    :param name: Name of the Model. Defaults to m.
    :type name: str
    :param init: Functions to run in order before the optional default initializers.
        Each model copies the supplied list. Defaults to None.
    :type init: list[Callable], optional
    :param default: True if some default objects should be declared.
    :type default: bool
    :param capacitate: True if process capacities should be determined to bound operations.
    :type capacitate: bool

    :ivar added: List of added objects to the Model.
    :vartype added: list[str]
    :ivar update_map: maps component type to representation and collection.
    :vartype update_map: dict
    :ivar time: time representation of the Model.
    :vartype time: Time
    :ivar space: spatial representation of the Model.
    :vartype space: Space
    :ivar impact: impact representation of the Model.
    :vartype impact: Impact
    :ivar tree: feasible region (Decision-Making) of the Model.
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
    :ivar directory: Map of attribute names to recipes for creating them.
    :vartype directory: dict[str, dict[str, Recipe]]
    :ivar classifiers: List of classifiers for the Model.
    :vartype classifiers: list[Enum]
    :ivar grb: Dictionary which tells you what aspects of resource have GRB {loc: time: []} and {time: loc: []}.
    :vartype grb: DefaultDict[Commodity,DefaultDict[Location | Linkage, DefaultDict[Periods, list[Aspect]]]]
    :ivar dispositions: Dictionary which tells you what aspects of what component have been bound at what location and time.
    :vartype dispositions: dict[Aspect, dict[Commodity | Process | Storage | Transport, dict[Location | Linkage, dict[Periods, list[Aspect]]]]]
    :ivar maps: Maps of aspects to domains.
    :vartype maps: dict[Aspect, dict[Domain, dict[str, list[Domain]]]]
    :ivar maps_report: Maps of aspects to domains for reporting variables.
    :vartype maps_report: dict[Aspect, dict[Domain, dict[str, list[Domain]]]]


    :raises ValueError: If an attribute name already exists in the Model.

    .. admonition:: Example

        .. code-block:: python

            from energia import Model, Resource

            m = Model()
            m.heat = Resource(label="Useful heat")
            assert m.heat.name == "heat"
            assert m.heat in m.system.resources
    """

    name: str = "m"
    init: list[Callable[[Model], object]] | None = None
    default: bool = True
    capacitate: bool = False

    def __post_init__(self):
        """Initialize the component registries, representations, and default modeling recipes."""
        self.reserved_names: list[str | tuple[str, ...]] = []

        # what components have been added to the model
        self.added: list[str] = []
        # map of what representation and collection within that representation
        # an object of a particular type belongs to

        # --------------------------------------------------------------------
        # * Component Mapping to Dimension and Collection
        # --------------------------------------------------------------------
        # Dimensions in brackets
        self.familytree: dict[type[Any], tuple[str, str]] = {
            # * I Temporal (Time):
            # 1.  Periods (Periods) generates a bespoke discretization.
            Periods: ("time", "periods"),
            # 2. Modes discrete options in the same time
            Modes: ("time", "modes"),
            # * II Spatial (Space):
            # Spatial representation (Space).
            # 1. a bespoke discretization.
            Location: ("space", "locations"),
            # 2. link between them
            Linkage: ("space", "linkages"),
            # * III Streams (System):
            # All are Commodity derived:
            # 1. Money (Currency)
            Currency: ("system", "currencies"),
            # 2. Land (Land) resource
            Land: ("system", "lands"),
            # 3. Emission (Emission) resource
            Emission: ("system", "emissions"),
            # Resource is a general Commodity
            # These are Resource subsets
            # 1. Material (Material) used to setup processes
            Material: ("system", "materials"),
            # 2. etc. societal (Jobs), etc (Etc).
            Resource: ("system", "resources"),
            # * IV Operations (System):
            # 1. A production operation (Process) involves conversion of resources
            Process: ("system", "processes"),
            # 2. A transport operation (Transport) which describes a task in the system
            # that involves transporting resources from
            #    one location to another.
            Transport: ("system", "transports"),
            # 3. A storage operation (Storage) stores (charges)
            # and retrieves (discharge) resources
            Storage: ("system", "storages"),
            # *V Indicators (Consequence):
            # scales a stream and projects onto a common metric
            # categories include
            Environ: ("impact", "environment"),
            Social: ("impact", "society"),
            Economic: ("impact", "economy"),
            # * VI Game Components
            # To model Competition
            Player: ("game", "players"),
            Interact: ("game", "interacts"),
            # * VII Problem Aspects
            # The problem at hand
            # 1. to control the volume of streams
            Control: ("problem", "controls"),
            # 2. movement
            Stream: ("problem", "streams"),
            # 3. size, quantity
            State: ("problem", "states"),
            # 4. consequence
            Consequence: ("problem", "consequences"),
        }

        self.reserved_names += zip(*self.familytree.values())

        # --------------------------------------------------------------------
        # * Dimensions or Representation
        # --------------------------------------------------------------------

        # * I Dimensions
        # * 1. Time with Periods and Modes
        self.time = Time(self)
        # * 2. Space with Locations and Linkages
        self.space = Space(self)
        # * 3. Impact with Indicator categories
        self.impact = Impact(self)
        # * 4. System (Resource Task Network)
        self.system = System(self)

        # * II Representations
        # * 1. Graph with Edges and Nodes
        self.graphs = [Graph(self)]
        # * 2. Problem at hand
        self.problems = [Problem(self)]
        # * 3 Mathematical Program of mpMINLP subclass
        self.programs = [Program(model=self)]
        # * 4 Scenario, the parameter set or uncertainty realization
        self.scenarios = [Scenario(model=self)]
        # * 5 Game, the decision-making representation
        self.games = [Game(model=self)]

        # shorthand
        self._ = self.program

        # --------------------------------------------------------------------
        # * Attributes Inherited from Dimensions or Representations
        # --------------------------------------------------------------------
        # Start with patterened
        self.program_attrs = [
            "constraint",
            "function",
            "variable",
            "parameter",
            "theta",
        ]
        # word -> words and word_sets
        self.program_attrs += [
            w + s for w in self.program_attrs for s in ["s", "_sets"]
        ]
        self.program_attrs += [
            "solution",
            "solutions",
            "formulation",
            "formulations",
            "evaluation",
        ]
        # word -> n_word
        self.program_attrs += ["n_" + w for w in self.program_attrs]
        self.program_attrs += [
            "index_sets",
            "indices",
            "objectives",
            "parameter_sets",
            "X",
        ]

        self.reserved_names += self.program_attrs

        # properties that can be called by model
        # these never get set
        _program_matrices = [
            "A",
            "B",
            "C",
            "F",
            "G",
            "H",
            "CrA",
            "CrB",
            "NN",
            "A_with_NN",
            "B_with_NN",
            "Z",
            "P",
        ]

        self.reserved_names += _program_matrices

        self.properties = dict.fromkeys(_program_matrices, self.program)

        # --------------------------------------------------------------------
        # * Default Components
        # --------------------------------------------------------------------
        # if any of these attributes are called,
        # or an exiting one is returned
        self.default_components: dict[
            str,
            Callable[[], Location | Periods | Currency],
        ] = {
            "l": self._l0,
            "l0": self._l0,
            "t0": self._t0,
            "t": self._t0,
            "money": self._cash,
        }

        self.graph_components = ["edges", "nodes"]

        # --------------------------------------------------------------------
        # * Books of Maps Between:
        # --------------------------------------------------------------------
        # * matching_aspect -> Recipe
        self.cookbook: dict[str, Recipe] = {}
        # * parameter_name -> parameter_handling_instruction
        self.manual: dict[str, Instruction] = {}
        # * already_defined_user_input_attr -> matching_aspect
        self.registry: dict[str, Aspect] = {}
        # * user_input_attr -> matching_aspect -> Recipe
        self.directory: dict[str, dict[str, Recipe]] = {}
        # * collection -> dimension
        # derived from familytree
        self.ancestry = {
            collection: dimension for dimension, collection in self.familytree.values()
        }
        # * collection to component
        # derived from familytree
        self.ilk = {
            collection: component
            for component, (_, collection) in self.familytree.items()
        }

        # --------------------------------------------------------------------
        # * Constraint Ledger
        # --------------------------------------------------------------------

        # Dictionary which tells you what aspects of resource
        # have been set in what location and time

        # * General Resource Balances
        self.balances: BalanceType = defaultdict(
            lambda: defaultdict(lambda: defaultdict(list)),
        )
        # Dictionary which tells you what aspects of what component
        # have been bound at what location and time

        # * Sample Dispositions
        self.dispositions: dict[
            Aspect,
            dict[
                Commodity | Process | Storage | Transport,
                dict[Location | Linkage, dict[Periods, list[Aspect]]],
            ],
        ] = {}

        # * Drawn Maps
        self.maps: dict[Aspect, dict[str, dict[Domain, list[Domain]]]] = {}
        self.maps_report: dict[Aspect, dict[str, dict[Domain, list[Domain]]]] = {}

        # * Generated Modes
        self.modes_dict: dict[Sample, Modes] = {}

        # * Conversion Matrix
        self.convmatrix: dict[Process, dict[Resource, int | float | list]] = {}

        # --------------------------------------------------------------------
        # * Measurement Related
        # --------------------------------------------------------------------
        self.units: list[Unit] = []
        # if SI units have been set
        self.siunits_set: bool = False

        # --------------------------------------------------------------------
        # * Model Classification
        # --------------------------------------------------------------------
        self.classifiers: dict[str, list[Enum]] = {
            "uncertainty": [],
            "structure": [],
            "scale": [],
            "paradigm": [],
        }

        # --------------------------------------------------------------------
        # * Model Initialization
        # --------------------------------------------------------------------
        self.init = list(self.init) if self.init is not None else []

        if self.default:
            self.init += [
                # Recipes
                capacity_sizing,
                operating,
                inventory_sizing,
                free_movement,
                trade,
                economic,
                environmental,
                social,
                usage,
                aspect_aliases,
                # Instructions
                costing_operation,
                costing_commodity,
            ]

        for func in self.init:
            func(self)

    # -------------------------------------------------------------------
    # * Active Representation
    # -------------------------------------------------------------------
    @property
    def problem(self) -> Problem:
        """The active problem."""
        return self.problems[-1]

    @property
    def graph(self) -> Graph:
        """Return the active model graph."""
        return self.graphs[-1]

    @property
    def program(self) -> Program:
        """The active program."""
        return self.programs[-1]

    @property
    def scenario(self) -> Scenario:
        """The active scenario."""
        return self.scenarios[-1]

    @property
    def game(self) -> Game:
        """The active game."""
        return self.games[-1]

    # -------------------------------------------------------------------
    # * Dimensional Properties and Collections
    # -------------------------------------------------------------------

    @property
    def horizon(self) -> Periods:
        """Time horizon."""
        return self.time.horizon

    @property
    def network(self) -> Location:
        """Encompassing Location."""
        return self.space.network

    @property
    def indicators(self) -> list[Environ | Social | Economic]:
        """Impact indicators."""
        return self.impact.indicators

    @property
    def operations(self) -> list[Process | Storage | Transport]:
        """System operations."""
        return self.system.operations

    @property
    def aspects(self) -> list[Consequence | Stream | Control | State]:
        """Problem aspects."""
        return self.problem.aspects

    @property
    def domains(self) -> list[Domain]:
        """Problem domains."""
        return self.problem.domains

    # -------------------------------------------------------------------
    # * Onboard Component and Send to Family
    # -------------------------------------------------------------------

    def update(
        self,
        name: str,
        value: _X,
        represent: str,
        collection: str,
        aspects: list[str] | None = None,
    ):
        """
        Update the Model with a new value.

        :param name: Name of the value to be added
        :type name: str
        :param value: Value to be added
        :type value: X
        :param represent: Representation to which the value belongs
        :type represent: str
        :param collection: Collection within the representation to which the value belongs
        :type collection: str
        :param aspects: Retained for compatibility with callers using this keyword.
        :type aspects: list[str], optional
        """
        del aspects  # Retained for callers of the original signature.
        value.name = name
        # every component is handed the model
        value.model = self

        if name in self.added:
            # do not allow overriding of components
            # throw error if name already exists
            message = f"{name} already defined"
            raise AttributeError(message)
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
            "locations",
            "linkages",
        ]:
            setattr(
                self.program,
                collection,
                getattr(self.program, collection) | value.I,
            )

        # # set aspect samples on the components
        # if aspects:
        #     for asp in aspects:
        #         aspect = getattr(self, asp)

        #         setattr(value, asp, aspect(value))

        #         if aspect.neg is not None:
        #             setattr(value, aspect.neg.name, aspect.neg(value))

    # -------------------------------------------------------------------
    # * Birthing Procedures and Setting Aliases
    # -------------------------------------------------------------------
    # These take an action on attribute inputs

    def Recipe(
        self,
        name: str,
        kind: type[Aspect],
        primary_type: tuple[type[_Component]] | type[_Component],
        label: str = "",
        latex: str = "",
        add: str = "",
        add_latex: str = "",
        add_kind: type[Aspect] | None = None,
        sub: str = "",
        sub_latex: str = "",
        sub_kind: type[Aspect] | None = None,
        neg: str = "",
        neg_latex: str = "",
        neg_label: str = "",
        bound: str = "",
        ispos: bool = True,
        nn: bool = True,
        use_multiplier: bool = False,
    ):
        """
        Creates a Recipe and updates recipes.

        :param name: Name of the aspect
        :type name: str
        :param kind: type of the aspect
        :type kind: type[Aspect]
        :param primary_type: type of primary component
        :type primary_type: tuple[type[_Component]] | type[_Component]
        :param label: label for the aspect. Defaults to ''.
        :type label: str, optional
        :param latex: LaTeX representation for the aspect. Defaults to None.
        :type latex: str, optional
        :param add: add control variable. Defaults to ''.
        :type add: str, optional
        :param add_latex: LaTeX representation for the add aspect. Defaults to ''.
        :type add_latex: str, optional
        :param add_kind: type of the add aspect. Defaults to None.
        :type add_kind: type[Aspect], optional
        :param sub: sub control variable. Defaults to ''.
        :type sub: str, optional
        :param sub_latex: LaTeX representation for the sub aspect. Defaults to ''.
        :type sub_latex: str, optional
        :param sub_kind: type of the sub aspect. Defaults to None.
        :type sub_kind: type[Aspect], optional
        :param neg: name of the negative aspect. Defaults to ''.
        :type neg: str, optional
        :param neg_latex: LaTeX representation for the negative aspect. Defaults to ''.
        :type neg_latex: str, optional
        :param neg_label: label for the negative aspect. Defaults to ''.
        :type neg_label: str, optional
        :param bound: name of the bound aspect. Defaults to ''.
        :type bound: str, optional
        :param ispos: whether the aspect is positive. Defaults to True.
        :type ispos: bool, optional
        :param nn: whether the aspect is non-negative. Defaults to True.
        :type nn: bool, optional
        :param use_multiplier: Use a scaler (such as distance) for calculations
        :type use_multiplier: bool
        """
        if name in self.cookbook:
            logger.warning("⛔ Overriding existing recipe: %s ⛔", name)

        self.cookbook[name] = Recipe(
            name=name,
            kind=kind,
            label=label or name,
            add=add,
            sub=sub,
            bound=bound,
            ispos=ispos,
            nn=nn,
            latex=latex,
            use_multiplier=use_multiplier,
            primary_type=primary_type,
        )

        def register_control(
            child: str,
            preferred: type[Aspect] | None,
            fallback: type[Aspect] | None,
            child_label: str,
            *,
            positive: bool,
        ) -> None:
            if child:
                self.Recipe(
                    name=child,
                    kind=preferred or fallback or Control,
                    label=child_label or child,
                    ispos=positive,
                    nn=True,
                    latex=latex or child,
                    primary_type=primary_type,
                )

        register_control(add, add_kind, sub_kind, add_latex, positive=True)
        register_control(sub, sub_kind, add_kind, sub_latex, positive=False)

        if neg:
            neg_recipe = Recipe(
                name=neg,
                kind=kind,
                label=neg_label,
                ispos=not ispos,
                nn=nn,
                latex=neg_latex or neg,
                use_multiplier=use_multiplier,
                primary_type=primary_type,
            )
            self.cookbook[neg] = neg_recipe

    def alias(self, *names: str, of: str):
        """
        Set aspect aliases.

        :param names: Names of the aliases
        :type names: str
        :param to: Name of the aspect to which the aliases point
        :type to: str

        .. admonition:: Example

            .. code-block:: python

                from energia import Model

                m = Model()
                m.alias("installed", of="capacity")
                assert m.installed is m.capacity
        """
        recipe = self.cookbook[of]
        self.directory = {**self.directory, **{name: {of: recipe} for name in names}}

    def Instruction(
        self,
        name: str,
        kind: type[_Component],
        deciding: str,
        depending: str,
        default: str,
        label: str = "",
        latex: str = "",
    ):
        """
        Creates an Instruction and updates the manual.

        :param deciding: Name of the deciding aspect
        :type deciding: str
        :param depending: Name of the depending aspect
        :type depending: str
        :param default: Name of the default component
        :type default: str
        :param label: Label for the parameter. Defaults to ''.
        :type label: str, optional
        :param latex: LaTeX representation for the parameter. Defaults to ''.
        :type latex: str, optional
        """
        self.manual[name] = Instruction(
            name=name,
            kind=kind,
            deciding=deciding,
            depending=depending,
            default=default,
            label=label,
            latex=latex,
        )

    # ------------------------------------------------------------------------
    # * Easy Birthing of Components
    # ------------------------------------------------------------------------

    def declare(self, what: type[_X], names: list[str]):
        """
        Declares objects conveniently.

        :param what: Type of object to be created
        :type what: type[X]
        :param names: Names of the objects to be created
        :type names: list[str]
        """
        for i in names:
            setattr(self, i, what())

    def Link(
        self,
        source: Location,
        sink: Location,
        dist: float = 0,
        bi: bool = False,
    ):
        """
        Link two Locations.

        :param source: Source Location
        :type source: Location
        :param sink: Sink Location
        :type sink: Location
        :param dist: Distance between the Locations. Defaults to None.
        :type dist: float | Unit, optional
        :param bi: Whether the linkage is bidirectional. Defaults to False.
        :type bi: bool, optional
        """
        if source - sink:
            # if source and sink are already linked
            message = (
                f"A link already defined between {source} and {sink}.\n"
                "For multiple linkages with different attributes, use model.named_link = Link(...)"
            )
            raise ValueError(message)

        link = Linkage(source=source, sink=sink, dist=dist, bi=bi, auto=True)
        setattr(self, f"{source.name}-{sink.name}", link)

    def TemporalScales(self, discretizations: list[int], names: list[str]):
        """
        Register a hierarchy of named time scales on the model.

        :param discretizations: List of discretizations for the temporal scale.
        :type discretizations: list[int]
        :param names: Names of the discretizations. Defaults to [t<i>] for each discretization.
        :type names: list[str], optional
        """
        # set the root periods
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

    def Modes(self, size: int, sample: Sample):
        """
        Create operating modes for a sample on its time scale.

        :param size: Number of modes to create
        :type size: int
        :param sample: Decision sample to which the modes belong.
        :type sample: Sample

        .. admonition:: Example

            .. code-block:: python

                from energia import Model, Process

                m = Model()
                m.boiler = Process()
                load = m.Modes(size=2, sample=m.boiler.operate)
                assert len(load) == 2
                assert load[0].parent is load
        """
        modes = Modes(size=size, sample=sample, n=len(self.modes))
        periods = sample.domain.periods or self.time.horizon
        setattr(self, f"_{periods}{len(periods.modes)}", modes)
        periods.modes.append(modes)
        return modes

    # ------------------------------------------------------------------------
    # * Illustrations from Different Perspectives
    # ------------------------------------------------------------------------

    # * I Mathematical
    def show(
        self,
        descriptive: bool = False,
        categorical: bool = True,
        category: str = "",
    ):
        """
        Pretty print the Model.

        :param descriptive: Whether to show descriptive information. Defaults to False.
        :type descriptive: bool, optional
        :param categorical: Whether to group by category. Defaults to True.
        :type categorical: bool, optional
        :param category: If provided, shows only this category. Defaults to None.
        :type category: str, optional
        """
        self.program.show(descriptive, categorical=categorical, category=category)

    # * II Graphical
    def draw(self, variable: Aspect | Sample | None = None, n_sol: int = 0):
        """
        Draw the solution for a variable.

        :param variable: Variable to draw. Defaults to None.
        :type variable: Aspect | Sample | None, optional
        :param n_sol: Solution number to draw. Defaults to 0.
        :type n_sol: int, optional
        """
        if variable is not None:
            self.program.draw(variable=variable.V(), n_sol=n_sol)

        else:
            self.program.draw(n_sol=n_sol)

    # * III Solution
    def output(self, n_sol: int = 0, slack: bool = True, compare: bool = False):
        """
        Display a solution's objective and variable values.

        :param n_sol: Index of the solution to display.
        :param slack: Retained for compatibility. Has no effect on the display.
        :param compare: Compare variable values across solutions.
        """
        del slack  # Display options are handled by Gana.
        return self.program.output(n_sol=n_sol, compare=compare)

    # ------------------------------------------------------------------------
    # * Solution Prep, Generation, and  Handling
    # ------------------------------------------------------------------------
    def locate(self, *operations: Process | Storage):
        """
        Locate operations in the network.

        :param operations: Operations to locate
        :type operations: Process | Storage
        """
        self.network.locate(*operations)

    # * Optimization
    def solve(
        self,
        using: Literal[
            "combinatorial",
            "combinatorial_parallel",
            "combinatorial_parallel_exp",
            "graph",
            "graph_exp",
            "graph_parallel",
            "graph_parallel_exp",
            "combinatorial_graph",
            "geometric",
            "geometric_parallel",
            "geometric_parallel_exp",
        ] = "combinatorial",
    ):
        """
        Solve the multiparametric program.

        :param using: The solving method to use. Defaults to "combinatorial".
        :type using: Literal

        .. admonition:: Example

            .. code-block:: python

                from math import isclose
                from energia import Model, Resource

                m = Model()
                m.labor = Resource(take=True, price=(7.86, 8.89))
                m.labor.release == 2
                m.cash.spend.obj()
                m.solve()
                cost = m.eval(8.375)[m.cash.spend.V()[0]]
                assert isclose(cost, 16.75)
        """
        self.program.solve(using=using)

    # * Solution evaluation
    def eval(
        self,
        *theta_vals: float,
        n_sol: int = 0,
        roundoff: int = 4,
    ) -> dict[V, float]:
        """
        Evaluate the model variables at given theta values.

        :param theta_vals: values for the parametric variables
        :type theta_vals: float
        :param n_sol: solution number to evaluate, defaults to 0
        :type n_sol: int, optional
        :param roundoff: number of decimal places to round off to, defaults to 4
        :type roundoff: int, optional

        :return: evaluated values keyed by model variable
        :rtype: dict[V, float]
        """
        return self.program.eval(*theta_vals, n_sol=n_sol, roundoff=roundoff)

    # * Saving
    def save(
        self,
        as_type: str = "dill",
        *,
        path: str | os.PathLike[str] | None = None,
        n_sol: int | None = None,
    ) -> None:
        """
        Save a solver result atomically as ``.energia`` or deterministic JSON.

        Use ``model.program.import_solution(path)`` to attach a JSON result
        to a rebuilt model with the same formulation.

        :param as_type: ``"dill"`` (default) or ``"json"`` for deterministic results.
        :param path: Destination file in an existing directory.
            Defaults to ``<model name>.energia`` or ``<model name>.json``
            in the current directory. JSON destinations require a ``.json`` suffix.
        :param n_sol: Zero-based solution index. Defaults to the latest result.
        :raises ValueError: If the format is unsupported or Gana cannot export
            the selected result to the JSON destination.
        :raises RuntimeError: If the program has no solver results.
        :raises KeyError: If the requested index is absent from the solved program.
        """
        if as_type not in ("dill", "json"):
            message = f"Unknown type {as_type} for saving the model"
            raise ValueError(message)

        program = self.program
        if not program.solutions:
            message = "Solve the model before saving a solution"
            raise RuntimeError(message)
        solution = program.solution if n_sol is None else program.solutions[n_sol]

        suffix = ".json" if as_type == "json" else ".energia"
        destination = Path(f"{self.name}{suffix}" if path is None else path).absolute()
        if as_type == "json":
            program.export_solution(destination, n_sol=n_sol)
            return

        with NamedTemporaryFile(
            mode="wb",
            dir=destination.parent,
            delete_on_close=False,
        ) as file:
            dump(solution, file)
            file.flush()
            os.fsync(file.fileno())
            file.close()  # Close before replacing the destination on Windows.
            Path(file.name).replace(destination)

    # ------------------------------------------------------------------------
    # * Default Components
    # ------------------------------------------------------------------------

    def _t0(self, size: int = 1) -> Periods:
        """
        Return a default period.

        :param size: Size of the period. Defaults to 0.
        :type size: int, optional

        :return: Periods object
        :rtype: Periods
        """
        periods = self.periods

        if not periods:
            if size > 1:
                self.t1 = Periods()
                self.t0 = size * self.t1
                return self.t1

        if size > 1:
            setattr(self, f"t{len(periods)}", self.horizon / size)
            return periods[-1]

        self.t0 = Periods()
        return self.t0

    def _l0(self) -> Location:
        """Return a default location."""
        self.l0 = Location(label="l")
        return self.l0

    def _cash(self) -> Currency:
        """Return a default currency."""
        currencies = self.currencies
        if currencies:
            return currencies[0]
        self.cash = Currency(label="$")
        return self.cash

    # -------------------------------------------------------------------
    # * Attribute Setting and Getting
    # -------------------------------------------------------------------

    def __setattr__(self, name: str, value: Any) -> None:
        """Register model components and assign their attributes."""
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
        for cls, updates in self.familytree.items():
            if isinstance(value, cls):
                # for args in updates:
                self.update(name, value, *updates)
                break

        # Special linkage instructions
        if isinstance(value, Linkage):
            self.space.sources.append(value.source)
            self.space.sinks.append(value.sink)

            if value.bi:
                # if bidirectional, set the reverse linkage
                # also ensures that all linakges go in one direction only
                rev = value.rev()
                setattr(self, rev.name, rev)

        super().__setattr__(name, value)

    def __getattr__(self, name):
        """Resolve default components, model collections, and attributes of the underlying program."""
        # Only called when attribute does not exist

        # if something like t, t0 is called
        # just return a default component
        # t/t0, l/l0, cash, money
        # this will not intefere with the setting of
        # attributes what this name
        if name in self.default_components:
            return self.default_components[name]()

        # Inherits collections based on ancestry
        if name in self.ancestry:
            dimension = getattr(self, self.ancestry[name])
            collection = getattr(dimension, name)
            setattr(self, name, collection)
            return collection

        # Program attributes
        if name in self.program_attrs:
            collection = getattr(self.program, name)
            setattr(self, name, collection)
            return collection

        # properties from dimensions and representations
        if name in self.properties:
            return getattr(self.properties[name], name)

        return self._resolve_aspect(name)

    def _resolve_aspect(self, name):
        """Look up a registered aspect or create it from its recipe."""
        # already declared and mapped to an aspect
        if name in self.registry:
            return self.registry[name]

        if name in self.manual:
            return self.manual[name]

        # Recipe for defining aspects
        if name in self.cookbook:
            recipe = self.cookbook[name]

            aspect = recipe.kind(**recipe.args)
            setattr(self, name, aspect)

            return aspect
        # maps many attribute names to aspects
        if name in self.directory:
            # if this is an attribute being called for the first time
            recipes = self.directory[name]
            aspect_name = next(iter(recipes))

            if aspect_name in self.added:
                # if same aspect is called by a different name
                return getattr(self, aspect_name)

            # these are the arguments for the aspect
            recipe = recipes[aspect_name]
            aspect = recipe.kind(**recipe.args)

            setattr(self, aspect_name, aspect)

            self.registry[name] = aspect

            return aspect

        message = f"{self} has no '{name}'"
        raise AttributeError(message)

    # ---------------------------------------------------------------
    # * Call to Initialize using functions and Hashing
    # ---------------------------------------------------------------

    def __call__(self, *funcs: Callable[[Model], object]):
        """
        Set functions on the model.

        These can include default units
        """
        for f in funcs:
            f(self)

    def __str__(self):
        """Return the model's assigned name."""
        return self.name

    def __repr__(self):
        """Return the model's assigned name."""
        return self.name

    def __hash__(self):
        """Hash the model name."""
        return hash(self.name)
