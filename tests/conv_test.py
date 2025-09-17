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
    _m.proc(_m.c) == {100: _m.a - [20, 30, 40] * _m.b, 200: [20, 30, 40] * _m.b + _m.a}

    return _m


def test_conv(m):
    assert m.conv1.conversion == {m.a: 1, m.b: [-20, -30, -40]}
    assert m.conv2.conversion == {m.b: [20, 30, 40], m.a: -1}
    assert m.conv3.conversion == {m.b: [20, 30, 40], m.a: 1}
    assert m.conv4.conversion == {m.a: 1, m.b: [20, 30, 40]}

    m.conv1.balancer()
    m.conv2.balancer()
    m.conv3.balancer()
    m.conv4.balancer()

    assert m.conv1.conversion == {m.a: [1, 1, 1], m.b: [-20, -30, -40]}
    assert m.conv2.conversion == {m.b: [20, 30, 40], m.a: [-1, -1, -1]}
    assert m.conv3.conversion == {m.b: [20, 30, 40], m.a: [1, 1, 1]}
    assert m.conv4.conversion == {m.a: [1, 1, 1], m.b: [20, 30, 40]}

    m.proc.conv.balancer()
    assert m.proc.conversion == {
        100: {m.c: [1.0, 1.0, 1.0], m.a: [1, 1, 1], m.b: [-20, -30, -40]},
        200: {m.c: [1.0, 1.0, 1.0], m.b: [20, 30, 40], m.a: [1, 1, 1]},
    }
