"""Operating bounds on time scales introduced by a storage conversion."""

import operator

import pytest
from gurobipy import GRB

from energia import Location, Model, Periods, Process, Resource, Storage


@pytest.fixture
def model():
    m = Model()
    m.hour = Periods()
    m.day = 3 * m.hour
    m.site = Location()
    m.power = Resource()
    m.battery = Storage(m.power == 0.9)
    m.battery.capacity(m.site, m.day) == 100
    for period in (m.day, m.hour):
        m.power.consume(m.site, period) <= 100
        m.power.release(m.site, period) <= 100
    m.battery.inventory(m.site, m.day) <= 0.5
    m.battery.inventory(m.site, m.hour).obj(maximize=True)
    return m


def placement_result(m):
    m.battery.locate(m.site)
    with m.program.gurobi() as solver:
        solver.Params.OutputFlag = 0
        fingerprint = solver.Fingerprint
        charge = m.battery.charge.operate(m.site, m.hour).V()
        hourly = [solver.getVarByName(variable.mps()) for variable in charge]
        maxima = []
        for objective in (hourly[0], sum(hourly)):
            solver.setObjective(objective, GRB.MAXIMIZE)
            solver.optimize()
            assert solver.Status == GRB.OPTIMAL
            maxima.append(solver.ObjVal)
    return fingerprint, maxima


@pytest.mark.parametrize(
    "daily, hourly, first_hour, total, expect_hourly_bound",
    [
        (2, None, 10, 20, True),
        (1, None, 10, 10, False),
        (0.5, None, 5, 5, False),
        (0, None, 0, 0, False),
        (2, 0, 0, 0, True),
        (2, 0.5, 5, 15, True),
        (2, 2, 20, 20, True),
    ],
)
def test_first_placement_respects_both_scales(
    model, daily, hourly, first_hour, total, expect_hourly_bound
):
    m = model
    for process in (m.battery.charge, m.battery.discharge):
        process.capacity(m.site, m.day) == 10
        process.operate(m.site, m.day) <= daily
        if hourly is not None:
            process.operate(m.site, m.hour) <= hourly
    first = placement_result(m)
    assert first[1] == pytest.approx([first_hour, total])
    assert placement_result(m) == first
    for process in (m.battery.charge, m.battery.discharge):
        name = f"operate_{process}_site_hour_ub"
        assert (name in m.program.names_constraint_sets) == expect_hourly_bound


@pytest.mark.parametrize("relation", [operator.eq, operator.le])
def test_absolute_daily_bound_declared_before_charge_capacity(model, relation):
    m = model
    charge = m.battery.charge
    relation(charge.operate(m.site, m.day), 1)
    charge.capacity(m.site, m.day) == 0.5
    first = placement_result(m)
    assert first[1] == pytest.approx([0.5, 1])
    assert placement_result(m) == first


def test_hourly_equality_takes_precedence_over_default(model):
    m = model
    charge = m.battery.charge
    charge.capacity(m.site, m.day) == 10
    charge.operate(m.site, m.day) <= 2
    charge.operate(m.site, m.hour) == [2, 0, 0]
    first = placement_result(m)
    assert first[1] == pytest.approx([20, 20])
    assert placement_result(m) == first
    assert "operate_battery.charge_site_hour_ub" not in m.program.names_constraint_sets


@pytest.mark.parametrize(
    "daily, hourly_needed", [([0.5, 1], False), ([0.5, 2], True), (None, False)]
)
def test_operating_bound_uses_actual_time_sums(daily, hourly_needed):
    m = Model()
    m.hour = Periods()
    m.day = 2 * m.hour
    m.week = 2 * m.day
    m.site = Location()
    m.fuel, m.power = Resource(), Resource()
    m.fuel.consume(m.site, m.hour) <= 100
    m.power.release(m.site, m.hour) <= 100
    m.plant = Process()
    m.plant(m.power) == -m.fuel
    m.plant.capacity(m.site, m.week) == 10
    if daily is None:
        m.plant.operate(m.site, m.week) <= 1
        m.plant.operate(m.site, m.day) >= 0
    else:
        m.plant.operate(m.site, m.day) <= daily

    m.plant.locate(m.site)
    names = tuple(m.program.names_constraint_sets)
    assert "operate_plant_site_hour_to__plant_site_day_tmap" in names
    assert ("operate_plant_site_hour_ub" in names) == hourly_needed
    m.plant.locate(m.site)
    assert tuple(m.program.names_constraint_sets) == names


def test_reporting_bound_does_not_replace_charge_capacity(model):
    m = model
    charge = m.battery.charge
    charge.capacity(m.site, m.day) == 0.5
    charge.operate(m.site, m.day).x <= 1
    first = placement_result(m)
    assert first[1] == pytest.approx([0.5, 1])
    assert placement_result(m) == first


def test_partial_row_set_cannot_establish_a_bound_for_all_periods(model):
    m = model
    charge = m.battery.charge
    charge.capacity(m.site, m.day) == 10
    charge.operate(m.site, m.hour) <= 1
    rows = getattr(m.program, "operate_battery.charge_site_hour_ub")
    hourly = charge.operate(m.site, m.hour)
    reference = hourly.V() - hourly.Vb()
    assert not charge._implies_capacity(next(iter(rows)), reference)
