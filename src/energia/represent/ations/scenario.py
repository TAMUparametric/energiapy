"""Scenario"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..._core._hash import _Hash
from ...utils.dictionary import merge_trees

if TYPE_CHECKING:
    from ...modeling.indices.sample import Sample
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

        self._ = {}


    def update(
        self,
        sample: Sample,
        # domain: Domain,
        rel: str,
        parameter: float | list[float],
    ):
        """Update the scenario representation"""

        self._ = merge_trees(
            self._, {sample.aspect: sample.domain.param_tree(parameter, rel)}
        )


    def __getitem__(self, item):
        return self._[item]
