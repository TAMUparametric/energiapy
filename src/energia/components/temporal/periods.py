"""Time Periods"""

from __future__ import annotations

from functools import cached_property
from operator import is_
from typing import TYPE_CHECKING, Self

from gana import I as Idx

from ..._core._x import _X
from ...modeling.parameters.value import Value
from .lag import Lag

if TYPE_CHECKING:
    from gana.sets.constraint import C

    from ...dimensions.time import Time


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
        periods: int | float = 1,
        of: Self | None = None,
        label: str = "",
        captions: str = "",
    ):
        self.periods = periods
        self.of = of

        _X.__init__(self, label=label, captions=captions)

        self._periods = self.periods

        self._of = self.of

        if self.of is not None and not self.of.isroot():
            self.periods = self.periods * self.of.periods
            self.of = self.of.of

        self._horizon: Self | None = None

        # can be overwritten by program
        self.name = f"{self._periods}{self._of}"

        if self.of is None:
            self.of = self

        # if this is a slice of another period
        self.slice: slice | None = None

        # if this is a single period in Periods
        self.pos: int | None = None

    def isroot(self):
        """Is used to define another period?"""
        if self.of is None:
            return True

    @property
    def cons(self) -> list[C]:
        """Constraints"""
        return [getattr(self.program, c) for c in self.constraints]

    @property
    def time(self) -> Time:
        """Time to which the Periods belongs"""
        return self.model.time

    @property
    def horizon(self) -> Self:
        """Time Horizon"""
        return self.time.horizon

    @property
    def ishorizon(self) -> bool:
        """Is this the horizon of the model?"""
        return self == self.time.horizon

    @cached_property
    def I(self) -> Idx:
        """Index set of scale"""

        # given that temporal scale is an ordered set and not a self contained set
        # any time periods will be a fraction of the horizon
        if self.slice is not None:
            return self.of.I[self.slice]

        if self.pos is not None:
            return self.of.I[self.pos]

        _index = Idx(size=self.time.horizon.howmany(self), tag=self.label or "")
        setattr(self.program, self.name, _index)
        return _index

    def howmany(self, period: Self | Lag):
        """How many periods make this period"""

        if isinstance(period, Lag):
            # lags are usually made up of negative multiplications of periods
            return self.howmany(period.of) * period.periods

        if period == self:
            # if the same
            return 1

        if period.isroot():

            # if there are multiple root periods defined
            if is_(period, self.of):
                # if they are multiples of the same base period
                # check if they contain the same number of periods
                return self.periods
            raise ValueError(f"{period} is not a period of {self.name}")

        if is_(period.of, self.of):

            # if they are multiples of the same base period
            # return the ratio of the periods
            p = self.periods / period.periods
            if p.is_integer():
                return int(p)
            return p

        if is_(self, period.of):

            # if self is the base of the period
            # return the inverse of the of the periods
            return 1 / period.periods

        raise ValueError(f"{period} is not a period of {self.name}")

    def __mul__(self, times: int | float):

        if times < 0:
            # if multiplying by a negative number
            # return a lag
            if not self._of:
                return Lag(of=self, periods=-times)

            raise ValueError(f"{self} is not a period of anything, so cannot be lagged")

        if times < 1:
            # if it is a fraction
            period = Periods()
            if not self.of:
                # this is a root period
                period.of = self
                period.periods = times
            else:
                self.of = period
                self.periods = int(1 / times)
            return period

        return Periods(periods=int(times), of=self)

    def __truediv__(self, other: int | float):
        if isinstance(other, Periods):
            return self.howmany(other)

        return self * (1 / other)

        # return Periods(periods=other, of=self)

    def __rtruediv__(self, other: int | float):
        return Value(value=other, periods=self)

    def __rmul__(self, other: int | float):
        return self * other

    def __call__(self, times):
        return Periods(periods=times, of=self)

    def __neg__(self):
        return self * -1

    def __len__(self):
        return int(self.howmany(self.time.horizon))

    def __eq__(self, other: Self | Lag):
        if isinstance(other, Lag):
            return is_(self, other.of)

        return is_(self, other)

    def __ge__(self, other: Self):
        return self.time.horizon.howmany(self) <= self.time.horizon.howmany(other)

    def __gt__(self, other: Self):
        return self.time.horizon.howmany(self) < self.time.horizon.howmany(other)

    def __le__(self, other: Self):
        return self.time.horizon.howmany(self) >= self.time.horizon.howmany(other)

    def __lt__(self, other: Self):
        return self.time.horizon.howmany(self) > self.time.horizon.howmany(other)

    def __getitem__(self, key: int | slice):
        periods = Periods()
        periods.of = self
        periods.model = self.model

        if isinstance(key, slice):
            periods.slice = key
            start = key.start or 0
            stop = key.stop or len(self)
            periods.name = rf"{self}[{start}: {stop}]"
        else:
            periods.pos = key
            periods.name = rf"{self}[{key}]"

        return periods
