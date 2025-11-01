"""Scenario"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..._core._hash import _Hash
from ...utils.dictionary import merge_trees

if TYPE_CHECKING:
    from ...modeling.variables.sample import Sample
    from ...represent.model import Model


class Scenario(_Hash):
    """Scenario representation"""

    def __init__(self, model: Model):

        self.model = model
        self.name = rf"Scenario({self.model})"

        # Bounds, upper, lower, and equality
        self.ubs = {}
        self.lbs = {}
        self.eqs = {}

        # Calculations
        self.calcs = {}
        # incidental calculations
        self.inc_calcs = {}

    @property
    def _(self):
        """Returns the scenario representation as a dictionary"""
        return {
            "ubs": self.ubs,
            "lbs": self.lbs,
            "eqs": self.eqs,
            "calcs": self.calcs,
            "inc_calcs": self.inc_calcs,
        }

    def update(
        self,
        sample: Sample,
        # domain: Domain,
        rel: str,
        parameter: float | list[float],
    ):
        """Update the scenario representation"""

        if rel == 'ub':
            self.ubs = merge_trees(
                self.ubs, {sample.aspect: sample.domain.param_tree(parameter)}
            )

        elif rel == 'lb':
            self.lbs = merge_trees(
                self.lbs, {sample.aspect: sample.domain.param_tree(parameter)}
            )
        elif rel == 'eq':
            self.eqs = merge_trees(
                self.eqs, {sample.aspect: sample.domain.param_tree(parameter)}
            )

        elif rel == 'calc':
            self.calcs = merge_trees(
                self.calcs, {sample.aspect: sample.domain.param_tree(parameter)}
            )
        elif rel == 'inc_calc':
            self.inc_calcs = merge_trees(
                self.inc_calcs, {sample.aspect: sample.domain.param_tree(parameter)}
            )
