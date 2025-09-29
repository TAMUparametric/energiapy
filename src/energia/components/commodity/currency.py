"""Currency"""

from dataclasses import dataclass

from operator import is_
from typing import Self

# from ..operation.task import Task
from ...modeling.variables.default import Transact

# from ..impact.categories import Eco
from ._commodity import _Commodity


@dataclass
class Currency(_Commodity, Transact):
    """Same as Economic Impact (Eco)"""

    def __post_init__(self):
        _Commodity.__post_init__(self)

    def howmany(self, cash: Self):
        """Exchange rate basically"""

        if is_(cash, self):
            return 1
        if cash in self.conversion:
            return self.conversion[cash]
        # find a common currency
        if list(self.conversion)[0] == list(cash.conversion)[0]:
            return (
                self.conversion[list(self.conversion)[0]]
                / cash.conversion[list(cash.conversion)[0]]
            )
        raise ValueError(f'{cash} does not have an exchange rate set {self.name}')
