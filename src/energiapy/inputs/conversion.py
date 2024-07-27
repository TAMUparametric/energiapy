from __future__ import annotations

import operator
from dataclasses import dataclass
from functools import reduce
from typing import TYPE_CHECKING

from ..core.base import Dunders
from ..utils.data_utils import get_depth

if TYPE_CHECKING:
    from ..components.operation.process import Process
    from ..type.alias import IsConv


@dataclass(kw_only=True)
class Conversion(Dunders):
    """
    Represents a conversion process between energy modes.

    Attributes:
        conversion (IsConv): The conversion process.
        process (Process): The process associated with the conversion.
        base (Resource): Resource produced, generated post initialization.
        modes (Union[IsNumeric, str]): list of modes, generated post initialization.
        n_modes (int): The number of modes, generated post initialization.
        discharge (List[Resource]): Resources discharged, generated post initialization.
        consume (List[Resource]): Resources consume, generated post initialization.
        balance (IsBalance): Overall balance attribute generated post initialization.
        involve (List[Resource]): The involve attribute generated post initialization.
        name (str): The name attribute generated post initialization.
    """
    conversion: IsConv
    process: Process

    def __post_init__(self):
        self.produce = list(self.conversion)[0]
        # check depth of nested dictionary
        if get_depth(self.conversion) > 2:

            self.modes = list(self.conversion[self.produce])
            self.n_modes = len(self.modes)
            self.discharge = [self.produce] + list(reduce(
                operator.or_, (set(j for j, k in self.conversion[self.produce][i].items() if k > 0) for i in self.modes), set()))
            self.consume = list(reduce(
                operator.or_, (set(j for j, k in self.conversion[self.produce][i].items() if k < 0) for i in self.modes), set()))
            self.balance = {
                i: {self.produce: 1, **self.conversion[self.produce][i]} for i in self.modes}

        elif get_depth(self.conversion) == 2:
            self.modes, self.n_modes = None, 1
            self.discharge = [
                self.produce] + [i for i in self.conversion[self.produce] if self.conversion[self.produce][i] > 0]
            self.consume = [i for i in self.conversion[self.produce]
                            if self.conversion[self.produce][i] < 0]
            self.balance = {self.produce: 1, **self.conversion[self.produce]}

        self.involve = list(self.discharge) + list(self.consume)
        self.name = f'Conv({self.produce.name},{self.process.name})'
