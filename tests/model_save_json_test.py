"""Exercise Gana's JSON format through Energia's save API."""

import json

import pytest

from energia import Model, Resource


def spend_model(name, demand):
    """Build a model with a fixed labor demand and spending objective."""
    model = Model(name)
    model.labor = Resource(take=True, price=3)
    model.labor.release == demand
    model.cash.spend.obj()
    return model


def test_json_round_trip_for_selected_result(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    original = spend_model("original", demand=2)
    original.program.opt()
    original.cash.spend.opt(maximize=True)
    assert original.program.active_objective.X == -6.0

    path = tmp_path / "first.json"
    original.save(as_type="json", path=path, n_sol=0)
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["format_version"] == 1
    assert record["objective_value"] == 6.0

    rebuilt = spend_model("rebuilt", demand=2)
    rebuilt.program.import_solution(path)
    assert rebuilt.program.active_objective.X == 6.0
    assert rebuilt.program.solution.asdict() == original.program.solutions[0].asdict()
    assert rebuilt.program.solution.asdict()["spend"] == [6.0, 6.0]
    assert rebuilt.program.formulations == {}


def test_json_default_destination_and_changed_bound(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    original = spend_model("original", demand=2)
    original.program.opt()
    original.save(as_type="json")

    path = tmp_path / "original.json"
    assert path.is_file()
    assert not (tmp_path / "original.energia").exists()

    changed = spend_model("changed", demand=3)
    with pytest.raises(ValueError, match="fingerprint does not match"):
        changed.program.import_solution(path)
    assert changed.program.solutions == changed.program.X == {}
    assert changed.program.active_objective.X is None
