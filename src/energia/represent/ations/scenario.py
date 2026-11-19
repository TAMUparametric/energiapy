"""Scenario."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..._core._hash import _Hash
from ...utils.dictionary import merge_trees

if TYPE_CHECKING:
    from ...modeling.indices.sample import Sample
    from ...represent.model import Model


class Scenario(_Hash):
    """Scenario representation."""

    def __init__(self, model: Model):
        """Create an empty parameter tree for the supplied model."""
        self.model = model
        self.name = rf"Scenario({self.model})"

        self._ = {}

    def update(
        self,
        sample: Sample,
        rel: str,
        parameter: float | list[float],
    ):
        """Update the scenario representation."""
        self._ = merge_trees(
            self._,
            {sample.aspect: sample.domain.param_tree(parameter, rel)},
        )

    def __getitem__(self, item):
        """
        Look up the parameter tree for a modeling aspect.

        .. admonition:: Example

            .. code-block:: python

                from energia import Location, Model, Periods, Process

                m = Model()
                m.day, m.site, m.pump = Periods(), Location(), Process()
                m.pump.capacity(m.site, m.day) == 5
                limits = m.scenario[m.capacity][m.pump][m.site][m.day]
                assert limits["eq"] == 5
        """
        return self._[item]
