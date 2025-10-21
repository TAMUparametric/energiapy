"""Conversion"""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Self

from ..._core._name import _Name
from ...components.temporal.lag import Lag
from ...components.temporal.modes import Modes

if TYPE_CHECKING:
    from gana.block.program import Prg

    from ...components.commodity.resource import Resource
    from ...components.operation._operation import _Operation
    from ...components.temporal.periods import Periods
    from ...represent.model import Model
    from ..variables.sample import Sample


class Conversion(_Name):
    """
    Processes convert one Resource to another Resource
    Conversion provides the conversion of resources

    :param resource: Resource that is balanced
    :type resource: Resource
    :param operation: Process or Storage that serves as primary spatial index
    :type operation: Process | Storage
    :param bind: Sample that is used to define the conversion
    :type bind: Sample

    :ivar name: Name of the component, generated based on the operation.
    :vartype name: str
    :ivar base: Basis Resource, usually has a value 1 in the conversion matrix, set using __call__. Defaults to None.
    :vartype base: Resource
    :ivar conversion: {Resources: conversion}. Defaults to {}, set using __eq__.
    :vartype conversion: dict[Resource : int | float]
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
        resource: Resource | None = None,
        operation: _Operation | None = None,
        bind: Sample | None = None,
    ):

        self.resource = resource
        self.operation = operation
        self.bind = bind

        # _Name.__init__(self, label="")

        # self.name = f"η({self.operation})"
        self.basis: Resource | None = None
        self.lag: Lag | None = None
        self.periods: Periods | None = None

        # if piece wise linear conversion is provided
        self.pwl: bool = False

        # this is holds a mode for the conversion to be appended to
        self._mode: int | str | None = None

        # modes if PWL conversion is defined
        # or if multiple modes are defined
        self._modes: Modes | None = None

        # if the keys are converted into Modes
        self.modes_set: bool = False
        self.balance: dict[Resource, int | float | list[int | float]] = {}

    @property
    def name(self) -> str:
        """Name"""
        return f"η({self.operation}, {self.basis})"

    @property
    def modes(self) -> Modes:
        """Modes of the operation"""
        if self._modes is None:
            n_modes = len(self.balance)
            modes_name = f"bin{len(self.model.modes)}"

            setattr(self.model, modes_name, Modes(n_modes=n_modes, bind=self.bind))

            self._modes = self.model.modes[-1]

        return self._modes

    @cached_property
    def model(self) -> Model:
        """energia Model"""

        if self.pwl:
            _conversion = self.balance[next(iter(self.balance))]
        else:
            _conversion = self.balance

        return next((i.model for i in _conversion), None)

    @cached_property
    def program(self) -> Prg:
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

        if self.pwl:
            for mode, conv in self.balance.items():
                self.balance[mode] = _balancer(conv)

            if isinstance(next(iter(self.balance)), Modes):
                self.modes_set = True

        else:
            self.balance = _balancer(self.balance)

    def __getitem__(self, mode: int | str) -> Self:
        """Used to define mode based conversions"""
        self._mode = mode
        return self

    def __call__(self, basis: Resource | Conversion, lag: Lag = None) -> Self:
        # sets the basis
        if isinstance(basis, Conversion):
            # if a Conversion is provided (parameter*Resource)
            # In this case the associated conversion is not 1
            # especially useful if Process is scaled to consumption of a resource
            # i.e. basis = -1*Resource
            self.balance = {**self.balance, **basis.balance}
            self.basis = next(iter(self.balance))

        else:
            # if a Resource is provided (Resource)
            # implies that the conversion is 1
            # i.e the Process is scaled to one unit of this Resource produced
            self.basis = basis
            self.balance = {basis: 1.0, **self.balance}

        if lag:
            self.lag = lag

        return self

    def __eq__(self, other: Conversion | int | float | dict[int | float, Conversion]):
        # cons = []

        if isinstance(other, Conversion) and other.basis is not None:
            self.basis = other.basis

        if isinstance(other, (int, float)):
            # this is used for inventory conversion
            # when not other resource besides the one being inventoried is involved

            self.balance = {**self.balance, self.resource: -1.0 / float(other)}

        elif isinstance(other, dict):

            key = next(iter(other.keys()))

            if isinstance(key, Modes):
                # conversion modes can collate
                # for example resource conversion modes and material conversion modes
                self.modes_set = True
                self._modes = key.parent

            # this is when there is a proper resource conversion
            # -20*res1 = 10*res2 for example
            self.balance = {k: {**self.balance, **v.balance} for k, v in other.items()}
            self.pwl = True

        # this would be a Conversion or Resource
        elif self._mode is not None:
            self.balance[self._mode] = other.balance
            if not self.pwl:
                self.pwl = True
            self._mode = None
        else:

            self.balance: dict[Resource, int | float] = {
                **self.balance,
                **other.balance,
            }

        self.model.convmatrix[self.operation] = self.balance

    # these update the conversion of the resource (self.conversion)
    def __add__(self, other: Conversion) -> Self:
        if isinstance(other, Conversion):
            self.balance = {**self.balance, **other.balance}
            return self
        self.balance = {**self.balance, other: 1}
        return self

    def __sub__(self, other: Conversion) -> Self:
        if isinstance(other, Conversion):
            self.balance = {
                **self.balance,
                **{res: -1 * par for res, par in other.balance.items()},
            }
            return self
        self.balance = {**self.balance, other: -1}
        return self

    def __mul__(self, times: int | float | list) -> Self:
        if isinstance(times, list):
            self.balance = {
                res: [par * i for i in times] for res, par in self.balance.items()
            }
        else:
            self.balance = {res: par * times for res, par in self.balance.items()}
        return self

    def __rmul__(self, times) -> Self:
        return self * times

    def __truediv__(self, periods: Periods) -> Self:
        self.periods = periods
        return self
