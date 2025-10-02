"""State Variable"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..constraints.vmap import Map
from .aspect import Aspect

if TYPE_CHECKING:
    from ..indices.domain import Domain
    from .control import Control


@dataclass
class State(Aspect):
    """State Variable
    Operational capacity or set point (utilization)
    """

    add: Control = None
    sub: Control = None
    bound: State = None

    def __post_init__(self):
        Aspect.__post_init__(self)
        self.mapped_from: list[Domain] = []

    def map_domain(self, domain: Domain, reporting: bool = False):
        """Add a domain to the decision variable"""

        # Write a mapping constraint
        Map(aspect=self, domain=domain, reporting=reporting)
