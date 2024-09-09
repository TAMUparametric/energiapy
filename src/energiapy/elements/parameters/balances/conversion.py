"""Conversion for Process Production Modes
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import reduce
from operator import or_
from typing import TYPE_CHECKING

from ....components.temporal.mode import X
from ....core._handy._dunders import _Reprs
from ....core.isalias.inps.isblc import IsCnv

if TYPE_CHECKING:
    from ....components.operation.process import Process


@dataclass
class Conversion(_Reprs):
    """
    The Balance of Resources in a Process with respect to a operated Resource

    Can have multiple Modes which can be declared using the Mode designator (X)

    Attributes:
        conversion (IsConvInput): The conversion process.
        process (IsProcess): The process associated with the conversion.
        operated (IsResource): Resource operated, generated post initialization.
        modes (IsNum, str]): list of modes, generated post initialization.
        n_modes (int): The number of modes, generated post initialization.
        discharged (list[IsResource]): Resources discharged, generated post initialization.
        consumed (list[IsResource]): Resources buy, generated post initialization.
        balance (IsConvBalance): Overall balance attribute generated post initialization.
        involved (list[IsResource]): The involved attribute generated post initialization.
        name (str): The name attribute generated post initialization.
    """

    conversion: IsCnv = field(default=None)
    process: Process = field(default=None)

    def __post_init__(self):

        # The purpose of the Process is to produce the operated Resource
        # The basis if set to one unit of this Resource
        # Cost inputs, for example, are scaled as per this operated
        self.operated = list(self.conversion)[0]

        # if Modes are given, then personalize the Modes to the Process
        if all(isinstance(i, X) for i in self.conversion[self.operated]):

            self.conversion = {
                self.operated: {
                    x.personalize(opn=self.process, attr='conv'): val
                    for x, val in self.conversion[self.operated].items()
                }
            }

            # list of Modes, and the Number of Modes
            self.modes = list(self.conversion[self.operated])
            self.n_modes = len(self.modes)

            # Resources which are dispensed
            # They have a positive value in the conversion dictionary, includes the operated
            self.discharged = [self.operated] + list(
                reduce(
                    or_,
                    (
                        set(
                            res
                            for res, val in self.conversion[self.operated][x].items()
                            if val > 0
                        )
                        for x in self.modes
                    ),
                    set(),
                )
            )
            # Resources which are consumed
            # They have a negative value in the conversion dictionary
            self.consumed = list(
                reduce(
                    or_,
                    (
                        set(
                            res
                            for res, val in self.conversion[self.operated][x].items()
                            if val < 0
                        )
                        for x in self.modes
                    ),
                    set(),
                )
            )

            # Balance provides a dictionary with the operated as a key and value of 1
            self.balance = {
                x: {self.operated: 1, **self.conversion[self.operated][x]} for x in self.modes
            }

        else:
            # If no modes set None, and set the number of modes to 1
            self.modes, self.n_modes = None, 1

            # Just like above but simpler
            self.discharged = [self.operated] + [
                res
                for res in self.conversion[self.operated]
                if self.conversion[self.operated][res] > 0
            ]
            self.consumed = [
                res
                for res in self.conversion[self.operated]
                if self.conversion[self.operated][res] < 0
            ]
            self.balance = {self.operated: 1, **self.conversion[self.operated]}

        # The resources involvedd in the conversion process
        self.involved = list(self.discharged) + list(self.consumed)

        self.name = f'Conv({self.operated},{self.process})'
