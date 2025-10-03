"""Stream Variable"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..constraints.balance import Balance
from ..constraints.vmap import Map
from .state import State

if TYPE_CHECKING:
    from ..indices.domain import Domain


@dataclass
class Stream(State):
    """Stream of Resource, also a state variable"""

    def __post_init__(self):
        State.__post_init__(self)

    # def map_domain(self, domain: Domain):
    #     """Add a domain to the decision variable"""

    #     # Write a mapping constraint

    #     Map(aspect=self, domain=domain)

    #     # Write/Update, the stream balance
    #     Balance(aspect=self, domain=domain)


@dataclass
class EndoStream(Stream):
    """Endogenous Stream of Resource, also a state variable"""

    def __post_init__(self):
        Stream.__post_init__(self)

    def map_domain(self, domain: Domain):

        Map(aspect=self, domain=domain)

        Balance(aspect=self, domain=domain)


@dataclass
class ExoStream(Stream):
    """Exogenous Stream of Resource, also a state variable"""

    def __post_init__(self):
        Stream.__post_init__(self)

    def map_domain(self, domain: Domain):

        Map(aspect=self, domain=domain)

        Balance(aspect=self, domain=domain)


@dataclass
class IndStream(Stream):
    """Indicator Stream of Resource, also a state variable"""

    def __post_init__(self):
        Stream.__post_init__(self)

    def map_domain(self, domain: Domain):

        Map(aspect=self, domain=domain)
