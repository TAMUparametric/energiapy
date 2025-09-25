"""Player"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...core.component import Component
from ...modeling.variables.default import Capacitate, Trade, Transact

if TYPE_CHECKING:
    from ...dimensions.decisionspace import DecisionSpace


@dataclass
class Player(Component, Capacitate, Trade, Transact):
    """Player or Actor, the one taking the decisions
    based on information provided

    Players own certain processes and be responsible for the streams and impact
    caused by their decisions pertaining to this
    """

    def __post_init__(self):
        Component.__post_init__(self)

    @property
    def decisionspace(self) -> DecisionSpace:
        """Tree of the player"""
        return self.model.decisionspace
