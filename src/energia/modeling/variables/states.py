"""State Variable"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..constraints.balance import Balance
from ..constraints.vmap import Map
from .aspect import Aspect

if TYPE_CHECKING:
    from ..indices.domain import Domain
    from .control import Control


@dataclass
class State(Aspect):
    """
    State Variable
    Operational capacity or set point (utilization)
    """

    add: Control | None = None
    sub: Control | None = None
    bound: State | None = None

    def __post_init__(self):
        Aspect.__post_init__(self)
        self.mapped_from: list[Domain] = []

    def update(self, domain: Domain, reporting: bool = False):
        """Add a domain to the decision variable"""

        # Write a mapping constraint
        Map(aspect=self, domain=domain, reporting=reporting)


@dataclass
class Size(State):
    """
    Capacity State Variable
    Operational capacity
    """

    def __post_init__(self):
        State.__post_init__(self)


@dataclass
class SetPoint(State):
    """
    Set Point State Variable
    Operational set point (utilization)
    """

    def __post_init__(self):
        State.__post_init__(self)


@dataclass
class Consequence(State):
    """Consequence of an action"""

    def __post_init__(self):
        State.__post_init__(self)


@dataclass
class Stream(State):
    """Stream of Resource, also a state variable"""

    def __post_init__(self):
        State.__post_init__(self)

    # def update(self, domain: Domain):
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

    def update(self, domain: Domain, reporting: bool = False):

        Map(aspect=self, domain=domain, reporting=reporting)

        Balance(aspect=self, domain=domain)


@dataclass
class ExoStream(Stream):
    """Exogenous Stream of Resource, also a state variable"""

    def __post_init__(self):
        Stream.__post_init__(self)

    def update(self, domain: Domain, reporting: bool = False):

        Map(aspect=self, domain=domain, reporting=reporting)

        Balance(aspect=self, domain=domain)


@dataclass
class IndStream(Stream):
    """Indicator Stream of Resource, also a state variable"""

    def __post_init__(self):
        Stream.__post_init__(self)

    def update(self, domain: Domain, reporting: bool = False):

        Map(aspect=self, domain=domain, reporting=reporting)
