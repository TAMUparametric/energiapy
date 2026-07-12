"""Domain"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from operator import is_, is_not
from typing import TYPE_CHECKING, Self

from ..._core._hash import _Hash

if TYPE_CHECKING:
    from gana import I as Idx
    from gana import V

    from ..._core._x import _X
    from ...components.commodities.commodity import Commodity
    from ...components.game.couple import Interact
    from ...components.game.player import Player
    from ...components.impact.indicator import Indicator
    from ...components.operations.process import Process
    from ...components.operations.storage import Storage
    from ...components.operations.transport import Transport
    from ...components.spatial.linkage import Linkage
    from ...components.spatial.location import Location
    from ...components.temporal.lag import Lag
    from ...components.temporal.modes import Modes
    from ...components.temporal.periods import Periods
    from ...represent.model import Model
    from ..variables.aspect import Aspect
    from .sample import Sample


@dataclass
class Domain(_Hash):
    """
    Point represented by a tuple of indices

    :param indicator: Indicates the impact of some activity through an equivalency,
        e.g. GWP, ODP.
    :type indicator: Indicator | None
    :param commodity: Represents the flow of any stream, measured using some basis,
        e.g. water, Rupee, carbon-dioxide.
    :type commodity: Commodity | None
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
    :param samples: List of samples that can be summed over.
    :type samples: list[Bind] | None

    :ivar model: Model to which the Domain belongs.
    :vartype model: Model

    """

    # the reason I keep these individual
    # instead of directly adding primary or stream
    # is because we do an instance check in Aspect
    # this helps relay the checks
    # primary component (one of these is needed)
    indicator: Indicator | None = None
    commodity: Commodity | None = None

    process: Process | None = None
    storage: Storage | None = None
    transport: Transport | None = None

    # decision - maker and other decision-maker
    player: Player | None = None
    couple: Interact | None = None

    # compulsory space and time elements
    location: Location | None = None
    linkage: Linkage | None = None
    periods: Periods | None = None
    lag: Lag | None = None
    modes: Modes | None = None

    # These can be summed over
    samples: list[Sample] = field(default_factory=list)

    def __post_init__(self):
        # Domains are structured something like this:
        # (primary_component ...aspect_n, secondary_component_n....,decision-makers, space, time
        # primary_component can be an indicator, commodity, or operation (process | storage | transport)
        # {aspect_n: secondary_component_n} is given in self.samples
        # decision-makers = player | couple
        # space = location | linkage
        # time = period | lag

        # primary index being modeled in some spatiotemporal context
        self.model: Model | None = next((i.model for i in self.index_short if i), None)

    # -----------------------------------------------------
    #                    Components
    # -----------------------------------------------------

    # These are kept as properties
    # because domains are updated on the fly
    # look at change() and call()

    @property
    def stream(self) -> Indicator | Commodity | None:
        """Stream"""
        return self.indicator or self.commodity

    @property
    def operation(self) -> Process | Storage | Transport | None:
        """Operation"""
        return self.process or self.storage or self.transport

    @property
    def primary(
        self,
    ) -> Indicator | Commodity | Process | Storage | Transport | list[Sample]:
        """Primary component"""
        _primary = self.stream or self.operation or self.samples
        if not _primary:
            raise ValueError("Domain must have at least one primary index")
        return _primary

    @property
    def sample(self) -> Sample | None:
        """Sample"""
        if self.samples:
            return self.samples[0]
        return None

    @property
    def space(self) -> Location | Linkage | None:
        """Space"""
        return self.linkage or self.location

    @property
    def maker(self) -> Player | Interact | None:
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
        if not self.lag and self.size == 3:
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
        return self.index_primary + self.index_binds + self.index_modes

    @property
    def index_primary(
        self,
    ) -> list[Indicator | Commodity | Process | Storage | Transport]:
        """Primary index

        :returns: list of primary indices
        :rtype: list[X]
        """
        return [self.primary] + [
            i for i in [self.space, self.periods, self.lag] if i is not None
        ]

    @property
    def index_spatiotemporal(self) -> list[Aspect | _X]:
        """List of indices with modes

        :returns: list of indices with modes
        :rtype: list[X]
        """
        return self.index_primary[1:] + self.index_modes

    @property
    def index_binds(self) -> list[Aspect | _X]:
        """List of bind indices

        :returns: list of bind indices
        :rtype: list[X]
        """
        return [x for b in self.samples for x in (b.aspect, b.domain.primary)]

    @property
    def index_modes(self) -> list[Modes]:
        """Set of mode indices"""
        return [self.modes] if self.modes else []

    @property
    def index_short(
        self,
    ) -> list[Indicator | Commodity | Process | Storage | Transport | Sample | Modes]:
        """Set of indices"""
        return self.index_primary + self.samples + self.index_modes

    @property
    def tree(self) -> dict:
        """Convert index into tree"""
        tree = {}
        node = tree
        for key in self.index:
            node[key] = {}
            node = node[key]
        return tree

    @property
    def aspects(self) -> list[Aspect]:
        """Aspects"""
        return [b.aspect for b in self.samples]

    @property
    def args(
        self,
    ) -> dict[
        str,
        Indicator
        | Commodity
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
            "samples": self.samples,
        }

    @property
    def dictionary(
        self,
    ) -> dict[
        str,
        Indicator
        | Commodity
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
        """Dictionary of Components"""
        return {
            "primary": self.primary,
            "player": self.player,
            "space": self.space,
            "time": self.time,
            "modes": self.modes,
            "samples": self.samples,
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

    @cached_property
    def I(self) -> list[Idx | list[V]]:
        """List of I"""
        _I = []
        for idx in self.index:
            if isinstance(idx, list):
                # this is how variables are handled in gana
                _I.append(idx)
            elif isinstance(idx.I, tuple):
                _I.extend(idx.I)
            else:
                _I.append(idx.I)
        return tuple(_I)

    @property
    def size(self) -> int:
        """Size of the domain"""
        return len(self.index)

    # -----------------------------------------------------
    #                    Helpers
    # -----------------------------------------------------

    def inform_components_of_cons(self, cons_name: str):
        """Update the constraints declared at every index"""
        for idx in self.index:
            idx.constraints.add(cons_name)

    def inform_components_of_domain(self, aspect: Aspect):
        """
        Update all components in the domains with the aspects
        that they have been modeled in

        :param aspect: Aspect being modeled
        :type aspect: Aspect
        """
        for i, j in self._.items():
            if i == "samples" or (self.lag and i == "time"):
                # lags disappear anyway, so dont bother
                continue
            # these are dependent variables, so do not update them
            if self not in j.domains:
                # check and update the domains at each index
                j.domains.append(self)
            # update the domain for the aspect for components
            try:
                j.aspects[aspect].add(self)
            except KeyError:
                j.aspects[aspect] = {self}

    def copy(self) -> Self:
        """Make a copy of self"""
        return Domain(**self.args)

    def edit(self, what: dict[str, _X]) -> Self:
        """Change some aspects and return a new Domain"""
        return Domain(**{**self.args, **what})

    def param_tree(self, parameter: float | list[float], rel: str) -> dict:
        """Tree representation of the Domain"""
        tree = {}
        node = tree
        n_last = len(self.index) - 1
        for n, key in enumerate(self.index):
            if n == n_last:
                if not node:
                    node[key] = {}
                node[key][rel] = parameter
            else:
                node[key] = {}
                node = node[key]
        return tree

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
