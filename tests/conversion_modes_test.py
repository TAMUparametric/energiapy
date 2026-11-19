"""Consistency of conversion coefficients, operating modes, and constraints."""

import pytest

from energia import Model, Process, Resource
from energia.components.temporal.modes import Modes
from energia.library.examples.energy import design_scheduling_material_modes


def test_balancer_rejects_mismatched_time_series():
    model = Model()
    model.fuel, model.power, model.plant = Resource(), Resource(), Process()
    conversion = model.plant(model.power)
    conversion[model.fuel] = [-1, -2]
    conversion[model.power] = [1, 2, 3]
    with pytest.raises(ValueError, match="inconsistent list lengths"):
        conversion.balancer()


@pytest.mark.parametrize(
    ("mix_parents", "message"),
    [(False, "must account for all modes"), (True, "must belong to the same parent")],
)
def test_piecewise_conversion_requires_a_complete_single_mode_group(
    mix_parents, message
):
    model = Model()
    model.fuel, model.power, model.plant = Resource(), Resource(), Process()
    modes = Modes(size=2)
    modes.name = "production"
    coefficients = {modes[0]: -model.fuel}
    if mix_parents:
        alternate = Modes(size=2)
        alternate.name = "construction"
        coefficients[alternate[1]] = -model.fuel

    with pytest.raises(ValueError, match=message):
        _ = model.plant(model.power) == coefficients


def test_mode_group_collects_its_own_and_child_constraints_once():
    model = design_scheduling_material_modes()
    group = model.wf.construction.modes
    expected_names = set(group.constraints)
    for mode in group:
        assert mode.constraints
        assert set(mode.cons) == {
            getattr(model.program, name) for name in mode.constraints
        }
        expected_names.update(mode.constraints)

    constraints = group.cons
    assert len(constraints) == len(expected_names)
    assert set(constraints) == {getattr(model.program, name) for name in expected_names}
