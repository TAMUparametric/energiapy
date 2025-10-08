"""Blocks of the Model"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from ..components.commodity.resource import Resource
from ..components.operation.transport import Transport
from ..dimensions.consequence import Consequence
from ..dimensions.problem import Problem
from ..dimensions.space import Space
from ..dimensions.system import System
from ..dimensions.time import Time
from .graph import Graph
from .program import Program

if TYPE_CHECKING:
    from gana import P, T, V
    from gana.block.solution import Solution
    from gana.sets.constraint import C as Cons
    from gana.sets.function import F as Func
    from pandas import DataFrame

    from ..components.impact.categories import Economic, Environ, Social
    from ..components.operation.process import Process
    from ..components.operation.storage import Storage
    from ..components.spatial.linkage import Linkage
    from ..components.spatial.location import Location
    from ..components.temporal.modes import Modes
    from ..components.temporal.periods import Periods
    from ..modeling.indices.domain import Domain
    from ..modeling.variables.aspect import Aspect
    from ..modeling.variables.control import Control
    from ..modeling.variables.states import Impact, State, Stream


@dataclass
class _Scope:
    """Defines the scope of the model.

    :param update_map: Mapping used for updating internal structures (if applicable).
    :type update_map: dict
    :param time: Time representation of the Model (set during post-initialization).
    :type time: Time
    :param space: Spatial representation of the Model (set during post-initialization).
    :type space: Space
    """

    # meshes of space and time to denote whether a constraint is written
    # general resource balance

    def __post_init__(self):

        # Temporal Scope
        self.time = Time(self)
        # Spatial Scope
        self.space = Space(self)

    @property
    def horizon(self) -> Periods:
        """The horizon of the Model"""
        return self.time.horizon

    @property
    def network(self) -> Location:
        """The network of the Model"""
        return self.space.network


@dataclass
class _Mapping:
    """Defines the scope of the model.

    :param update_map: Mapping used for updating internal structures (if applicable).
    :type update_map: dict
    :param time: Time representation of the Model (set during post-initialization).
    :type time: Time
    :param space: Spatial representation of the Model (set during post-initialization).
    :type space: Space
    """

    # meshes of space and time to denote whether a constraint is written
    # general resource balance

    def __post_init__(self):

        # Dictionary which tells you what aspects of resource
        # have grb {loc: time: []} and {time: loc: []}
        self.grb: dict[
            Resource,
            dict[Location | Linkage, dict[Periods, list[Aspect]]],
        ] = {}

        # Dictionary which tells you what aspects of what component
        # have been bound at what location and time
        self.dispositions: dict[
            Aspect,
            dict[
                Resource | Process | Storage | Transport,
                dict[Location | Linkage, dict[Periods, list[Aspect]]],
            ],
        ] = {}

        self.maps: dict[Aspect, dict[Domain, dict[str, list[Domain]]]] = {}
        self.maps_report: dict[Aspect, dict[Domain, dict[str, list[Domain]]]] = {}

    def update_dispositions(
        self,
        aspect: Aspect,
        domain: Domain,
    ):
        """Updates the spatiotemporal dispositions for an aspect pertaining to a component"""

        def merge_trees(d1, d2):
            """Recursively merge two tree-like dicts (values always dicts)."""
            result = dict(d1)  # shallow copy of d1
            for k, v in d2.items():
                if k in result:
                    result[k] = merge_trees(
                        result[k],
                        v,
                    )  # recurse since v must also be a dict
                else:
                    result[k] = v
            return result

        self.dispositions = merge_trees(self.dispositions, {aspect: domain.tree})

    def update_grb(self, resource: Resource, space: Location | Linkage, time: Periods):
        """Creates a mesh for grb dict"""

        if resource not in self.grb:
            # update resource if needed
            self.grb[resource] = {}

        if space not in self.grb[resource]:
            # update space if needed
            self.grb[resource][space] = {}

        if time not in self.grb[resource][space]:
            self.grb[resource][space][time] = []


@dataclass
class _Impact:
    """Defines the impact of the model"""

    def __post_init__(self):

        # Impact on the exterior
        self.consequence = Consequence(self)

    @property
    def indicators(self) -> list[Social | Environ | Economic]:
        """Indicators"""
        return self.consequence.indicators


@dataclass
class _Tree:
    """Defines the feasible region of the model"""

    def __post_init__(self):
        # Tree (Feasible Region)
        self.problem = Problem(self)

    def get(
        self,
        keys: Literal[
            "aspects",
            "states",
            "controls",
            "streams",
            "impacts",
            "domains",
        ] = "aspects",
        values: Literal[
            "aspects",
            "states",
            "controls",
            "streams",
            "impacts",
            "domains",
        ] = "domains",
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
        return self.problem.get(keys, values)


@dataclass
class _Graph:
    """Defines the network as a graph"""

    def __post_init__(self):
        # Graph (Network)
        self.graph = Graph(self)

    # @property
    # def edges(self) -> list[Linkage]:
    #     """The Edges"""
    #     return self.graph.edges

    # @property
    # def nodes(self) -> list[Location]:
    #     """The Nodes"""
    #     return self.graph.nodes


@dataclass
class _System:
    """Defines the system of the model"""

    def __post_init__(self):
        # System (Resource Task Network)
        self.system = System(self)

    @property
    def operations(self) -> list[Process | Storage | Transport]:
        """The Operations"""
        return self.system.operations


@dataclass
class _Program:
    """Defines the mathematical program of the model"""

    def __post_init__(self):
        # mathematical (mixed integer) program
        self.program = Program(self.name)
        self._ = self.program

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

    # -------------------------------------
    #            Solution
    # -------------------------------------

    @property
    def solution(self) -> Solution:
        """The solution of the program"""
        return self.program.solution

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
    #            Ordered Lists
    # -------------------------------------

    def cons(self) -> list[Cons]:
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


@dataclass
class _Init(_Scope, _Impact, _Tree, _Graph, _System, _Program, _Mapping):
    """Defines the representation of the model"""

    def __post_init__(self):
        # Initialize the components
        _Scope.__post_init__(self)
        _Impact.__post_init__(self)
        _Tree.__post_init__(self)
        _Graph.__post_init__(self)
        _System.__post_init__(self)
        _Program.__post_init__(self)
        _Mapping.__post_init__(self)
