"""Check weighted totals against expanded and nested temporal models."""

import numpy as np
import pytest
from gana import inf
from gurobipy import GRB

from energia import Model, Periods, Process


def dispatch_model(name, amounts):
    model = Model(name)
    model.study = Periods()
    model.day = model.study / len(amounts)
    model.plant = Process()
    dispatch = model.plant.operate(model.day)
    dispatch == amounts
    return model, dispatch


def test_weighted_dispatch_matches_full_timeline(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    full, full_dispatch = dispatch_model("full", [10, 10, 10, 20])
    reduced, reduced_dispatch = dispatch_model("reduced", [10, 20])

    full_dispatch.opt()
    unweighted = reduced.plant.operate(reduced.study)
    unweighted <= 100
    reduced.program.total = inf(reduced_dispatch.weighted_sum(np.array([3, 1])))
    reduced.program.opt()

    assert full.program.formulation.Status == GRB.OPTIMAL
    assert reduced.program.formulation.Status == GRB.OPTIMAL
    assert full.program.active_objective.X == pytest.approx(50)
    assert reduced.program.active_objective.X == pytest.approx(50)
    assert reduced_dispatch.output(aslist=True) == pytest.approx([10, 20])
    assert unweighted.output(aslist=True) == pytest.approx([30])


def test_weights_align_with_time_inside_other_indices():
    model = Model()
    model.study = Periods()
    model.season = model.study / 2
    model.day = model.season / 2
    model.plant = Process()
    modes = model.Modes(size=3, sample=model.plant.operate(model.day))
    dispatch = model.plant.operate(model.day, modes)

    model.program.total = inf(dispatch.weighted_sum([3, 1, 2, 4]))

    objective = model.program.active_objective.matrix
    assert [objective[variable.n] for variable in dispatch.V()] == pytest.approx(
        [3, 3, 3, 1, 1, 1, 2, 2, 2, 4, 4, 4]
    )


def test_period_weight_defaults_and_can_build_a_bound():
    model, dispatch = dispatch_model("uniform", [10, 20])
    model.day.weight = 4
    model.program.budget = dispatch.weighted_sum() <= 120

    bound = model.program.budget[0]
    assert bound.A == pytest.approx([4, 4])
    assert bound.B == pytest.approx(120)


def test_weighted_sum_uses_horizon_for_untimed_sample():
    model = Model()
    model.study = Periods(weight=2)
    model.plant = Process()
    model.program.total = inf(model.plant.operate.weighted_sum())

    assert model.program.C == pytest.approx([2])


@pytest.mark.parametrize("weights", [[2], [-1, 1], [float("inf"), 1], ["3", 1]])
def test_invalid_occurrence_weights_are_rejected(weights):
    model, dispatch = dispatch_model("invalid", [10, 20])
    before = model.program.n_variables

    with pytest.raises(ValueError, match="occurrence weights|Occurrence weights"):
        dispatch.weighted_sum(weights)

    assert model.program.n_variables == before


def test_occurrence_weights_require_unlagged_periods():
    model, _ = dispatch_model("lagged", [10, 20])
    with pytest.raises(ValueError, match="without a lag"):
        model.plant.operate(-model.day).weighted_sum([3, 1])
