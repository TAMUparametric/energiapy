"""HiGHS solves through Energia's deterministic objective APIs."""

import json

import pytest
from highspy import HighsModelStatus

from energia import Model, Resource
from energia.library.examples.energy import scheduling


def test_highs_solves_scheduling_model_and_saves_dispatch(tmp_path):
    model = scheduling()
    model.usd.spend.obj()
    model.opt(using="highs")
    assert model.program.formulation.getModelStatus() == HighsModelStatus.kOptimal
    assert model.wf.operate(model.time.densest).output(aslist=True) == pytest.approx(
        [60, 70, 100, 30]
    )
    model.save(as_type="json", path=tmp_path / "dispatch.json")
    record = json.loads((tmp_path / "dispatch.json").read_text())
    assert record["objective_value"] == pytest.approx(1_081_000)
    assert record["status"] == "optimal"


def test_highs_sample_and_combined_objective():
    model = Model()
    model.labor = Resource(take=True, price=3)
    model.labor.release == 2
    model.cash.spend.opt(using="highs")
    assert model.program.active_objective.X == 6
    spend = model.cash.spend(model.horizon)
    (2 * spend).opt(maximize=True, using="highs")
    assert model.program.active_objective.X == -12
    assert model.program.n_solutions == 2
