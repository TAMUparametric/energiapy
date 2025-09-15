"""State Variable"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

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

    def __post_init__(self):
        Aspect.__post_init__(self)
        # decision that adds to the domain
        self.add: Control = None
        # decision that subtracts from the domain
        self.sub: Control = None

        self.mapped_from: list[Domain] = []

    def __setattr__(self, name: str, value: Control | Any):

        if name in ['add', 'sub'] and not value is None:
            # set self as state that the control variable adjusts
            value.state = self

        super().__setattr__(name, value)

    def adddomains(self) -> list[Domain]:
        """Get the domains over which the add variable is defined"""
        return self.tree.get('aspects', 'domains')[self.add]

    def subdomains(self) -> list[Domain]:
        """Get the domains over which the sub variable is defined"""
        return self.tree.get('aspects', 'domains')[self.sub]

    def map_domain(self, domain: Domain, reporting: bool = False):
        """Add a domain to the decision variable"""

        # Write a mapping constraint
        Map(aspect=self, domain=domain, reporting=reporting)
