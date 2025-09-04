"""Impact Variable"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..constraints.vmap import Map
from .state import State

if TYPE_CHECKING:
    from ..indices.domain import Domain


@dataclass
class Impact(State):
    """Consequence of an action"""

    def map_domain(self, domain: Domain):
        """Add a domain to the decision variable"""

        # Write a mapping constraint
        Map(aspect=self, domain=domain)
