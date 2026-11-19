"""Verify the inventory limits that apply when storage is placed."""

import operator

import pytest
from gurobipy import GRB

from energia import Location, Model, Periods, Resource, Storage


@pytest.fixture
def model():
    m = Model()
    m.hour = Periods()
    m.day = 3 * m.hour
    m.site, m.other = Location(), Location()
    m.power = Resource()
    m.battery = Storage(m.power == 0.9)
    return m


def maximum_inventory(inventory):
    inventory.opt(maximize=True)
    assert inventory.program.formulation.Status == GRB.OPTIMAL
    return inventory.output(aslist=True)[0]


@pytest.mark.parametrize(
    "bind, amount, capacity_first, expected",
    [
        (operator.eq, 2, True, 20),
        (operator.eq, 0, True, 0),
        (operator.le, 2, True, 20),
        (operator.le, 0, True, 0),
        (operator.eq, 20, False, 20),
    ],
)
def test_locate_preserves_declared_inventory(
    model, bind, amount, capacity_first, expected
):
    m = model
    capacity = m.battery.capacity(m.site, m.day)
    inventory = m.battery.inventory(m.site, m.day)
    if capacity_first:
        capacity == 10
    bind(inventory, amount)
    if not capacity_first:
        capacity == 10
    record = m.scenario[m.inventory][m.battery.stored][m.site][m.day].copy()

    assert maximum_inventory(inventory) == pytest.approx(expected)
    for _ in range(2):
        m.battery.locate(m.site)
        assert m.scenario[m.inventory][m.battery.stored][m.site][m.day] == record
        assert maximum_inventory(inventory) == pytest.approx(expected)


@pytest.mark.parametrize("declare_lower_bound", [False, True])
def test_locate_caps_inventory_at_capacity_by_default(model, declare_lower_bound):
    m = model
    m.battery.capacity(m.site, m.day) == 10
    inventory = m.battery.inventory(m.site, m.day)
    if declare_lower_bound:
        inventory >= 0.5

    m.battery.locate(m.site)
    assert m.scenario[m.inventory][m.battery.stored][m.site][m.day]["ub"] == 1
    assert maximum_inventory(inventory) == pytest.approx(10)


@pytest.mark.parametrize("other", ["site", "period", "storage"])
def test_inventory_bound_applies_only_to_its_own_domain(model, other):
    m = model
    m.battery.capacity(m.site, m.day) == 10
    if other == "site":
        m.battery.inventory(m.other, m.day) == 0
    elif other == "period":
        m.battery.inventory(m.site, m.hour) == 0
    else:
        m.reserve = Storage(m.power == 0.8)
        m.reserve.capacity(m.site, m.day) == 5
        m.reserve.inventory(m.site, m.day) == 0

    m.battery.locate(m.site)
    assert m.scenario[m.inventory][m.battery.stored][m.site][m.day]["ub"] == 1


def test_hourly_inventory_equality_is_preserved_at_the_balance_period(model):
    m = model
    m.battery.capacity(m.site, m.day) == 10
    m.power.consume(m.site, m.hour) >= 0
    m.power.release(m.site, m.hour) >= 0
    hourly_inventory = m.battery.inventory(m.site, m.hour)
    hourly_inventory == [0, 0, 0]

    m.battery.locate(m.site)
    assert set(m.scenario[m.inventory][m.battery.stored][m.site][m.hour]) == {"eq"}
    hourly_inventory.opt(maximize=True)
    assert hourly_inventory.output(aslist=True) == [0, 0, 0]
