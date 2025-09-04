import pytest

from energia import Model, Period


@pytest.fixture
def horizon_first():
    m = Model()
    m.t0 = Period()
    m.t1 = m.t0 / 4
    return m


@pytest.fixture
def period_first():
    m = Model()
    m.t1 = Period()
    m.t0 = 4 * m.t1
    return m


def test_time(horizon_first, period_first):
    assert horizon_first.horizon == horizon_first.t0
    assert horizon_first.t0 > horizon_first.t1
    assert horizon_first.t0 / horizon_first.t1 == 4

    assert period_first.horizon == period_first.t0
    assert period_first.t0 > period_first.t1
    assert period_first.t0 / period_first.t1 == 4
