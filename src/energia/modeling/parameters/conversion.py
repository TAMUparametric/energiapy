"""Conversion"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from ...components.temporal.lag import Lag
from ...core.name import Name
from ...components.temporal.modes import Modes

if TYPE_CHECKING:
    from gana.block.program import Prg

    from ...components.commodity.resource import Resource
    from ...components.measure.unit import Unit
    from ...components.operation._operation import _Operation
    from ...components.operation.process import Process
    from ...components.operation.storage import Storage
    from ...components.temporal.periods import Periods
    from ...represent.model import Model
    from ...modeling.constraints.bind import Bind


@dataclass
class Conversion(Name):
    """Processes convert one Resource to another Resource

    Conversion provides the conversion of resources

    Attributes:
        label (str): Label of the component, used for plotting. Defaults to None.
        process (Process): Process that converts Resources. Defaults to None.
        storage (Storage): Storage that stores Resources. Defaults to None.
        resource (Resource): Resource that is balanced. Defaults to None.
        name (str): generated as η(process).
        operation (Process | Storage): Process or Storage that serves as primary spatial index.
        base (Resource): Basis Resource, usually has a value 1 in the conversion matrix, set using __call__. Defaults to None.
        conversion (dict[Resource : int | float]): {Resources: conversion}. Defaults to {}, set using __eq__.
        lag (Lag): Temporal lag (processing time) for conversion, set using __getitem__. Defaults to None.

    Raises:
        TypeError: If __getitem__ input is not of type Lag.

    Note:
        - name and operation are generated post init
        - base (__call__), conversion (__eq__), lag (__getitem__) are defined as the program is built
        - Storage contains two processes (charge and discharge), hence is provided separately

    """

    resource: Resource = None
    operation: _Operation = None
    bind: Bind = None

    def __post_init__(self):
        self.name = f'η({self.operation})'
        self.base: Resource = None
        self.conversion: dict[Resource, int | float | list[int | float]] = {}
        self.lag: Lag = None
        self.period: Periods = None

        # if piece wise linear conversion is provided
        self.pwl: bool = False

        # this is holds a mode for the conversion to be appended to
        self._mode: int | str = None

        # modes if PWL conversion is defined
        # or if multiple modes are defined
        self._modes: Modes = None

    @property
    def modes(self) -> Modes:
        """Modes of the operation"""
        if self._modes is None:
            n_modes = len(self.conversion)
            modes_name = f'bin{len(self.model.modes)}'

            setattr(self.model, modes_name, Modes(n_modes=n_modes, bind=self.bind))

            self._modes = self.model.modes[-1]

        return self._modes

    @property
    def model(self) -> Model:
        """energia Model"""
        return self.operation.model

    @property
    def program(self) -> Prg:
        """gana Program"""
        return self.operation.program

    def balancer(self):
        """Checks if there is a list in the conversion
        If yes, tries to make everything consistent
        """

        def _balancer(conversion: dict):

            # check if lists are provided
            check_list = {res: False for res in conversion.keys()}
            # check lengths of the list, for parameter the length is 1
            check_len = {res: 1 for res in conversion.keys()}

            for res, par in conversion.items():
                if isinstance(par, list):
                    check_list[res] = True
                    check_len[res] = len(par)

            # check if all the list lens are the same
            lengths = set([i for i in check_len.values() if i > 1])

            if len(lengths) > 1:
                # if there are different lengths, raise an error
                raise ValueError(
                    f'Conversion: {self.name} has inconsistent list lengths: {lengths}'
                )

            if any(check_list.values()):
                length = list(lengths)[0]
                # if any of the values are a list
                #
                for res, par in conversion.items():
                    if isinstance(par, (float, int)):
                        conversion[res] = [par] * length
            return conversion

        if self.pwl:
            for mode, conv in self.conversion.items():
                self.conversion[mode] = _balancer(conv)

        else:
            self.conversion = _balancer(self.conversion)

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
            self.conversion = {**self.conversion, **basis.conversion}
            self.base = list(self.conversion)[0]

        else:
            # if a Resource is provided (Resource)
            # implies that the conversion is 1
            # i.e the Process is scaled to one unit of this Resource produced
            self.base = basis
            self.conversion = {basis: 1.0, **self.conversion}

        if lag:
            self.lag = lag

        return self

    def __eq__(self, other: Conversion | int | float | dict[int | float, Conversion]):
        # cons = []

        if isinstance(other, (int, float)):
            # this is used for inventory conversion
            # when not other resource besides the one being inventoried is involved

            self.conversion = {**self.conversion, self.resource: -1.0 * float(other)}

        elif isinstance(other, dict):

            # this is when there is a proper resource conversion
            # -20*res1 = 10*res2 for example
            self.conversion = {
                k: {**self.conversion, **v.conversion} for k, v in other.items()
            }
            self.pwl = True

        else:
            # this would be a Conversion or Resource
            if self._mode is not None:
                self.conversion[self._mode] = other.conversion
                if not self.pwl:
                    self.pwl = True
                self._mode = None
            else:

                self.conversion: dict[Resource, int | float] = {
                    **self.conversion,
                    **other.conversion,
                }

        self.model.convmatrix[self.operation] = self.conversion

    # these update the conversion of the resource (self.conversion)
    def __add__(self, other: Conversion) -> Self:
        if isinstance(other, Conversion):
            self.conversion = {**self.conversion, **other.conversion}
            return self
        self.conversion = {**self.conversion, other: 1}
        return self

    def __sub__(self, other: Conversion) -> Self:
        if isinstance(other, Conversion):
            self.conversion = {
                **self.conversion,
                **{res: -1 * par for res, par in other.conversion.items()},
            }
            return self
        self.conversion = {**self.conversion, other: -1}
        return self

    def __mul__(self, times: int | float | list) -> Self:
        if isinstance(times, list):
            self.conversion = {
                res: [par * i for i in times] for res, par in self.conversion.items()
            }
        else:
            self.conversion = {res: par * times for res, par in self.conversion.items()}
        return self

    def __rmul__(self, times) -> Self:
        return self * times

    def __truediv__(self, period: Periods) -> Self:
        self.period = period
        return self
