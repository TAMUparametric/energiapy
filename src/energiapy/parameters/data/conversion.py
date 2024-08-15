"""Conversion for Process Production Modes
"""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from functools import reduce
from typing import TYPE_CHECKING
from ..mode import X
from ..._core._handy._dunders import _Reprs

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsProcess
    from ..._core._aliases._is_input import IsConvInput


@dataclass
class Conversion(_Reprs):
    """
    Represents a conversion process between energy modes.

    Attributes:
        conversion (IsConv): The conversion process.
        process (Process): The process associated with the conversion.
        base (Resource): Resource base, generated post initialization.
        modes (Union[IsNumeric, str]): list of modes, generated post initialization.
        n_modes (int): The number of modes, generated post initialization.
        sell (List[Resource]): Resources discharged, generated post initialization.
        buy (List[Resource]): Resources buy, generated post initialization.
        balance (IsConvBalance): Overall balance attribute generated post initialization.
        involve (List[Resource]): The involve attribute generated post initialization.
        name (str): The name attribute generated post initialization.
    """

    conversion: IsConvInput = field(default=None)
    process: IsProcess = field(default=None)

    def __post_init__(self):

        self.base = list(self.conversion)[0]

        if all(isinstance(i, X) for i in self.conversion[self.base]):
            self.modes = [
                i.personalize(self.process, 'conv') for i in self.conversion[self.base]
            ]

            self.n_modes = len(self.modes)

            self.conversion = {
                self.modes[i]: self.conversion[self.base][i]
                for i in range(self.n_modes)
            }

            self.sold = [self.base] + list(
                reduce(
                    operator.or_,
                    (
                        set(
                            j for j, k in self.conversion[self.base][i].items() if k > 0
                        )
                        for i in self.modes
                    ),
                    set(),
                )
            )
            self.bought = list(
                reduce(
                    operator.or_,
                    (
                        set(
                            j for j, k in self.conversion[self.base][i].items() if k < 0
                        )
                        for i in self.modes
                    ),
                    set(),
                )
            )
            self.balance = {
                i: {self.base: 1, **self.conversion[self.base][i]} for i in self.modes
            }

        else:
            self.modes, self.n_modes = None, 1
            self.sold = [self.base] + [
                i
                for i in self.conversion[self.base]
                if self.conversion[self.base][i] > 0
            ]
            self.bought = [
                i
                for i in self.conversion[self.base]
                if self.conversion[self.base][i] < 0
            ]
            self.balance = {self.base: 1, **self.conversion[self.base]}

        self.involve = list(self.sold) + list(self.bought)
        self.name = f'Conv({self.base},{self.process})'
