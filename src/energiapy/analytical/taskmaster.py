"""Task Master relates attributes to Elements
"""

from __future__ import annotations

from ..core.energia import Energia

from .decision import Decision


class Chanakya(Energia):
    """Taskmaster, collects decisions"""

    def __init__(self, name: str):
        super().__init__(name)

        self.decisions: list[Decision] = []

    def __setattr__(self, name: str, decision: Decision):

        if isinstance(decision, Decision):
            decision.name = name
            decision.pos = +decision
            decision.neg = -decision
            self.decisions.append(decision)

        super().__setattr__(name, decision)
