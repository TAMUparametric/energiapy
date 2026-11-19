"""Conversion."""

from __future__ import annotations

import operator
from collections.abc import Callable, Mapping
from copy import copy
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


type _Coefficient = float | list[float]
type _Arithmetic = Callable[[float, float], float]


def _apply_coefficients(
    left: _Coefficient,
    right: _Coefficient,
    operation: _Arithmetic,
) -> _Coefficient:
    """Apply arithmetic period by period, broadcasting scalar coefficients."""
    if isinstance(left, list):
        if isinstance(right, list):
            return [operation(a, b) for a, b in zip(left, right, strict=True)]
        return [operation(a, right) for a in left]
    if isinstance(right, list):
        return [operation(left, b) for b in right]
    return operation(left, right)


class Conversion(Mapping, _Hash):
    """
    Processes convert one Commodity to another Commodity.

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
        """Initialize the material balance, reference commodity, and decision aspect."""
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
        """Arguments of the conversion."""
        return {
            "by": self.aspect,
            "add": self.add,
            "sub": self.sub,
            "operation": self.operation,
            "basis": self.resource,
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
        """
        Creates Conversion from balance dict.

        .. admonition:: Example

            .. code-block:: python

                from energia import Model, Resource
                from energia.modeling.parameters.conversion import Conversion

                m = Model()
                m.power, m.heat = Resource(), Resource()
                mix = Conversion.from_balance({m.power: 1, m.heat: 2})
                assert (3 * mix)[m.heat] == 6
                assert mix[m.heat] == 2
        """
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
        """Name."""
        if self.resource:
            return f"{self.symbol}({self.operation}, {self.resource})"
        return f"{self.symbol}({self.operation})"

    @cached_property
    def model(self) -> Model | None:
        """Energia Model."""
        return next((i.model for i in self.balance), None)

    @cached_property
    def program(self) -> Prg | None:
        """Gana Program."""
        return self.operation.program

    def balancer(self):
        """Expand scalar coefficients to match the conversion's series length."""
        lengths = {
            len(value) for value in self.balance.values() if isinstance(value, list)
        }
        if not lengths:
            return
        if 0 in lengths:
            message = f"Conversion: {self.name} has an empty coefficient list"
            raise ValueError(message)

        # A singleton coefficient also works as a constant alongside a longer series.
        if len(lengths - {1}) > 1:
            message = (
                f"Conversion: {self.name} has inconsistent list lengths: {lengths}"
            )
            raise ValueError(message)

        length = max(lengths)
        for resource, value in self.balance.items():
            if isinstance(value, (float, int)):
                self.balance[resource] = [value] * length

    def time_checker(
        self,
        commodity: Commodity,
        space: Location | Linkage,
        time: Periods,
    ):
        """Determine whether the conversion needs a finer time scale."""
        # This checks whether some other aspect is defined at
        # a lower temporal scale

        if space not in self.model.balances[commodity]:
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

        _ = self.model.balances[commodity][space][time]

        if commodity.inv_of:
            # for inventoried resources, the conversion is written
            # using the time of the base resource's grb
            commodity = commodity.inv_of

        try:
            times = [
                t
                for t in self.model.balances[commodity][space]
                if self.model.balances[commodity][space][t]
            ]
        except KeyError:
            times = []
        # write the conversion balance at
        # densest temporal scale in that space
        if times:
            if self.use_max_time:
                return max(times)
            return min(times)

        return time.horizon

    def write(
        self,
        space: Location | Linkage,
        time: Periods | Lag,
        modes: Modes | None = None,
    ):
        """Writes equations for conversion balance."""
        for res, par in self.items():
            resource_time = time
            if res in self.model.balances:
                resource_time = self.time_checker(res, space, time)

            eff = par if isinstance(par, list) else [par]

            decision = getattr(self.operation, self.aspect)

            if eff[0] < 0:
                # Resources are consumed (expendend by Process) immediately

                dependent = getattr(res, self.sub)
                eff = [-e for e in eff]
            else:
                # Production — may occur after lag
                if self.lag:
                    resource_time = self.lag.of
                dependent = getattr(res, self.add)

            if modes:
                rhs = dependent(decision, space, modes, resource_time)

                lhs = decision(space, modes, resource_time)
            else:
                rhs = dependent(decision, space, resource_time)

                lhs = decision(space, resource_time)

            _ = lhs[rhs] == eff

    def items(self):
        """Items of the conversion balance."""
        return self.balance.items()

    def keys(self):
        """Keys of the conversion balance."""
        return self.balance.keys()

    def values(self):
        """Values of the conversion balance."""
        return self.balance.values()

    def __getitem__(self, key: Commodity) -> float | list[float]:
        """Used to define mode based conversions."""
        return self.balance[key]

    def __setitem__(self, key: Commodity, value: float | list[float]):
        """Assign a scalar or series of coefficients to a commodity in the balance."""
        self.balance[key] = value

    def __call__(self, basis: Commodity | Conversion, lag: Lag | None = None) -> Self:
        """Set the conversion basis and optionally attach a time lag."""
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
        """Assign coefficients, a balance, or mode-specific conversions to the operation."""
        if isinstance(other, dict):
            collect_parents = []
            for mode, conv in other.items():
                conv.operation = self.operation

                collect_parents.append(mode.parent)

                other[mode] = Conversion.from_balance({**self, **conv}, **self.args)

            if len(set(collect_parents)) > 1:
                message = (
                    f"{self}: PWL Conversion modes must belong to the same parent Modes"
                )
                raise ValueError(message)

            if len(collect_parents[0]) != len(other):
                message = f"{self}: PWL Conversion modes must account for all modes in {collect_parents[0]}"
                raise ValueError(message)

            setattr(
                self.operation,
                self.attr_name,
                PWLConversion.from_balance(
                    balance=other,
                    sample=getattr(self.operation, self.aspect),
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

    def _with_balance(self, balance: dict[Commodity, _Coefficient]) -> Self:
        result = copy(self)
        result.balance = balance
        result.__dict__.pop("model", None)  # derived from the first commodity
        return result

    def _combine(self, other: Conversion | Commodity, operation: _Arithmetic) -> Self:
        balance = {res: copy(par) for res, par in self.items()}
        for res, par in other.items():
            balance[res] = _apply_coefficients(balance.get(res, 0), par, operation)
        return self._with_balance(balance)

    def __neg__(self) -> Self:
        """Return a conversion with every coefficient negated."""
        return self * -1

    def __add__(self, other: Conversion | Commodity) -> Self:
        """Return the sum of the operands' coefficients for each commodity."""
        return self._combine(other, operator.add)

    def __sub__(self, other: Conversion | Commodity) -> Self:
        """Return the difference of the operands' coefficients for each commodity."""
        return self._combine(other, operator.sub)

    def __mul__(self, times: _Coefficient) -> Self:
        """Scale every coefficient by a scalar or per-period multiplier."""
        return self._with_balance(
            {
                res: _apply_coefficients(par, times, operator.mul)
                for res, par in self.items()
            },
        )

    def __rmul__(self, times: _Coefficient) -> Self:
        """Scale the conversion with the multiplier on the left."""
        return self * times

    def __len__(self):
        """Length of the conversion balance."""
        return len(self.balance)

    def __iter__(self):
        """Iterate over the commodities in the conversion balance."""
        return iter(self.balance)


class PWLConversion(Mapping, _Hash):
    """Piece Wise Linear Conversion."""

    def __init__(
        self,
        conversions: list[Conversion],
        sample: Sample,
        aspect: str = "",
        add: str = "",
        sub: str = "",
    ):
        """Pair the supplied conversions with operating modes for the selected sample."""
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

    @classmethod
    def from_balance(
        cls,
        balance: dict[Modes, Conversion],
        sample: Sample,
    ) -> Self:
        """Creates PWLConversion from balance dict."""
        conv = cls([], sample)
        conv.operation = sample.domain.operation
        conv.balance = balance
        conv.modes = (next(iter(balance))).parent

        return conv

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

    @property
    def name(self) -> str:
        """Name."""
        return f"η_PWL({self.operation}, {self.modes})"

    def balancer(self):
        """Balances all conversions."""
        for conv in self.balance.values():
            conv.balancer()

    def items(self):
        """Items of the conversion balance."""
        return self.balance.items()

    def keys(self):
        """Keys of the conversion balance."""
        return self.balance.keys()

    def values(self):
        """Values of the conversion balance."""
        return self.balance.values()

    def box(self):
        """Consolidates the conversion dict into {resource: par} format."""
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
        """Writes equations for conversion balance."""
        for mode, conv in self.items():
            conv.write(space, time, mode)

    def __len__(self):
        """Length of the conversion balance."""
        return len(self.balance)

    def __iter__(self):
        """Iterate over the modes represented in the piecewise balance."""
        return iter(self.balance)

    def __setitem__(self, key: int | str | Modes, value: Conversion):
        """Assign a conversion to a mode, resolving an integer through the mode group."""
        if isinstance(key, int):
            key = self.modes[key]

        self.balance[key] = value

    def __getitem__(self, key: int | str) -> Conversion:
        """Used to define mode based conversions."""
        if isinstance(key, int):
            key = self.modes[key]

        return self.balance[key]
