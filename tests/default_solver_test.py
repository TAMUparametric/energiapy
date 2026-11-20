"""Compare deterministic objectives across the default solver and Gurobi."""

import json

import pytest
from highspy import Highs

from energia import Model, Resource
from energia.library.examples.energy import (
    design_scheduling_material,
    design_scheduling_material_modes,
    supermarket,
)


def test_default_model_and_expression_objectives():
    model = Model()
    model.labor = Resource(take=True, price=3)
    model.labor.release == 2
    model.cash.spend.obj()
    model.opt()
    assert isinstance(model.program.formulation, Highs)
    assert model.program.active_objective.X == 6
    (2 * model.cash.spend(model.horizon)).opt(maximize=True)
    assert isinstance(model.program.formulation, Highs)
    assert model.program.active_objective.X == -12


@pytest.mark.parametrize(
    ("build", "objectives"),
    [
        (supermarket, ("usd.spend", "co2_vent.release")),
        (design_scheduling_material_modes, ("usd.spend", "gwp.emit")),
        (design_scheduling_material, ("gwp.emit", "usd.spend")),
    ],
)
def test_default_and_gurobi_reach_same_objectives(
    build, objectives, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    default_model, gurobi_model = build(), build()
    for objective in objectives:
        stream, aspect = objective.split(".")
        getattr(getattr(default_model, stream), aspect).opt()
        getattr(getattr(gurobi_model, stream), aspect).opt(using="gurobi")
        assert isinstance(default_model.program.formulation, Highs)
        records = []
        for model, name in ((default_model, "default"), (gurobi_model, "gurobi")):
            path = tmp_path / f"{name}.json"
            model.save(as_type="json", path=path)
            records.append(json.loads(path.read_text()))
        default, gurobi = records
        assert default["status"] == gurobi["status"] == "optimal"
        assert default["formulation_fingerprint"] == gurobi["formulation_fingerprint"]
        assert default["objective_value"] == pytest.approx(gurobi["objective_value"])
