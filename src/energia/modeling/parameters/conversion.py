"""Conversion"""

from __future__ import annotations

from collections.abc import Mapping
from functools import cached_property
from typing import TYPE_CHECKING, Self

from ..._core._hash import _Hash
from ...components.temporal.lag import Lag
from ...components.temporal.modes import Modes

if TYPE_CHECKING:
    from gana import Prg

    from ...components.commodities.commodity import Commodity
    from ...components.operations.operation import Operation
    from ...components.operations.storage import Storage
    from ...components.spatial.linkage import Linkage
    from ...components.spatial.location import Location
    from ...components.temporal.periods import Periods
    from ...represent.model import Model
    from ..indices.sample import Sample


class Conversion(Mapping, _Hash):
    """
    Processes convert one Commodity to another Commodity
    Conversion provides the conversion of resources

    :param resource: Commodity that is balanced
    :type resource: Commodity
    :param operation: Process or Storage that serves as primary spatial index
    :type operation: Process | Storage
    :param bind: Sample that is used to define the conversion
    :type bind: Sample

    :ivar name: Name of the component, generated based on the operation.
    :vartype name: str
    :ivar base: Basis Commodity, usually has a value 1 in the conversion matrix, set using __call__. Defaults to None.
    :vartype base: Commodity
    :ivar conversion: {Commoditys: conversion}. Defaults to {}, set using __eq__.
    :vartype conversion: dict[Commodity : int | float]
    :ivar lag: Temporal lag (processing time) for conversion, set using __getitem__.
    :vartype lag: Lag
    :ivar periods: Periods over which the conversion is defined. Defaults to None.
    :vartype periods: Periods

    :raises ValueError: If conversion lists are of inconsistent lengths.

    .. note::
        - name and operation are generated post init
        - base (__call__), conversion (__eq__), lag (__getitem__) are defined as the program is built
        - Storage contains two processes (charge and discharge), hence is provided separately

    """

    def __init__(
        self,
        aspect: str = "",
        add: str = "",
        sub: str = "",
        operation: Operation | Storage | None = None,
        resource: Commodity | None = None,
        balance: dict[Commodity, float | list[float]] | None = None,
        hold: int | float | None = None,
        attr_name: str = "",
        symbol: str = "η",
        use_max_time: bool = False,
    ):

        self.resource = resource
        self.operation = operation

        self.symbol = symbol

        # * Aspect that elicits the conversion
        self.aspect = aspect

        # * Aspects corresponding to positive and negative conversion
        self.add = add
        self.sub = sub

        if balance:
            self.balance = balance
        else:
            self.balance = {}

        # value to hold, will be applied later
        # occurs when Conversion/Commodity == parameter is used
        # the parameter is held until a dummy resource is created
        self.hold = hold
        # used if a resource is expected to be inventoried
        self.expect: Commodity | None = None

        self.lag: Lag | None = None

        # this is carried forth incase, piece wise linear conversion is used
        self.attr_name = attr_name

        self.use_max_time = use_max_time

    @property
    def args(self) -> dict[str, str | Operation | Commodity | None]:
        """Arguments of the conversion"""
        return {
            'by': self.aspect,
            'add': self.add,
            'sub': self.sub,
            'operation': self.operation,
            'basis': self.resource,
        }

    @classmethod
    def from_balance(
        cls,
        balance: dict[Commodity, float | list[float]],
        by: str = "",
        add: str = "",
        sub: str = "",
        operation: Operation | None = None,
        basis: Commodity | None = None,
    ) -> Self:
        """Creates Conversion from balance dict"""
        conv = cls()
        # set first resource as the basis
        conv.balance = balance
        conv.operation = operation
        conv.aspect = by
        conv.add = add
        conv.sub = sub
        conv.resource = basis
        return conv

    @property
    def name(self) -> str:
        """Name"""
        if self.resource:
            return f"{self.symbol}({self.operation}, {self.resource})"
        return f"{self.symbol}({self.operation})"

    @cached_property
    def model(self) -> Model | None:
        """energia Model"""
        return next((i.model for i in self.balance), None)

    @cached_property
    def program(self) -> Prg | None:
        """gana Program"""
        return self.operation.program

    def balancer(self):
        """
        Checks if there is a list in the conversion
        If yes, tries to make everything consistent
        """

        def _balancer(conversion: dict):

            # check if lists are provided
            check_list = dict.fromkeys(conversion.keys(), False)
            # check lengths of the list, for parameter the length is 1
            check_len = dict.fromkeys(conversion.keys(), 1)

            for res, par in conversion.items():
                if isinstance(par, list):
                    check_list[res] = True
                    check_len[res] = len(par)

            # check if all the list lens are the same
            lengths = {i for i in check_len.values() if i > 1}

            if len(lengths) > 1:
                # if there are different lengths, raise an error
                raise ValueError(
                    f"Conversion: {self.name} has inconsistent list lengths: {lengths}",
                )

            if any(check_list.values()):
                length = next(iter(lengths))
                # if any of the values are a list
                #
                for res, par in conversion.items():
                    if isinstance(par, (float, int)):
                        conversion[res] = [par] * length
            return conversion

        self.balance = _balancer(self.balance)

    def write(
        self, space: Location | Linkage, time: Periods | Lag, modes: Modes | None = None
    ):
        """Writes equations for conversion balance"""

        def time_checker(res: Commodity, space: Location | Linkage, time: Periods):
            """This checks if it is actually necessary
            to write conversion at denser temporal scales
            """
            # This checks whether some other aspect is defined at
            # a lower temporal scale

            if space not in self.model.balances[res]:
                # if not defined for that location, check for a lower order location
                # i.e. location at a lower hierarchy,
                # e.g. say if space being passed is a city, and a grb has not been defined for it
                # then we need to check at a higher order
                parent = self.model.space.split(space)[
                    1
                ]  # get location at one hierarchy above
                if parent:
                    # if that indeed exists, then make the parent the space
                    # the conversion Balance variables will feature in grb for parent location
                    space = parent

            _ = self.model.balances[res][space][time]

            if res.inv_of:
                # for inventoried resources, the conversion is written
                # using the time of the base resource's grb
                res = res.inv_of

            try:
                times = list(
                    [
                        t
                        for t in self.model.balances[res][space]
                        if self.model.balances[res][space][t]
                    ],
                )
            except KeyError:
                times = []
            # write the conversion balance at
            # densest temporal scale in that space
            if times:
                if self.use_max_time:
                    return max(times)
                return min(times)

            return time.horizon

        for res, par in self.items():

            if res in self.model.balances:
                time = time_checker(res, space, time)
                _ = self.model.balances[res].get(space, {})

            eff = par if isinstance(par, list) else [par]

            decision = getattr(self.operation, self.aspect)

            if eff[0] < 0:
                # Resources are consumed (expendend by Process) immediately

                dependent = getattr(res, self.sub)
                eff = [-e for e in eff]
            else:
                # Production — may occur after lag
                time = self.lag.of if self.lag else time
                dependent = getattr(res, self.add)

            if modes:
                rhs = dependent(decision, space, modes, time)

                lhs = decision(space, modes, time)
            else:
                rhs = dependent(decision, space, time)

                lhs = decision(space, time)

            _ = lhs[rhs] == eff

    def items(self):
        """Items of the conversion balance"""
        return self.balance.items()

    def keys(self):
        """Keys of the conversion balance"""
        return self.balance.keys()

    def values(self):
        """Values of the conversion balance"""
        return self.balance.values()

    def __getitem__(self, key: Commodity) -> float | list[float]:
        """Used to define mode based conversions"""
        return self.balance[key]

    def __setitem__(self, key: Commodity, value: float | list[float]):
        self.balance[key] = value

    def __call__(self, basis: Commodity | Conversion, lag: Lag | None = None) -> Self:
        # sets the basis
        if isinstance(basis, Conversion):
            # if a Conversion is provided (parameter*Commodity)
            # In this case the associated conversion is not 1
            # especially useful if Process is scaled to consumption of a commodity
            # i.e. basis = -1*Commodity
            self.balance = {**self, **basis}
            self.resource = next(iter(self))

        else:
            # if a Commodity is provided
            # implies that the conversion is 1
            # i.e the Process is scaled to one unit of this Commodity produced
            self.balance = {basis: 1.0, **self}

        if lag:
            self.lag = lag

        return self

    def __eq__(
        self,
        other: Conversion | list[Conversion] | int | float | dict[Modes, Conversion],
    ):
        if isinstance(other, dict):

            collect_parents = []
            for mode, conv in other.items():
                conv.operation = self.operation

                collect_parents.append(mode.parent)

                other[mode] = Conversion.from_balance({**self, **conv}, **self.args)

            if len(set(collect_parents)) > 1:
                raise ValueError(
                    f"{self}: PWL Conversion modes must belong to the same parent Modes",
                )

            if len(collect_parents[0]) != len(other):
                raise ValueError(
                    f"{self}: PWL Conversion modes must account for all modes in {collect_parents[0]}",
                )

            setattr(
                self.operation,
                self.attr_name,
                PWLConversion.from_balance(
                    balance=other, sample=getattr(self.operation, self.aspect)
                ),
            )
            return getattr(self.operation, self.attr_name)

        if isinstance(other, list):
            if self.resource:
                for i, o in enumerate(other):
                    other[i] = Conversion.from_balance(
                        {**self, **o},
                    )
            setattr(
                self.operation,
                self.attr_name,
                PWLConversion(
                    conversions=other,
                    sample=(
                        getattr(self.operation.stored, self.aspect)
                        if hasattr(self.operation, "stored")
                        else getattr(self.operation, self.aspect)
                    ),
                    aspect=self.aspect,
                    add=self.add,
                    sub=self.sub,
                ),
            )
            return getattr(self.operation, self.attr_name)

        if isinstance(other, (int, float)):
            # this is used for inventory conversion
            # when not other resource besides the one being inventoried is involved
            self.balance = {**self, self.expect: 1 / -float(other)}
        else:
            self.balance = {**self, **other}
        self.model.convmatrix[self.operation] = self.balance
        return self

    def __neg__(self) -> Self:
        self.balance = {res: -par for res, par in self.balance.items()}
        return self

    def __add__(self, other: Conversion) -> Self:
        self.balance = {**self, **other}
        return self

    def __sub__(self, other: Conversion) -> Self:
        self.balance = {**self, **-other}
        return self

    def __mul__(self, times: int | float | list) -> Self:
        if isinstance(times, list):
            self.balance = {res: [par * i for i in times] for res, par in self.items()}
        else:
            self.balance = {res: par * times for res, par in self.items()}
        return self

    def __rmul__(self, times) -> Self:
        return self * times

    def __len__(self):
        """Length of the conversion balance"""
        return len(self.balance)

    def __iter__(self):
        return iter(self.balance)


class PWLConversion(Mapping, _Hash):
    """Piece Wise Linear Conversion"""

    def __init__(
        self,
        conversions: list[Conversion],
        sample: Sample,
        aspect: str = "",
        add: str = "",
        sub: str = "",
    ):

        self.sample = sample
        self.operation = self.sample.domain.operation or self.sample.domain.primary
        self.model = self.sample.model
        if conversions:

            self.modes = self.model.Modes(size=len(conversions), sample=sample)
            self.balance: dict[Modes, Conversion] = dict(zip(self.modes, conversions))

            for conv in conversions:
                conv.operation = self.operation
                conv.aspect = aspect or conv.aspect
                conv.add = add or conv.add
                conv.sub = sub or conv.sub

        self._aspect = aspect
        self._add = add
        self._sub = sub

    @property
    def aspect(self) -> str:
        if self._aspect:
            return self._aspect
        return self[0].aspect

    @property
    def add(self) -> str:
        if self._add:
            return self._add
        return self[0].add

    @property
    def sub(self) -> str:
        if self._sub:
            return self._sub
        return self[0].sub

    @property
    def lag(self) -> str:
        return self[0].lag

    @classmethod
    def from_balance(
        cls,
        balance: dict[Modes, Conversion],
        sample: Sample,
    ) -> Self:
        """Creates PWLConversion from balance dict"""
        conv = cls([], sample)
        conv.operation = sample.domain.operation
        conv.balance = balance
        conv.modes = (next(iter(balance))).parent

        return conv

    def balancer(self):
        """Balances all conversions"""
        for conv in self.balance.values():
            conv.balancer()

    @property
    def name(self) -> str:
        """Name"""
        return f"η_PWL({self.operation}, {self.modes})"

    def __len__(self):
        """Length of the conversion balance"""
        return len(self.balance)

    def __iter__(self):
        return iter(self.balance)

    def __setitem__(self, key: int | str | Modes, value: Conversion):

        if isinstance(key, int):
            key = self.modes[key]

        self.balance[key] = value

    def __getitem__(self, key: int | str) -> Conversion:
        """Used to define mode based conversions"""

        if isinstance(key, int):
            key = self.modes[key]

        return self.balance[key]

    def items(self):
        """Items of the conversion balance"""
        return self.balance.items()

    def keys(self):
        """Keys of the conversion balance"""
        return self.balance.keys()

    def values(self):
        """Values of the conversion balance"""
        return self.balance.values()

    def box(self):
        """Consolidates the conversion dict into {resource: par} format"""
        resources = list(set().union(*self.values()))
        _box = {r: [] for r in resources}
        for conv in self.values():
            for resource in resources:
                if resource in conv:
                    _box[resource].append(conv[resource])
                else:
                    _box[resource].append(None)

        return _box

    def write(self, space: Location | Linkage, time: Periods | Lag):
        """Writes equations for conversion balance"""

        for mode, conv in self.items():
            conv.write(space, time, mode)
