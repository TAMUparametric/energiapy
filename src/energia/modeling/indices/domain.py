"""Domain"""

from __future__ import annotations

from dataclasses import dataclass
from math import prod
from operator import is_, is_not
from typing import TYPE_CHECKING, Self

from gana.sets.index import I

if TYPE_CHECKING:
    from ...components.commodity.resource import Resource
    from ...components.game.player import Player
    from ...components.game.couple import Couple
    from ...components.impact.indicator import Indicator
    from ...components.operation.process import Process
    from ...components.operation.storage import Storage
    from ...components.operation.transport import Transport
    from ...components.spatial.linkage import Link
    from ...components.spatial.location import Loc
    from ...components.temporal.lag import Lag
    from ...components.temporal.period import Period
    from ...core.component import Component
    from ...core.x import X
    from ..constraints.bind import Bind
    from ..parameters.conversion import Conv
    from ..variables.aspect import Aspect


@dataclass
class Domain:
    """A domain is a an ordered set of the indices of an element

    Attributes:
        indicator (Indicator): Indicates the impact of some activity through an equivalency, e.g. GWP, ODP.
        resource (Resource): Resource can represent the flow of any stream, measured using some basis, e.g. water, Rupee, carbon-dioxide.
        player (Player): Player is the actor that takes decisions, e.g. me, you.
        dr_aspect (Aspect): The aspect regarding the dresource that is being considered, e.g. consumption, production, purchase.
        dresource (Resource): dresource is responsible for the flow of resource, e.g. GWP due to water consumption, Rupee spent on water purchasing.
        op_aspect (Aspect): The aspect regarding the operation that is being considered, e.g. capacity, operating level.
        process (Process): Process is the process that is being considered, e.g. dam, farming.
        storage (Storage): Storage is the storage that is being considered, e.g. reservoir,
        transport (Transport): Transport is the transport that is being considered, e.g. pipeline, road.
        lag (bool): Lag is a boolean that indicates whether the temporal element is lagged or not
        loc (Loc): Location is the spatial aspect of the domain, e.g. Goa, Texas.
        link (Link): Linkage is the linkage aspect of the domain, e.g. pipeline, road.
        link (bool): Link is a boolean that indicates whether the spatial element is a linkage.
        period (Period): Time is the temporal aspect of the domain, e.g. year, month.
        lag (Lag): Lag is a boolean that indicates whether the temporal element is lagged or not.
    """

    # primary component
    indicator: Indicator = None
    resource: Resource = None
    process: Process = None
    storage: Storage = None
    transport: Transport = None
    # dr_aspect: Aspect = None
    # dresource: Resource = None
    # # operational
    # op_aspect: Aspect = None
    binds: dict[Resource | Process | Storage | Transport, Aspect] = None
    # decision - maker and other decision-maker
    player: Player = None
    couple: Couple = None
    # compulsory space and time elements
    loc: Loc = None
    link: Link = None
    period: Period = None
    lag: Lag = None

    def __post_init__(self):
        """Post initialization method to set up the domain
        Args:
            operation (Process | Storage | Transport): Operation is the process that is being considered, e.g. dam, farming.
            space (Loc | Link): Space is the spatial aspect of the domain, e.g. Goa, Texas.
            lagged (bool): Lagged is a boolean that indicates whether the temporal element is lagged or not.
        """

        # Domains are structured something like this:
        # (primary_component ...aspect_n, secondary_component_n....,decision-makers, space, time
        # primary_component can be an indicator, resource, or operation (process | storage | transport)
        # {aspect_n: secondary_component_n} is given in self.binds
        # decision-makers = player | couple
        # space = loc | link
        # time = period | lag

        # self.operation = self.process or self.storage or self.transport
        # self.space = self.loc or self.link
        # self.linked = True if self.link else False
        # self.time = self.period or self.lag
        # self.lagged = True if self.lag else False

        # primary index being modeled in some spatiotemporal context
        self.model = next((i.model for i in self.index if i), None)

        if self.indicator:
            self.primary = self.indicator
        elif self.resource:
            self.primary = self.resource
        elif self.operation:
            self.primary = self.operation
        else:
            raise ValueError('Domain must have at least one primary index')

        if not self.binds:
            self.binds = {}

    @property
    def I(self):
        """Compound index"""
        return prod(self.Ilist)

    # -----------------------------------------------------
    #                    Components
    # -----------------------------------------------------

    @property
    def operation(self) -> Process | Storage | Transport:
        """Operation"""
        return self.process or self.storage or self.transport

    @property
    def space(self) -> Loc | Link:
        """Space"""
        return self.link or self.loc

    @property
    def time(self) -> Period | Lag:
        """Time"""
        if self.period is not None:
            return self.period
        if self.lag is not None:
            return self.lag

        return self.model.horizon

    @property
    def linked(self) -> bool:
        """Linked"""
        return True if self.link else False

    @property
    def lagged(self) -> bool:
        """Lagged"""
        return True if self.lag else False

    # -----------------------------------------------------
    #                    Disposition
    # -----------------------------------------------------

    @property
    def isroot(self) -> bool:
        """This implies that the domain is of the form
        <object, space, time>
        """
        if self.lag:
            return False
        if self.disposition in [
            ('resource', 'space', 'time'),
            ('indicator', 'space', 'time'),
            ('operation', 'space', 'time'),
        ]:
            return True
        return False

    @property
    def isrootroot(self) -> bool:
        """This implies that the domain is of the form
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
    def disposition(self) -> str:
        """Disposition"""
        return tuple(self._.keys())

    # -----------------------------------------------------
    #                    Naming
    # -----------------------------------------------------

    @property
    def name(self):
        """Name"""
        return f'{tuple(self.index)}'

    @property
    def idxname(self):
        """Name of the index"""
        return '_' + '_'.join(f'{i}' for i in self.index)

    # -----------------------------------------------------
    #                    Dictionaries
    # -----------------------------------------------------

    @property
    def index(self) -> list[X]:
        """list of _Index elements"""
        return [
            i
            for i in [self.indicator, self.resource, self.operation]
            + list(sum(([i, j] for i, j in self.binds.items()), []))
            + [
                # self.dr_aspect,
                # self.dresource,
                # self.op_aspect,
                self.player,
                self.couple,
                self.space,
                self.period,
                self.lag,
            ]
            if i is not None
        ]

    @property
    def components(self) -> list[Component]:
        """Components"""
        return [
            i
            for i in [
                self.player,
                self.indicator,
                self.resource,
                self.operation,
            ]
            if i is not None
        ] + list(self.binds.keys())

    @property
    def aspects(self) -> list[Aspect]:
        """Aspects"""
        return list(self.binds.values())
        # return [
        #     i
        #     for i in [
        #         self.dr_aspect,
        #         self.op_aspect,
        #     ]
        #     if i is not None
        # ]

    @property
    def args(self) -> dict[str, X]:
        """Dictionary of indices"""
        return {
            'indicator': self.indicator,
            'resource': self.resource,
            'player': self.player,
            'binds': self.binds,
            'process': self.process,
            'storage': self.storage,
            'transport': self.transport,
            'loc': self.loc,
            'link': self.link,
            'period': self.period,
            'lag': self.lag,
        }

    @property
    def dictionary(self) -> dict[str, X]:
        """Dictionary of indices"""
        return {
            'indicator': self.indicator,
            'resource': self.resource,
            'player': self.player,
            'binds': self.binds,
            # 'dr_aspect': self.dr_aspect,
            # 'dresource': self.dresource,
            # 'op_aspect': self.op_aspect,
            'operation': self.operation,
            'space': self.space,
            'time': self.time,
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
    def Ilist(self):
        """List of I"""
        return [i if isinstance(i, list) else i.I for i in self.index]

    # -----------------------------------------------------
    #                    Helpers
    # -----------------------------------------------------

    def update_cons(self, cons_name: str):
        """Update the constraints declared at every index"""
        for j in self.index:
            if not cons_name in j.constraints:
                j.constraints.append(cons_name)

    def update_domains(self, aspect: Aspect):
        """Update all elements in the domains with the aspects
        that they have been modeled in
        """
        for i, j in self._.items():
            if self.lag and i == 'time':
                # lags disappear anyway, so dont bother
                continue
            if not i in ['binds']:
                # these are dependent variables, so do not update them
                if not self in j.domains:
                    # check and update the domains at each index
                    j.domains.append(self)
                # if the variable is not in the list of variables at the index
                # update those
                if not aspect in j.aspects:
                    # first time (variable) is a dict {aspect: [..aspects..]}
                    j.aspects[aspect] = [self]
                else:
                    if not self in j.aspects[aspect]:
                        j.aspects[aspect].append(self)

    def copy(self) -> Self:
        """Make a copy of self"""
        return Domain(**self.args)

    def change(self, what: dict[str, X]) -> Self:
        """Change some aspects and return a new Domain"""
        return Domain(**{**self.args, **what})

    # -----------------------------------------------------
    #                    Vector
    # -----------------------------------------------------

    def __getitem__(self, index: str) -> X:
        """Get the index by name"""
        return self._[index]

    def __iter__(self):
        """Iterate over the indices"""
        return iter(self.index)

    def __call__(self, *args: str) -> Self:
        return Domain(**{i: j for i, j in self.args.items() if i in args})

    def __len__(self):
        return len(self.disposition)

    # -----------------------------------------------------
    #                    Operators
    # -----------------------------------------------------

    def __truediv__(self, other: list[str]) -> Self:
        """Will give you the Domain minus a particular index

        Args:
            other (str): index you wish to remove

        Returns:
            Self: lower dimensional domain

        Example:
            >>> domain = Domain(resource=water, operation=dam, space=goa, time=year)
            (water, dam, goa, year)
            >>> domain/'operation'
            (water, goa, year)
            >>> domain/['resource', 'operation']
            (goa, year)
        """

        return Domain(**{i: j for i, j in self.args.items() if i not in other})

    def __sub__(self, other: Self) -> list[str]:
        """Will give you a list of indices that are not common between two domains
        Args:
            other (Self): another Domain object
        Returns:
            list[str]: list of indices that are not common

        Example:
            >>> domain1 = Domain(resource=water, operation=dam, space=goa, time=year)
            >>> domain2 = Domain(resource=water, space=mumbai, time=year)
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
            if not k in self._:
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
