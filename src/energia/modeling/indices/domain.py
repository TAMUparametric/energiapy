"""Domain"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import prod
from operator import is_, is_not
from typing import TYPE_CHECKING, Optional, Self

if TYPE_CHECKING:
    from gana import I as Idx
    from gana import V

    from ..._core._x import _X
    from ...components.commodity._commodity import _Commodity
    from ...components.game.couple import Couple
    from ...components.game.player import Player
    from ...components.impact.indicator import Indicator
    from ...components.operation.process import Process
    from ...components.operation.storage import Storage
    from ...components.operation.transport import Transport
    from ...components.spatial.linkage import Linkage
    from ...components.spatial.location import Location
    from ...components.temporal.lag import Lag
    from ...components.temporal.modes import Modes
    from ...components.temporal.periods import Periods
    from ...represent.model import Model
    from ..variables.aspect import Aspect
    from ..variables.sample import Sample


@dataclass
class Domain:
    """
    A domain is an ordered set of the indices of an element.

    :param indicator: Indicates the impact of some activity through an equivalency,
        e.g. GWP, ODP.
    :type indicator: Indicator | None
    :param commodity: Represents the flow of any stream, measured using some basis,
        e.g. water, Rupee, carbon-dioxide.
    :type commodity: _Commodity | None
    :param process: Process that is being considered, e.g. dam, farming.
    :type process: Process | None
    :param storage: Storage that is being considered, e.g. reservoir.
    :type storage: Storage | None
    :param transport: Transport that is being considered, e.g. pipeline, road.
    :type transport: Transport | None
    :param player: Actor that takes decisions, e.g. me, you.
    :type player: Player | None
    :param couple: Other actor that might be paired with the player.
    :type couple: Couple | None
    :param location: Spatial aspect of the domain, e.g. Goa, Texas.
    :type location: Location | None
    :param linkage: Linkage aspect of the domain, e.g. pipeline, road.
    :type linkage: Linkage | None
    :param periods: Temporal aspect of the domain, e.g. year, month.
    :type periods: Periods | None
    :param lag: Indicates whether the temporal element is lagged or not.
    :type lag: Lag | None
    :param modes: Modes applicable to the domain.
    :type modes: Modes | None
    :param binds: List of binds that can be summed over.
    :type binds: list[Bind] | None

    :ivar model: Model to which the Domain belongs.
    :vartype model: Model

    """

    # the reason I keep these individual
    # instead of directly adding primary or stream
    # is because we do an instance check in Aspect
    # this helps relay the checks
    # primary component (one of these is needed)
    indicator: Optional[Indicator] = None
    commodity: Optional[_Commodity] = None

    process: Optional[Process] = None
    storage: Optional[Storage] = None
    transport: Optional[Transport] = None

    # decision - maker and other decision-maker
    player: Optional[Player] = None
    couple: Optional[Couple] = None

    # compulsory space and time elements
    location: Optional[Location] = None
    linkage: Optional[Linkage] = None
    periods: Optional[Periods] = None
    lag: Optional[Lag] = None
    modes: Optional[Modes] = None

    # These can be summed over
    binds: Optional[list[Sample]] = field(default_factory=list)

    def __post_init__(self):
        # Domains are structured something like this:
        # (primary_component ...aspect_n, secondary_component_n....,decision-makers, space, time
        # primary_component can be an indicator, commodity, or operation (process | storage | transport)
        # {aspect_n: secondary_component_n} is given in self.binds
        # decision-makers = player | couple
        # space = location | linkage
        # time = period | lag

        # primary index being modeled in some spatiotemporal context
        self.model: Model = next((i.model for i in self.index_short if i), None)

    @property
    def I(self) -> tuple[Idx, ...]:
        """Compound index"""
        return prod(self.Ilist)

    # -----------------------------------------------------
    #                    Components
    # -----------------------------------------------------

    # These are kept as properties
    # because domains are updated on the fly
    # look at change() and call()

    @property
    def stream(self) -> Indicator | _Commodity:
        """Stream"""
        return self.indicator or self.commodity

    @property
    def operation(self) -> Process | Storage | Transport:
        """Operation"""
        return self.process or self.storage or self.transport

    @property
    def primary(self) -> Indicator | _Commodity | Process | Storage | Transport:
        """Primary component"""
        _primary = self.stream or self.operation
        if not _primary:
            raise ValueError("Domain must have at least one primary index")
        return _primary

    @property
    def space(self) -> Location | Linkage:
        """Space"""
        return self.linkage or self.location

    @property
    def maker(self) -> Player | Couple:
        """Decision-maker"""
        return self.couple or self.player

    @property
    def time(self) -> Periods | Lag:
        """Time"""
        if self.periods is not None:
            return self.periods
        if self.lag is not None:
            return self.lag

        return self.model.horizon

    @property
    def linked(self) -> bool:
        """Linked"""
        return True if self.linkage else False

    @property
    def lagged(self) -> bool:
        """Lagged"""
        return True if self.lag else False

    # -----------------------------------------------------
    #                    Disposition
    # -----------------------------------------------------

    @property
    def isroot(self) -> bool:
        """
        This implies that the domain is of the form
        <object, space, time>
        """
        if self.lag:
            return False
        if self.disposition in [
            ("commodity", "space", "time"),
            ("indicator", "space", "time"),
            ("operation", "space", "time"),
        ]:
            return True
        return False

    @property
    def isrootroot(self) -> bool:
        """
        This implies that the domain is of the form
        <object, network, horizon>
        Thus, an element attached to this domain has the
        lowest possible dimensionality
        """
        if self.isroot:
            if is_(self.time, self.time.horizon):
                if is_(self.space, self.space.network):
                    return True
        return False

    @property
    def disposition(self) -> tuple[str, ...]:
        """Disposition"""
        return tuple(self._.keys())

    # -----------------------------------------------------
    #                    Naming
    # -----------------------------------------------------

    @property
    def name(self):
        """Name"""
        return f"{tuple(self.index)}"

    @property
    def idxname(self):
        """Name of the index"""
        return "_" + "_".join(f"{i}" for i in self.index)

    # -----------------------------------------------------
    #                    Dictionaries
    # -----------------------------------------------------

    @property
    def index(self) -> list[Aspect | _X]:
        """list of _Index elements"""

        # binds = sum([[i, j] for i, j in self.binds.items()], [])

        # these default to network and horizon, so can default from model using .space or .time

        return self.index_primary + self.index_binds

    @property
    def index_primary(
        self,
    ) -> list[Indicator | _Commodity | Process | Storage | Transport]:
        """Primary index

        :returns: list of primary indices
        :rtype: list[X]
        """
        return [self.primary] + [
            i
            for i in [self.location, self.linkage, self.periods, self.lag, self.modes]
            if i is not None
        ]

    @property
    def index_binds(self) -> list[Aspect | _X]:
        """List of bind indices

        :returns: list of bind indices
        :rtype: list[X]
        """
        return [x for b in self.binds for x in (b.aspect, b.domain.primary)]

    @property
    def index_short(
        self,
    ) -> list[Indicator | _Commodity | Process | Storage | Transport | Sample]:
        """Set of indices"""
        return self.index_primary + self.binds

    @property
    def tree(self) -> dict:
        """Convert index into tree"""

        tree = {}
        node = tree

        if self.binds:
            index = self.index[: -2 * (len(self.binds))]
        else:
            index = self.index
        for key in index:
            node[key] = {}
            node = node[key]
        for b in self.binds:
            node[b.aspect] = {}
            node[b.aspect][b.domain.primary] = {}
            node = node[b.aspect][b.domain.primary]

        # tree = {}
        # node = tree

        return tree

    @property
    def aspects(self) -> list[Aspect]:
        """Aspects"""
        return [b.aspect for b in self.binds]

    @property
    def args(
        self,
    ) -> dict[
        str,
        Indicator
        | _Commodity
        | Player
        | Process
        | Storage
        | Transport
        | Location
        | Linkage
        | Periods
        | Lag
        | Modes
        | list[Sample]
        | None,
    ]:
        """Dictionary of indices"""
        return {
            "indicator": self.indicator,
            "commodity": self.commodity,
            "player": self.player,
            "process": self.process,
            "storage": self.storage,
            "transport": self.transport,
            "location": self.location,
            "linkage": self.linkage,
            "periods": self.periods,
            "lag": self.lag,
            "modes": self.modes,
            "binds": self.binds,
        }

    @property
    def dictionary(
        self,
    ) -> dict[
        str,
        Indicator
        | _Commodity
        | Process
        | Storage
        | Transport
        | Player
        | Location
        | Linkage
        | Periods
        | Lag
        | Modes
        | list[Sample]
        | None,
    ]:
        """Dictionary of indices"""
        return {
            "primary": self.primary,
            "player": self.player,
            "space": self.space,
            "time": self.time,
            "modes": self.modes,
            "binds": self.binds,
        }

    # -----------------------------------------------------
    #                    Iterables
    # -----------------------------------------------------

    @property
    def _(self):
        """Dictionary of indices that are not None"""
        return {i: j for i, j in self.dictionary.items() if j is not None}

    @property
    def tup(self):
        """Tuple of objects"""
        return tuple(self._.values())

    @property
    def lst(self):
        """Tuple of objects"""
        return list(self._.values())

    @property
    def Ilist(self) -> list[Idx | list[V]]:
        """List of I"""
        return [i if isinstance(i, list) else i.I for i in self.index]

    # -----------------------------------------------------
    #                    Helpers
    # -----------------------------------------------------

    def update_cons(self, cons_name: str):
        """Update the constraints declared at every index"""
        for j in self.index:
            if cons_name not in j.constraints:
                j.constraints.append(cons_name)

    def update_domains(self, aspect: Aspect):
        """
        Update all elements in the domains with the aspects
        that they have been modeled in
        """
        for i, j in self._.items():
            if self.lag and i == "time":
                # lags disappear anyway, so dont bother
                continue
            if i not in ["binds"]:
                # these are dependent variables, so do not update them
                if self not in j.domains:
                    # check and update the domains at each index
                    j.domains.append(self)
                # if the variable is not in the list of variables at the index
                # update those
                if aspect not in j.aspects:
                    # first time (variable) is a dict {aspect: [..aspects..]}
                    j.aspects[aspect] = [self]
                elif self not in j.aspects[aspect]:
                    j.aspects[aspect].append(self)

    def copy(self) -> Self:
        """Make a copy of self"""
        return Domain(**self.args)

    def change(self, what: dict[str, _X]) -> Self:
        """Change some aspects and return a new Domain"""
        return Domain(**{**self.args, **what})

    # -----------------------------------------------------
    #                    Vector
    # -----------------------------------------------------

    def __getitem__(self, index: str) -> _X:
        """Get the index by name"""
        return self._[index]

    def __iter__(self):
        """Iterate over the indices"""
        return iter(self.index_short)

    def __call__(self, *args: str) -> Self:
        return Domain(**{i: j for i, j in self.args.items() if i in args})

    def __len__(self):
        return len(self.disposition)

    # -----------------------------------------------------
    #                    Operators
    # -----------------------------------------------------

    def __truediv__(self, other: list[str]) -> Self:
        """
        Will give you the Domain minus a particular index

        :param other: index you wish to remove
        :type other: str | list[str]

        :returns: lower dimensional domain
        :rtype: Domain

        .. example::
            >>> domain = Domain(commodity=water, operation=dam, space=goa, time=year)
            (water, dam, goa, year)
            >>> domain/'operation'
            (water, goa, year)
            >>> domain/['commodity', 'operation']
            (goa, year)
        """

        return Domain(**{i: j for i, j in self.args.items() if i not in other})

    def __sub__(self, other: Self) -> list[str]:
        """
        Will give you a list of indices that are not common between two domains

        :param other: another Domain object
        :type other: Self

        .. example::
            >>> domain1 = Domain(commodity=water, operation=dam, space=goa, time=year)
            >>> domain2 = Domain(commodity=water, space=mumbai, time=year)
            >>> domain1 - domain2
            ['operation', 'space']

        """
        notcommon = []
        for i, j in self._.items():
            # append if disposition is same but value is not
            if i in other._:
                if is_not(other._[i], j):
                    notcommon.append(i)
            else:
                # append if disposition is not in other
                notcommon.append(i)
        # The first loop will not check for the keys that are not in self._
        for k in other._.keys():
            if k not in self._:
                notcommon.append(k)

        return notcommon

    def __add__(self, other: Self) -> Self:
        return Domain(**{**self.args, **other.args})

    # -----------------------------------------------------
    #                    Relational
    # -----------------------------------------------------

    def __eq__(self, other):
        return self.name == str(other)

    def __lt__(self, other: Self) -> bool:
        """Less than comparison based on the number of indices"""
        if len(self) < len(other):
            return True
        return False

    def __gt__(self, other: Self) -> bool:
        """Greater than comparison based on the number of indices"""
        return other < self

    # -----------------------------------------------------
    #                    Hashing
    # -----------------------------------------------------

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
