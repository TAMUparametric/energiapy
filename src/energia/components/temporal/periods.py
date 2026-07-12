"""Time Periods"""

from __future__ import annotations

import logging
from functools import cached_property
from operator import is_
from typing import TYPE_CHECKING, Self

from gana import I as Idx

from ..._core._x import _X
from ...modeling.parameters.value import Value
from ...utils.dictionary import NotFoundError, compare
from .lag import Lag

if TYPE_CHECKING:
    from gana.sets.constraint import C

    from ...components.temporal.modes import Modes
    from ...dimensions.time import Time


logger = logging.getLogger("energia")


class Periods(_X):
    """
    A discretization of Time.

    :param periods: Number of periods in Periods. Defaults to 1.
    :type periods: int | float
    :param of: The periods of which this is a multiple. Defaults to None.
    :type of: Periods | Lag, optional
    :param name: Name of the periods. Defaults to None.
    :type name: str, optional
    :param label: Label of the periods. Defaults to None.
    :type label: str, optional

    :ivar model: Model to which the Periods belongs.
    :vartype model: Model
    :ivar time: Time to which the Periods belongs.
    :vartype time: Time
    :ivar horizon: Horizon of the Time.
    :vartype horizon: Periods
    :ivar I: Index set of the Periods.
    :vartype I: I
    :ivar constraints: List of constraints associated with the Periods. Defaults to [].
    :vartype constraints: list[str]
    :ivar domains: List of domains associated with the Periods. Defaults to [].
    :vartype domains: list[Domain]
    :ivar aspects: Aspects associated with the Periods.
    :vartype aspects: dict[Aspect, list[Domain]]
    """

    def __init__(
        self,
        size: int | float = 1,
        of: Self | None = None,
        n: int | None = None,
        label: str = "",
        citations: str = "",
    ):
        self.size = size

        if of is not None:
            of.isof.append(self)

        self.of = of

        # is a period of
        self.isof: list[Self] = []

        _X.__init__(self, label=label, citations=citations)

        # if this is a slice of another period
        self.slice: slice | None = None

        # if this is a single period in Periods
        self.n = n

        # if parent is true, this is part of another periods set
        self.parent: Self | None = None

        self.modes: list[Modes] = []

        if self.of is not None and self.size:
            # self.tree = {self.of: self.of.tree}
            self.name = f"{self.size}{self.of}"

        self._howmany: dict[Periods, float] = {}

    def isroot(self):
        """Is used to define another period?"""
        if self.of is None:
            return True

    def ishorizon(self) -> bool:
        """Is this the horizon of the model?"""
        return self == self.time.horizon

    @property
    def tree(self) -> dict[Self, dict]:
        """Tree representation of the Periods"""
        if self.of is None:
            return {self: {}}

        return {self: self.of.tree}

    @property
    def cons(self) -> list[C]:
        """Constraints"""
        return [getattr(self.program, c) for c in self.constraints]

    @property
    def horizon(self) -> Self:
        """Time Horizon"""
        return self.time.horizon

    @cached_property
    def time(self) -> Time:
        """Time to which the Periods belongs"""
        return self.model.time

    @cached_property
    def I(self) -> Idx:
        """Index tuple"""

        # given that temporal scale is an ordered set and not a self contained set
        # any time periods will be a fraction of the horizon
        if self.slice is not None:
            return self.of.I[self.slice]

        if self.n is not None:
            return self.of.I[self.n]

        if self.isof:
            return self.isof[0].I + (self.i,)
        return (self.i,)

    @cached_property
    def i(self) -> Idx:
        """Only Index"""
        _i = Idx(size=self.isof[0].size if self.isof else 1, tag=self.label or "")
        setattr(self.program, self.name, _i)
        return _i

    @property
    def true_size(self) -> float:
        """True size of the Periods"""
        if self.of is None:
            return self.size

        return self.size * self.of.true_size

    def howmany(self, of: Periods):
        """How many periods make this period"""

        # Cached result?
        if of in self._howmany:
            return self._howmany[of]

        attempts = [
            lambda: compare(self.tree, of),
            lambda: 1 / compare(of.tree, self),
            lambda: self.size / compare(of.tree, self.of),
            lambda: compare(self.tree, of.of) / of.size,
        ]

        for attempt in attempts:
            try:
                result = attempt()
                self._howmany[of] = result
                return result
            except NotFoundError:
                continue

        raise ValueError(f"No common basis between {self} and {of}")

    def __mul__(self, times: int | float):

        if times == 0:
            return 0

        if times < 0:
            # if multiplying by a negative number
            # return a lag
            # if not self._of:
            return Lag(of=self, periods=-times)

            # raise ValueError(f"{self} is not a period of anything, so cannot be lagged")

        # if times < 1:
        #     return (1 / times) * self

        return Periods(size=times, of=self)

    def __truediv__(self, other: int | float):
        if isinstance(other, Periods):
            return self.howmany(other)

        return self * (1 / other)

        # return Periods(periods=other, of=self)

    def __rtruediv__(self, other: int | float):
        return Value(value=other, periods=self)

    def __rmul__(self, other: int | float):
        return self * other

    # def __call__(self, times):
    #     return Periods(size=times, of=self)

    def __neg__(self):
        return self * -1

    def __len__(self):
        return int(self.howmany(self.time.horizon))

    def __eq__(self, other: Self | Lag):
        return is_(self, other)

    def __ge__(self, other: Self):
        if isinstance(other, Periods):
            return self.time.horizon.howmany(self) <= self.time.horizon.howmany(other)
        raise NotImplementedError

    def __gt__(self, other: Self):
        if isinstance(other, Periods):
            return self.time.horizon.howmany(self) < self.time.horizon.howmany(other)
        raise NotImplementedError

    def __le__(self, other: Self):
        if isinstance(other, Periods):
            return self.time.horizon.howmany(self) >= self.time.horizon.howmany(other)
        raise NotImplementedError

    def __lt__(self, other: Self):
        if isinstance(other, Periods):
            return self.time.horizon.howmany(self) > self.time.horizon.howmany(other)
        raise NotImplementedError

    def __getitem__(self, key: int | slice):

        periods = Periods()
        periods.parent = self
        periods.of = self.of
        periods.model = self.model

        if isinstance(key, slice):
            periods.slice = key
            # record the range
            start = key.start or 0
            stop = key.stop or len(self)
            # not set on the model
            periods.name = rf"{self}[{start}: {stop}]"
        else:
            # single period
            periods.n = key
            periods.name = rf"{self}[{key}]"

        return periods
