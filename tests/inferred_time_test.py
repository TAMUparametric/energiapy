"""Solver indices and time sums for periods defined by subdivision."""

import pytest
from gurobipy import GRB

from energia import Model, Periods, Process


@pytest.mark.parametrize("coarse_bound_first", [False, True])
def test_nested_time_sums(coarse_bound_first):
    model = Model()
    model.day = Periods()
    model.shift = model.day / 2
    model.hour = model.shift / 3
    model.plant = Process()
    operate = model.plant.operate
    if coarse_bound_first:
        operate(model.day) <= 100
        operate(model.shift) <= 100
    operate(model.hour) == [1, 2, 3, 4, 5, 6]
    if not coarse_bound_first:
        operate(model.shift) <= 100
        operate(model.day) <= 100
    operate(model.day).opt()

    assert model.program.formulation.Status == GRB.OPTIMAL
    assert operate(model.shift).output(aslist=True) == pytest.approx([6, 15])
    assert operate(model.day).output(aslist=True) == pytest.approx([21])


def test_profile_length_after_horizon_index_is_used():
    model = Model()
    horizon = model.horizon
    already_used = horizon.i
    fine = model.time.find(93)

    assert fine.I == (already_used, fine.i)
    assert len(fine.i) == 93
    assert len(already_used) == 1
    assert model.time.find(93) is fine


def test_partial_period_does_not_match_a_whole_profile():
    model = Model()
    model.day = Periods()
    model.partial = model.day / 2.5
    half_day = model.time.find(2)

    assert half_day is not model.partial
    assert len(half_day.i) == 2
    with pytest.raises(ValueError, match="nonintegral"):
        _ = model.partial.i
