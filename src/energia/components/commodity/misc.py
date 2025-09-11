from __future__ import annotations

from dataclasses import dataclass
from operator import is_
from typing import TYPE_CHECKING, Self

# from ..operation.task import Task
from ...modeling.variables.default import Transact, Utilize

# from ..impact.categories import Eco
from .resource import Resource

if TYPE_CHECKING:
    from ..spatial.location import Location


class Cash(Resource, Transact):
    """Same as Economic Impact (Eco)"""

    def __init__(self, *locs: Location, label: str = ''):

        Resource.__init__(self, label=label)
        # Eco.__init__(self)

        # the locations, where this currency applies
        self.locs: Location = locs

        # also applies to all locations nested under the locations
        if locs:
            for loc in self.locs:
                for locin in loc.has:
                    if not locin in self.locs:
                        self.locs += (locin,)

            for loc in self.locs:
                # set the currency on the ensted locations as well
                loc.currency = self

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


@dataclass
class Emission(Resource):
    """Emission"""


@dataclass
class Material(Resource):
    """Materials are Resources, that are used to set up Operations"""


@dataclass
class Land(Resource):
    """Land used by Operations"""


@dataclass
class Package(Resource):
    """Package, discrete"""


@dataclass
class Human(Resource):
    """Human"""


@dataclass
class Mana(Resource):
    """Mana"""


@dataclass
class Etc(Resource):
    """Etc, used for resources that do not fit into the other categories"""
