"""Tests for Conversion"""

import pytest

from energia import Resource, Model, Process


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
        _m.proc2.production.modes[0]: _m.conv1,
        _m.proc2.production.modes[1]: _m.conv2,
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
