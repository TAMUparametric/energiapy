"""Blocks of the Model"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from ..components.commodity.misc import Cash, Emission, Land, Material
from ..components.impact.indicator import Indicator
from ..components.commodity.resource import Resource
from ..components.operation.transport import Transport
from ..dimensions.consequence import Consequence
from ..dimensions.decisiontree import DecisionTree
from ..dimensions.space import Space
from ..dimensions.system import System
from ..dimensions.time import Time
from .graph import Graph
from .program import Program

if TYPE_CHECKING:
    from gana.block.solution import Solution
    from gana.sets.constraint import C
    from gana.sets.parameter import P
    from gana.sets.theta import T
    from gana.sets.variable import V
    from pandas import DataFrame

    from ..components.game.player import Player
    from ..components.impact.categories import Economic, Environ, Social
    from ..components.operation.process import Process
    from ..components.operation.storage import Storage
    from ..components.spatial.linkage import Linkage
    from ..components.spatial.location import Location
    from ..components.temporal.period import Period
    from ..modeling.indices.domain import Domain
    from ..modeling.variables.aspect import Aspect
    from ..modeling.variables.control import Control
    from ..modeling.variables.impact import Impact
    from ..modeling.variables.state import State
    from ..modeling.variables.stream import Stream


@dataclass
class _Scope:
    """Defines the scope of the model"""

    # meshes of space and time to denote whether a constraint is written
    # general resource balance

    def __post_init__(self):

        # Temporal Scope
        self.time = Time(self)
        # Spatial Scope
        self.space = Space(self)

        # Dictionary which tells you what aspects of resource
        # have grb {loc: time: []} and {time: loc: []}
        self.grb: dict[
            Resource, dict[Location | Linkage, dict[Period, list[Aspect]]]
        ] = {}

        # Dictionary which tells you what aspects of what component
        # have been bound at what location and time
        self.dispositions: dict[
            Aspect,
            dict[
                Resource | Process | Storage | Transport,
                dict[Location | Linkage, dict[Period]],
            ],
        ] = {}

    @property
    def horizon(self) -> Period:
        """The horizon of the Model"""
        return self.time.horizon

    @property
    def network(self) -> Location:
        """The network of the Model"""
        return self.space.network

    def update_dispositions(
        self,
        aspect: Aspect,
        domain: Domain,
        # resource: Resource = None,
        # operation: Process | Storage | Transport = None,
        # space: Space = None,
        # time: Period = None,
    ):
        """Updates the spatiotemporal dispositions for an aspect pertaining to a component"""

        def merge_trees(d1, d2):
            """Recursively merge two tree-like dicts (values always dicts)."""
            result = dict(d1)  # shallow copy of d1
            for k, v in d2.items():
                if k in result:
                    result[k] = merge_trees(
                        result[k], v
                    )  # recurse since v must also be a dict
                else:
                    result[k] = v
            return result

        self.dispositions = merge_trees(self.dispositions, {aspect: domain.tree})

        # # indicator = domain.indicator
        # # resource = domain.resource
        # # operation = domain.operation
        # primary = domain.primary

        # binds = domain.binds

        # # dr_aspect = domain.dr_aspect
        # # dresource = domain.dresource
        # # op_aspect = domain.op_aspect
        # dm = domain.player or domain.couple

        # space = domain.space
        # time = domain.period

        # the base key, value combinations are of the form
        # 1. {aspect: resource: {}}
        # 2. {aspect: resource: {operation: {}}}
        # 3. {aspect: operation: {}}

        # ======== Commodities for the 0 the index

        # def update_aspect(aspect: Aspect):
        #     """Update aspect"""
        #     if not aspect in self.dispositions:
        #         self.dispositions[aspect] = {}

        # def update_primary(
        #     component: Resource | Indicator | Process | Storage | Transport,
        # ):
        #     """Update stream or operation"""
        #     if not component in self.dispositions[aspect]:
        #         self.dispositions[aspect][component] = {}

        # def update_space_time(
        #     dict_: (
        #         dict[Aspect, dict[Resource, set]]
        #         | dict[Aspect, dict[Resource, dict[Process | Storage | Transport, set]]]
        #         | dict[Aspect, dict[Process | Storage | Transport, set]]
        #     ),
        # ):
        #     """Updates the space and time dictionaries for the given base dictionary."""
        #     if not space in dict_:
        #         dict_[space] = set()

        #     if not time in dict_[space]:
        #         dict_[space].add(time)
        #     return dict_

        # def update_binds(
        #     binds: dict[Aspect, Resource | Process | Storage | Transport],
        # ):
        #     """Update component that influences primary stream or operation"""
        #     binds = list(binds.items())
        #     _dict = {binds[-1][0]: {binds[-1][1]: {}}}
        #     for k, v in reversed(binds[:-1]):
        #         _dict = {k: {v: _dict}}
        #     return _dict

        #     # self.dispositions[aspect][primary] =
        #     # return {
        #     #     **self.dispositions[aspect][primary],
        #     #     **_dict,
        #     # }

        # def update_dm(
        #     _dict: dict[
        #         Aspect, dict[Resource | Process | Storage | Transport, dict[Player]]
        #     ],
        #     player: Player,
        # ):
        #     """Update Player"""
        #     if not player in _dict:
        #         _dict[player] = {}
        #     return _dict

        #     # update_player(dm, component)

        # update_aspect(aspect)

        # update_primary(primary)

        # _dict = {}

        # if binds:
        #     _dict = update_binds(binds)

        # if dm:
        #     _dict = update_dm(_dict, dm)

        # self.dispositions[aspect][primary] = update_space_time(_dict)

    def update_grb(self, resource: Resource, space: Location | Linkage, time: Period):
        """Creates a mesh for grb dict"""

        if not resource in self.grb:
            # update resource if needed
            self.grb[resource] = {}

        if not space in self.grb[resource]:
            # update space if needed
            self.grb[resource][space] = {}

        if not time in self.grb[resource][space]:
            self.grb[resource][space][time] = []

    @property
    def periods(self) -> list[Period]:
        """The periods of the Model"""
        return self.time.periods

    @property
    def locs(self) -> list[Location]:
        """The Locations"""
        return self.space.locs

    @property
    def links(self) -> list[Linkage]:
        """The Links"""
        return self.space.links


@dataclass
class _Impact:
    """Defines the impact of the model"""

    def __post_init__(self):

        # Impact on the exterior
        self.impact = Consequence(self)

    @property
    def socs(self) -> list[Social]:
        """The Soc Variables"""
        return self.impact.socs

    @property
    def envs(self) -> list[Environ]:
        """The Env Variables"""
        return self.impact.envs

    @property
    def ecos(self) -> list[Economic]:
        """The Eco Variables"""
        return self.impact.ecos

    @property
    def indicators(self) -> list[Social | Environ | Economic]:
        """Indicators"""
        return self.impact.indicators


@dataclass
class _Tree:
    """Defines the feasible region of the model"""

    def __post_init__(self):
        # Tree (Feasible Region)
        self.tree = DecisionTree(self)

    @property
    def states(self) -> list[State]:
        """The State Variables"""
        return self.tree.states

    @property
    def controls(self) -> list[Control]:
        """The Control Variables"""
        return self.tree.controls

    @property
    def streams(self) -> list[Stream]:
        """The Stream Variables"""
        return self.tree.streams

    @property
    def impacts(self) -> list[Impact]:
        """The Impact Variables"""
        return self.tree.impacts

    @property
    def players(self) -> list[Player]:
        """The Players"""
        return self.tree.players

    @property
    def domains(self):
        """The domains of the Model"""
        return self.tree.domains

    def get(
        self,
        keys: Literal[
            'aspects', 'states', 'controls', 'streams', 'impacts', 'domains'
        ] = 'aspects',
        values: Literal[
            'aspects', 'states', 'controls', 'streams', 'impacts', 'domains'
        ] = 'domains',
    ) -> dict[
        State | Control | Stream | Impact | Domain,
        list[State | Control | Stream | Impact | Domain],
    ]:
        """Get a dictionary of the treewith a particular structure

        Args:
            keys (Literal[ 'aspects', 'states', 'controls', 'streams', 'impacts', 'domains' ], optional): Defaults to 'aspects'.
            values (Literal[ 'aspects', 'states', 'controls', 'streams', 'impacts', 'domains' ], optional): Defaults to 'domains'.

        Returns:
            dict[Variable | Domain, list[Variable | Domain]]: dictionary with particular structure
        """
        return self.tree.get(keys, values)


@dataclass
class _Graph:
    """Defines the network as a graph"""

    def __post_init__(self):
        # Graph (Network)
        self.graph = Graph(self)

    @property
    def edges(self) -> list[Linkage]:
        """The Edges"""
        return self.graph.edges

    @property
    def nodes(self) -> list[Location]:
        """The Nodes"""
        return self.graph.nodes


@dataclass
class _System:
    """Defines the system of the model"""

    def __post_init__(self):
        # System (Resource Task Network)
        self.system = System(self)

    @property
    def resources(self) -> list[Resource]:
        """The Resources"""
        return self.system.resources

    @property
    def lands(self) -> list[Land]:
        """The Lands"""
        return self.system.lands

    @property
    def materials(self) -> list[Material]:
        """The Materials"""
        return self.system.materials

    @property
    def currencies(self) -> list[Cash]:
        """The Currencies"""
        return self.system.currencies

    @property
    def emissions(self) -> list[Emission]:
        """The Emissions"""
        return self.system.emissions

    @property
    def processes(self) -> list[Process]:
        """The Processes"""
        return self.system.processes

    @property
    def storages(self) -> list[Storage]:
        """The Storages"""
        return self.system.storages

    @property
    def transits(self) -> list[Transport]:
        """The Transits"""
        return self.system.transits

    @property
    def operations(self) -> list[Process | Storage | Transport]:
        """The Operations"""
        return self.system.operations


@dataclass
class _Program:
    """Defines the mathematical program of the model"""

    def __post_init__(self):
        # mathematical (mixed integer) program
        self.program = Program(getattr(self, 'name'))

    @property
    def _(self):
        """gana program"""
        return self.program

    # -------------------------------------
    #            Sets
    # -------------------------------------

    @property
    def constraint_sets(self) -> list[C]:
        """Constraint sets"""
        return self.program.constraint_sets

    @property
    def function_sets(self) -> list[C]:
        """Function sets"""
        return self.program.function_sets

    @property
    def variable_sets(self) -> list[V]:
        """Variable sets"""
        return self.program.variable_sets

    @property
    def parameter_sets(self) -> list[P]:
        """Parameter sets"""
        return self.program.parameter_sets

    @property
    def theta_sets(self) -> list[T]:
        """Theta sets"""
        return self.program.theta_sets

    @property
    def index_sets(self) -> list[str]:
        """Index sets"""
        return self.program.index_sets

    # -------------------------------------
    #            Elements
    # -------------------------------------

    @property
    def constraints(self) -> list[C]:
        """Constraints"""
        return self.program.constraints

    @property
    def functions(self) -> list[C]:
        """Functions"""
        return self.program.functions

    @property
    def variables(self) -> list[V]:
        """Variables"""
        return self.program.variables

    @property
    def thetas(self) -> list[T]:
        """Thetas"""
        return self.program.thetas

    @property
    def indices(self) -> list[str]:
        """Indices"""
        return self.program.indices

    # -------------------------------------
    #            Ordered Lists
    # -------------------------------------

    def cons(self) -> list[C]:
        """Order list of constraints"""
        return self.program.cons()

    def contvars(self) -> list[V]:
        """Order list of continuous variables"""
        return self.program.contvars()

    def intvars(self) -> list[V]:
        """Order list of integer variables"""
        return self.program.intvars()

    def bnrvars(self) -> list[V]:
        """Order list of binary variables"""
        return self.program.bnrvars()

    # -------------------------------------
    #            Matrices
    # -------------------------------------

    @property
    def A(self) -> list[list[float]]:
        """Matrix A"""
        return self.program.A

    @property
    def B(self) -> list[float]:
        """Matrix B"""
        return self.program.B

    @property
    def C(self) -> list[float]:
        """Matrix C"""
        return self.program.C

    @property
    def X(self) -> list[list[int]]:
        """Structure of the constraint matrix"""
        return self.program.X

    @property
    def Z(self) -> list[list[int]]:
        """Structure of theta matrix"""
        return self.program.Z

    @property
    def G(self) -> list[list[int]]:
        """Matrix of Variable coefficients for type:

        g < = 0
        """
        return self.program.G

    @property
    def H(self) -> list[list[int]]:
        """Matrix of Variable coefficients for type:

        h == 0
        """
        return self.program.H

    @property
    def NN(self) -> list[list[int]]:
        """Matrix of Variable coefficients for non-negativity constraints"""
        return self.program.NN

    @property
    def CrA(self) -> list[list[float]]:
        """Critical Region A matrix:"""
        return self.program.CrA

    @property
    def CrB(self) -> list[float]:
        """Critical Region B matrix:"""
        return self.program.CrB

    @property
    def F(self) -> list[list[float]]:
        """F matrix for the constraints"""
        return self.program.F

    def make_A_df(self, longname: bool = False) -> DataFrame:
        """Create a DataFrame from the A matrix.

        Args:
            longname (bool, optional): Whether to use long names for variables. Defaults to False.

        Returns:
            DataFrame: Columns are the variables, rows are the constraints.
        """
        return self.program.make_A_df(longname)

    def make_B_df(self, longname: bool = False) -> DataFrame:
        """Create a DataFrame from the B vector.

        Args:
            longname (bool, optional): Whether to use long names for variables. Defaults to False.

        Returns:
            DataFrame: Has a single column, rows are the constraints.
        """
        return self.program.make_B_df(longname)

    def make_C_df(self, longname: bool = False) -> DataFrame:
        """Create a DataFrame from the C matrix.

        Args:
            longname (bool, optional): Whether to use long names for variables. Defaults to False.

        Returns:
            DataFrame: Columns are the variables, Has a single row
        """
        return self.program.make_C_df(longname)

    def make_df(self, longname: bool = False) -> DataFrame:
        """Create a DataFrame from the model.

        Args:
            longname (bool, optional): Whether to use long names for variables. Defaults to False.

        Returns:
            DataFrame: A DataFrame with the A matrix, B vector, and C vector.
        """
        return self.program.make_df(longname)

    def make_F_df(self, longname: bool = False) -> DataFrame:
        """Create a DataFrame from the F matrix.

        Args:
            longname (bool, optional): Whether to use long names for variables. Defaults to False.

        Returns:
            DataFrame: Columns are the variables, rows are the constraints.
        """
        return self.program.make_F_df(longname)

    def make_CrA_df(self, longname: bool = False) -> DataFrame:
        """Create a DataFrame from the CrA matrix.

        Args:
            longname (bool, optional): Whether to use long names for variables. Defaults to False.

        Returns:
            DataFrame: Columns are the variables, rows are the constraints.
        """
        return self.program.make_CrA_df(longname)

    def make_CrB_df(self, longname: bool = False) -> DataFrame:
        """Create a DataFrame from the CrB matrix.
        Args:
            longname (bool, optional): Whether to use long names for variables. Defaults to False.
        Returns:
            DataFrame: Columns are the variables, rows are the constraints.
        """
        return self.program.make_CrB_df(longname)

    # -------------------------------------
    #            Solution
    # -------------------------------------

    @property
    def solution(self) -> Solution:
        """The solution of the program"""
        return self.program.solution


@dataclass
class _Init(_Scope, _Impact, _Tree, _Graph, _System, _Program):
    """Defines the representation of the model"""

    def __post_init__(self):
        # Initialize the components
        _Scope.__post_init__(self)
        _Impact.__post_init__(self)
        _Tree.__post_init__(self)
        _Graph.__post_init__(self)
        _System.__post_init__(self)
        _Program.__post_init__(self)
