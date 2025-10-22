"""A Model"""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Self, Type

from dill import dump
from ppopt.mplp_program import MPLP_Program
from ppopt.solution import Solution as MPSolution

from .._core._x import _X
from ..components.commodity.currency import Currency
from ..components.commodity.emission import Emission
from ..components.commodity.land import Land
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.game.couple import Interact
from ..components.game.player import Player
from ..components.graph.edge import Edge
from ..components.graph.node import Node
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
from ..dimensions.impact import Impact
from ..dimensions.problem import Problem
from ..dimensions.space import Space
from ..dimensions.system import System
from ..dimensions.time import Time
from ..library.aliases import aspect_aliases
from ..library.instructions import costing_operation
from ..library.recipes import (capacity_sizing, economic, environmental,
                               free_movement, inventory_sizing, operating,
                               social, trade, usage)
from ..modeling.parameters.conversion import Conversion
from ..modeling.parameters.instruction import Instruction
from ..modeling.variables.control import Control
from ..modeling.variables.recipe import Recipe
from ..modeling.variables.states import Consequence, State, Stream
from .ations.graph import Graph
from .ations.program import Program

logger = logging.getLogger("energia")
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


if TYPE_CHECKING:
    from enum import Enum
    from typing import DefaultDict

    from gana.block.solution import Solution
    from gurobipy import Model as GPModel

    from .._core._commodity import _Commodity
    from .._core._component import _Component
    from ..modeling.indices.domain import Domain
    from ..modeling.variables.aspect import Aspect
    from ..modeling.variables.sample import Sample

    GRBType = DefaultDict[
        _Commodity,
        DefaultDict[Location | Linkage, DefaultDict[Periods, list[Aspect]]],
    ]


@dataclass
class Model:
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
    :vartype grb: DefaultDict[_Commodity,DefaultDict[Location | Linkage, DefaultDict[Periods, list[Aspect]]]]
    :ivar dispositions: Dictionary which tells you what aspects of what component have been bound at what location and time.
    :vartype dispositions: dict[Aspect, dict[_Commodity | Process | Storage | Transport, dict[Location | Linkage, dict[Periods, list[Aspect]]]]]
    :ivar maps: Maps of aspects to domains.
    :vartype maps: dict[Aspect, dict[Domain, dict[str, list[Domain]]]]
    :ivar maps_report: Maps of aspects to domains for reporting variables.
    :vartype maps_report: dict[Aspect, dict[Domain, dict[str, list[Domain]]]]


    :raises ValueError: If an attribute name already exists in the Model.
    """

    name: str = "m"
    init: list[Callable[Self]] | None = None
    default: bool = True
    capacitate: bool = False

    def __post_init__(self):

        # what components have been added to the model
        self.added: list[str] = []
        # map of what representation and collection within that representation
        # an object of a particular type belongs to

        # --------------------------------------------------------------------
        # Component Mapping to Dimension and Collection 
        # --------------------------------------------------------------------
        #Dimensions in brackets
        self.familytree = {            
            # * I Temporal (Time):
            # 1.  Periods (Periods) generates a bespoke discretization.
            Periods: ("time", "periods"),
            # 2. Modes discrete options in the same time 
            Modes: ("time", "modes"),
            # * II Spatial (Space):
            # 1. Spatial representation (Space). Location (Loc) generate a bespoke discretization.
            Location: ("space", "locations"),
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
            Environ: (
                "impact",
                "environment",
            ),
            Social: (
                "impact",
                "society",
            ),
            Economic: ("impact", "economy"),
            # * VI Game Components
            # To model Competition
            Player: ("game", "players"),
            Interact: ("game", "interacts"),
            # * VII Problem Aspects
            # The problem at hand
            #1. to control the volume of streams
            Control: ("problem", "controls"),
            #2. movement
            Stream: ("problem", "streams"),
            #3. size, quantity
            State: ("problem", "states"),
            #4. consequence
            Consequence: ("problem", "consequences"),
        }

        # 
        self.ancestry = {
            collection: dimension for dimension, collection in self.familytree.values()
        }

        # Temporal Scope
        self.time = Time(self)
        # Spatial Scope
        self.space = Space(self)        
        # Impact on the exterior
        self.impact = Impact(self)
        # System (Resource Task Network)
        self.system = System(self)
        # Graph (Network)
        self.graph = Graph(self)
        # the problem
        self.problem = Problem(self)
        # mathematical program
        self.program = Program(model=self)
        # shorthand
        self._ = self.program

        # Start with patterened
        self.program_attrs =    [ 
            "constraint",
            "function",
            "variable",
            "parameter",
            "theta",
        ]
        # word -> words and word_sets
        self.program_attrs += [w + s for w in self.program_attrs for s in ['s', '_sets']]
        self.program_attrs += ["solution", "formulation",  "evaluation"]
        # word -> n_word
        self.program_attrs += ['n_' + w for w in self.program_attrs]
        self.program_attrs += ["index_sets", "indices", "objectives", "parameter_sets", "X"]
        self.program_attrs = {i: self.program for i in  self.program_attrs}
        
        # properties that can be called by model
        # these never get set
        _program_matrices = [ "A","B","C","F","G","H","CrA","CrB","NN","A_with_NN","B_with_NN","Z","P",]
        self.properties = {
            "horizon": self.time, 
            "network": self.space,
            "indicators": self.impact, 
            "operations": self.system, 
            "aspects": self.problem,
            "domains": self.problem,
            **{i: self.program for i in _program_matrices},
        }

        # if any of these attributes are called,
        # or an exiting one is returned
        self.default_components = {
            "l": self._l0,
            "l0": self._l0,
            "t0": self._t0,
            "t": self._t0,
            "money": self._cash,
        }

        self.graph_components = ["edges", "nodes"]

        # -----------------------------------------------
        #  Books
        # -----------------------------------------------
        # Maps between:

        # user_input_attr -> matching_aspect -> Recipe
        self.directory: dict[str, dict[str, Recipe]] = {}
        # already_defined_user_input_attr -> matching_aspect
        self.registry: dict[str, Aspect] = {}
        # matching_aspect -> Recipe
        self.cookbook: dict[str, Recipe] = {}
        # parameter_name -> parameter_handling_instruction
        self.manual: dict[str, Instruction] = {}

        # measuring units
        self.units: list[Unit] = []
        # if SI units have been set
        self.siunits_set: bool = False

        self.convmatrix: dict[Process, dict[Resource, int | float | list]] = {}
        self.modes_dict: dict[Sample, Modes] = {}

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
                aspect_aliases,
                costing_operation,
            ]

        for func in self.init:
            func(self)

        self.classifiers: dict[str, list[Enum]] = {
            "uncertainty": [],
            "structure": [],
            "scale": [],
            "paradigm": [],
        }

        # Dictionary which tells you what aspects of resource
        # have been set in what location and time
        self.grb: dict[
            _Commodity,
            dict[Location | Linkage, dict[Periods, list[Aspect]]],
        ] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        # Dictionary which tells you what aspects of what component
        # have been bound at what location and time
        self.dispositions: dict[
            Aspect,
            dict[
                _Commodity | Process | Storage | Transport,
                dict[Location | Linkage, dict[Periods, list[Aspect]]],
            ],
        ] = {}

        self.maps: dict[Aspect, dict[Domain, dict[str, list[Domain]]]] = {}
        self.maps_report: dict[Aspect, dict[Domain, dict[str, list[Domain]]]] = {}


    # -----------------------------------------------------
    #              Set Component
    # -----------------------------------------------------

    def update(
        self,
        name: str,
        value: _X,
        represent: str,
        collection: str,
        aspects: list[str] | None = None,
    ):
        """Update the Model with a new value

        :param name: Name of the value to be added
        :type name: str
        :param value: Value to be added
        :type value: X
        :param represent: Representation to which the value belongs
        :type represent: str
        :param collection: Collection within the representation to which the value belongs
        :type collection: str
        :param aspects: Aspects to be added to the value, defaults to None
        :type aspects: list[str], optional
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
            "locations",
            "linkages",
        ]:
            setattr(
                self.program, collection, getattr(self.program, collection) | value.I
            )

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
        # Only called when attribute does not exist

        # if something like t, t0 is called
        # just return a default component
        # t/t0, l/l0, cash, money
        # this will not intefere with the setting of 
        # attributes what this name
        if name in self.default_components:
            component = self.default_components[name]()
            return component

        # 
        if name in self.ancestry:
            dimension = getattr(self, self.ancestry[name])
            collection = getattr(dimension, name)
            setattr(self, name, collection)
            return collection

        if name in self.program_attrs:
            collection = getattr(self.program_attrs[name], name)
            setattr(self, name, collection)
            return collection

        if name in self.registry:
            # if attribute has been called before
            # the next time the created attribute is returned
            return self.registry[name]

        if name in self.cookbook:
            recipe = self.cookbook[name]

            aspect = recipe.kind(**recipe.args)
            setattr(self, name, aspect)

            return aspect

        if name in self.properties:
            return getattr(self.properties[name], name)


        if name in self.manual:
            return self.manual[name]

        if name in self.directory:
            # if this is an attribute being called for the first time
            recipe = self.directory[name]
            aspect_name = list(recipe.keys())[0]

            if aspect_name in self.added:
                # if same aspect is called by a different name
                return getattr(self, aspect_name)

            # these are the arguments for the aspect
            recipe = recipe[aspect_name]
            aspect = recipe.kind(**recipe.args)

            setattr(self, aspect_name, aspect)

            self.registry[name] = aspect

            return aspect

        raise AttributeError(
            f"{self} has no '{name}'",
        )

    def aliases(self, *names: str, to: str):
        """Set aspect aliases

        :param names: Names of the aliases
        :type names: str
        :param to: Name of the aspect to which the aliases point
        :type to: str
        """
        _add = dict.fromkeys(list(names), {to: self.cookbook[to]})
        self.directory = {**self.directory, **_add}

    def Recipe(
        self,
        name: str,
        kind: Type[Aspect],
        primary_type: tuple[Type[_Component]] | Type[_Component],
        label: str = "",
        latex: str = "",
        add: str = "",
        add_latex: str = "",
        add_kind: Type[Aspect] | None = None,
        sub: str = "",
        sub_latex: str = "",
        sub_kind: Type[Aspect] | None = None,
        neg: str = "",
        neg_latex: str = "",
        neg_label: str = "",
        bound: str = "",
        ispos: bool = True,
        nn: bool = True,
    ):
        """Creates a Recipe and updates recipes

        :param name: Name of the aspect
        :type name: str
        :param kind: type of the aspect
        :type kind: Type[Aspect]
        :param primary_type: type of primary component
        :type primary_type: tuple[Type[_Component]] | Type[_Component]
        :param label: label for the aspect. Defaults to ''.
        :type label: str, optional
        :param latex: LaTeX representation for the aspect. Defaults to None.
        :type latex: str, optional
        :param add: add control variable. Defaults to ''.
        :type add: str, optional
        :param add_latex: LaTeX representation for the add aspect. Defaults to ''.
        :type add_latex: str, optional
        :param add_kind: type of the add aspect. Defaults to None.
        :type add_kind: Type[Aspect], optional
        :param sub: sub control variable. Defaults to ''.
        :type sub: str, optional
        :param sub_latex: LaTeX representation for the sub aspect. Defaults to ''.
        :type sub_latex: str, optional
        :param sub_kind: type of the sub aspect. Defaults to None.
        :type sub_kind: Type[Aspect], optional
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
        """
        if name in self.cookbook:
            logger.warning("Overriding existing recipe: %s", name)

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

    def Instruction(
        self,
        name: str,
        kind: Type[_Component],
        deciding: str,
        depending: str,
        default: str,
        label: str = "",
    ):
        """Creates an Instruction and updates the manual

        :param deciding: Name of the deciding aspect
        :type deciding: str
        :param depending: Name of the depending aspect
        :type depending: str
        :param default: Name of the default component
        :type default: str
        :param label: Label for the parameter. Defaults to ''.
        :type label: str, optional
        :param citations: Captions for the parameter. Defaults to ''.
        :type citations: str, optional
        """

        self.manual[name] = Instruction(
            name=name,
            kind=kind,
            deciding=deciding,
            depending=depending,
            default=default,
            label=label,
        )

    # -----------------------------------------------------
    #              Birth Component
    # -----------------------------------------------------

    def declare(self, what: Type[_X], names: list[str]):
        """Declares objects conveniently

        :param what: Type of object to be created
        :type what: Type[X]
        :param names: Names of the objects to be created
        :type names: list[str]
        """
        for i in names:
            setattr(self, i, what())

    def Link(
        self,
        source: Location,
        sink: Location,
        dist: float | Unit = 0,
        bi: bool = False,
    ):
        """
        Link two Locations

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
        category: str = "",
    ):
        """
        Pretty print the Model

        :param descriptive: Whether to show descriptive information. Defaults to False.
        :type descriptive: bool, optional
        :param categorical: Whether to group by category. Defaults to True.
        :type categorical: bool, optional
        :param category: If provided, shows only this category. Defaults to None.
        :type category: str, optional
        """
        self.program.show(descriptive, categorical=categorical, category=category)

    def sol(self, n_sol: int = 0, slack: bool = True, compare: bool = False):
        """Solution"""
        return self.program.sol(n_sol=n_sol, slack=slack, compare=compare)

    def eval(
        self, *theta_vals: float, n_sol: int = 0, roundoff: int = 4
    ) -> list[float]:
        """
        Evaluate the objective function at given theta values

        :param theta_vals: values for the parametric variables
        :type theta_vals: float
        :param n_sol: solution number to evaluate, defaults to 0
        :type n_sol: int, optional
        :param roundoff: number of decimal places to round off to, defaults to 4
        :type roundoff: int, optional

        :return: list of objective function values
        :rtype: list[float]
        """
        return self.program.eval(*theta_vals, n_sol=n_sol, roundoff=roundoff)

    def save(self, as_type: str = "dill"):
        """Save the Model to a file"""
        if as_type == "dill":
            with open(self.name + ".energia", "wb") as f:
                dump(self.solution, f)
        else:
            raise ValueError(f"Unknown type {as_type} for saving the model")

    def draw(self, variable: Aspect | Sample | None = None, n_sol: int = 0):
        """
        Draw the solution for a variable

        :param variable: Variable to draw. Defaults to None.
        :type variable: Aspect | Sample | None, optional
        :param n_sol: Solution number to draw. Defaults to 0.
        :type n_sol: int, optional

        """
        if variable is not None:
            self.program.draw(variable=variable.V(), n_sol=n_sol)

        else:
            self.program.draw(n_sol=n_sol)
    
    def _t0(self, size: int = 0) -> Periods:
        """Return a default period

        :param size: Size of the period. Defaults to 0.
        :type size: int, optional

        :return: Periods object
        :rtype: Periods
        """

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

    def _l0(self) -> Location:
        """Return a default location"""
        self.l0 = Location(label="l")
        return self.l0

    def _cash(self) -> Currency:
        """Return a default currency"""
        if self.currencies:
            return self.currencies[0]
        self.cash = Currency(label="$")
        return self.cash

    def locate(self, *operations: Process | Storage):
        """Locate operations in the network

        :param operations: Operations to locate
        :type operations: Process | Storage
        """
        self.network.locate(*operations)

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
        Solve the multiparametric program

        :param using: The solving method to use. Defaults to "combinatorial".
        :type using: Literal[
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
        ], optional
        """

        self.program.solve(using=using)

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
