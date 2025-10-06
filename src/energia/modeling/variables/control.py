"""Control Variable"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from ..constraints.vmap import Map
from .aspect import Aspect

if TYPE_CHECKING:
    from ..indices.domain import Domain
    from .states import State


@dataclass
class Control(Aspect):
    """Some action to be performed by a component
    that adjusts a state variable
    can have a consequence (Impact)
    or elicit a motion (Stream) that has a consequence (Impact)
    """

    def __post_init__(self):
        Aspect.__post_init__(self)

        # a state that is being controlled
        self.state: State = None
        # a stream that is being controlled
        self.stream: Self = None
        # an impact that is being controlled
        self.impact: Self = None
        # what increase the state/impact/stream
        self.more: Self = None
        # what decreases the state/impact/stream
        self.less: Self = None

    def map_domain(self, domain: Domain):
        """Add a domain to the decision variable"""

        # Write a mapping constraint
        Map(aspect=self, domain=domain)
