import pytest

from energia import Resource, Model, Periods, Location, Process, Unit
from operator import is_


@pytest.fixture
def m():
    _m = Model("test")
    _m.t = Periods()
    _m.l = Location()
    _m.r = Resource()
    _m.r_in = Resource()
    _m.r_out = Resource()
    _m.r.consume <= 100
    _m.p = Process()
    _m.p(_m.r_out) == -_m.r_in
    return _m


def test_props(m):

    assert is_(m.r.model, m)
    assert is_(m.r.horizon, m.t)
    assert is_(m.r.network, m.l)
    assert is_(m.r.problem, m.problem)
    assert is_(m.r.time, m.time)
    assert is_(m.r.space, m.space)

    # check naming, hashing, str
    assert str(m.space) == "Space(test)"
    assert repr(m.space) == "Space(test)"
    assert hash(m.space) == hash("Space(test)")
    assert m.t.cons == m.constraint_sets
    assert not m.r.conversions
    assert m.r.conversion == {m.r: 1.0}
    assert m.r_in.conversion == {m.r_in: 1.0}


