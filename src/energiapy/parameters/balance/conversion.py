"""Conversion for Process Production Modes
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import reduce
from operator import or_
from typing import TYPE_CHECKING

from ..._core._handy._dunders import _Reprs
from ..designators.mode import X

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsProcess
    from ..._core._aliases._is_input import IsConvInput


@dataclass
class Conversion(_Reprs):
    """
    The Balance of Resources in a Process with respect to a Base Resource

    Can have multiple Modes which can be declared using the Mode designator (X)

    Attributes:
        conversion (IsConvInput): The conversion process.
        process (IsProcess): The process associated with the conversion.
        base (IsResource): Resource base, generated post initialization.
        modes (Union[IsNumeric, str]): list of modes, generated post initialization.
        n_modes (int): The number of modes, generated post initialization.
        sold (List[IsResource]): Resources discharged, generated post initialization.
        bought (List[IsResource]): Resources buy, generated post initialization.
        balance (IsConvBalance): Overall balance attribute generated post initialization.
        involved (List[IsResource]): The involved attribute generated post initialization.
        name (str): The name attribute generated post initialization.
    """

    conversion: IsConvInput = field(default=None)
    process: IsProcess = field(default=None)

    def __post_init__(self):

        # The purpose of the Process is to produce the base Resource
        # The basis if set to one unit of this Resource
        # Cost inputs, for example, are scaled as per this base
        self.base = list(self.conversion)[0]

        # if Modes are given, then personalize the Modes to the Process
        if all(isinstance(i, X) for i in self.conversion[self.base]):

            self.conversion = {
                self.base: {
                    i.personalize(opn=self.process, attr='conv'): j
                    for i, j in self.conversion[self.base].items()
                }
            }

            # List of Modes, and the Number of Modes
            self.modes = list(self.conversion[self.base])
            self.n_modes = len(self.modes)

            # Resources which are dispensed
            # They have a positive value in the conversion dictionary, includes the base
            self.sold = [self.base] + list(
                reduce(
                    or_,
                    (
                        set(
                            res
                            for res, val in self.conversion[self.base][x].items()
                            if val > 0
                        )
                        for x in self.modes
                    ),
                    set(),
                )
            )
            # Resources which are consumed
            # They have a negative value in the conversion dictionary
            self.bought = list(
                reduce(
                    or_,
                    (
                        set(
                            res
                            for res, val in self.conversion[self.base][x].items()
                            if val < 0
                        )
                        for x in self.modes
                    ),
                    set(),
                )
            )

            # Balance provides a dictionary with the base as a key and value of 1
            self.balance = {
                x: {self.base: 1, **self.conversion[self.base][x]} for x in self.modes
            }

        else:
            # If no modes set None, and set the number of modes to 1
            self.modes, self.n_modes = None, 1

            # Just like above but simpler
            self.sold = [self.base] + [
                res
                for res in self.conversion[self.base]
                if self.conversion[self.base][res] > 0
            ]
            self.bought = [
                res
                for res in self.conversion[self.base]
                if self.conversion[self.base][res] < 0
            ]
            self.balance = {self.base: 1, **self.conversion[self.base]}

        # The resources involvedd in the conversion process
        self.involved = list(self.sold) + list(self.bought)

        self.name = f'Conv({self.base},{self.process})'
