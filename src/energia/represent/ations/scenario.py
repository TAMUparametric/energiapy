"""Scenario"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..._core._hash import _Hash

if TYPE_CHECKING:
    from ..modeling.indices.domain import Domain
    from ..modeling.variables.aspect import Aspect
    from ..modeling.variables.sample import Sample
    from ..represent.model import Model


class Scenario(_Hash):
    """Scenario representation"""

    def __init__(self, model: str):

        self.model: Model = model
        self.name = rf"Scenario({self.model})"
        # Bounds, upper, lower, and equality
        self.ubs: dict[Aspect] = {}
        self.lbs = {}
        self.eqs = {}

        # Calculations
        self.calcs = {}

    def _update(
        self,
        sample: Sample,
        domain: Domain,
        tree: dict,
    ):
        """Update the scenario representation"""
