"""Tests for Conversion"""

from itertools import permutations

import pytest
from gurobipy import GRB

from energia import Currency, Model, Periods, Process, Resource


@pytest.fixture
def m():
    _m = Model()
    _m.a = Resource()
    _m.b = Resource()
    _m.c = Resource()
    _m.conv1 = _m.a - [20, 30, 40] * _m.b
    _m.conv2 = [20, 30, 40] * _m.b - _m.a
    _m.conv3 = [20, 30, 40] * _m.b + _m.a
    _m.conv4 = _m.a + [20, 30, 40] * _m.b

    _m.proc = Process()
    _m.proc(_m.c) == [_m.a - [20, 30, 40] * _m.b, [20, 30, 40] * _m.b + _m.a]

    _m.proc2 = Process()
    _m.proc2(_m.c) == [[1, 2, 3] * _m.a, _m.b]

    _ = _m.proc.construction == [_m.conv1, _m.conv2, _m.conv3, _m.conv4]

    _ = _m.proc2.construction == {
        _m.proc2.primary_conversion.modes[0]: _m.conv1,
        _m.proc2.primary_conversion.modes[1]: _m.conv2,
    }

    return _m


def test_conv(m):
    assert {**m.conv1} == {m.a: 1, m.b: [-20, -30, -40]}
    assert {**m.conv2} == {m.b: [20, 30, 40], m.a: -1}
    assert {**m.conv3} == {m.b: [20, 30, 40], m.a: 1}
    assert {**m.conv4} == {m.a: 1, m.b: [20, 30, 40]}

    m.conv1.balancer()
    m.conv2.balancer()
    m.conv3.balancer()
    m.conv4.balancer()

    assert {**m.conv1} == {m.a: [1, 1, 1], m.b: [-20, -30, -40]}
    assert {**m.conv2} == {m.b: [20, 30, 40], m.a: [-1, -1, -1]}
    assert {**m.conv3} == {m.b: [20, 30, 40], m.a: [1, 1, 1]}
    assert {**m.conv4} == {m.a: [1, 1, 1], m.b: [20, 30, 40]}

    m.proc.production.balancer()
    assert {k: {**v} for k, v in m.proc.production.items()} == {
        m.modes[0][0]: {m.c: [1.0, 1.0, 1.0], m.a: [1, 1, 1], m.b: [-20, -30, -40]},
        m.modes[0][1]: {m.c: [1.0, 1.0, 1.0], m.b: [20, 30, 40], m.a: [1, 1, 1]},
    }

    m.proc2.production.balancer()
    assert {k: {**v} for k, v in m.proc2.production.items()} == {
        m.modes[1][0]: {m.c: [1.0, 1.0, 1.0], m.a: [1, 2, 3]},
        m.modes[1][1]: {m.c: 1.0, m.b: 1.0},
    }

    m.proc.construction.balancer()
    assert {k: {**v} for k, v in m.proc.construction.balance.items()} == {
        m.modes[2][0]: {m.a: [1, 1, 1], m.b: [-20, -30, -40]},
        m.modes[2][1]: {m.b: [20, 30, 40], m.a: [-1, -1, -1]},
        m.modes[2][2]: {m.b: [20, 30, 40], m.a: [1, 1, 1]},
        m.modes[2][3]: {m.a: [1, 1, 1], m.b: [20, 30, 40]},
    }

    m.proc2.construction.balancer()
    assert {k: {**v} for k, v in m.proc2.construction.balance.items()} == {
        m.modes[1][0]: {m.a: [1, 1, 1], m.b: [-20, -30, -40]},
        m.modes[1][1]: {m.b: [20, 30, 40], m.a: [-1, -1, -1]},
    }


@pytest.mark.parametrize(
    "basis, second, third", list(permutations(("power", "fuel", "waste")))
)
def test_conversion_resource_order(basis, second, third):
    m = Model()
    m.hour = Periods()
    m.shift = 2 * m.hour
    m.usd = Currency()
    m.power, m.fuel, m.waste = Resource(), Resource(), Resource()
    m.fuel.consume <= 100
    m.power.release(m.hour) >= [2, 4]
    m.waste.release >= 0

    m.plant = Process()
    terms = {"power": 1 * m.power, "fuel": -2 * m.fuel, "waste": 1 * m.waste}
    m.plant(terms[basis]) == terms[second] + terms[third]
    m.plant.operate(m.hour) >= 0
    m.usd.spend(m.fuel.consume) == 3
    m.locate(m.plant)
    m.usd.spend.opt()

    assert m.program.formulation.Status == GRB.OPTIMAL
    assert m.program.formulation.ObjVal == pytest.approx(36)
    assert m.plant.operate(m.hour).output(aslist=True) == pytest.approx([2, 4])
    assert m.fuel.consume.output(aslist=True) == pytest.approx([12])


def test_lagged_output_preserves_input_time():
    m = Model()
    m.hour = Periods()
    m.shift = 2 * m.hour
    m.usd = Currency()
    m.fuel, m.power = Resource(), Resource()
    m.fuel.consume(m.hour) <= [2, 10]
    m.power.release >= 6
    m.plant = Process()
    m.plant(m.power, lag=-m.shift) == -1 * m.fuel
    m.plant.operate(m.hour) >= 0
    m.usd.spend(m.fuel.consume, m.hour) == [1, 3]
    m.locate(m.plant)
    m.usd.spend.opt()

    assert m.program.formulation.Status == GRB.OPTIMAL
    assert m.fuel.consume(m.hour).output(aslist=True) == pytest.approx([2, 4])
    assert m.program.formulation.ObjVal == pytest.approx(14)
