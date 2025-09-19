import pytest

from energia import Model, Periods, TemporalScales


@pytest.fixture
def horizon_first():
    m = Model()
    m.t0 = Periods()
    m.t1 = m.t0 / 4
    return m


@pytest.fixture
def period_first():
    m = Model()
    m.t1 = Periods()
    m.t0 = 4 * m.t1
    return m


def test_time(horizon_first, period_first):
    assert horizon_first.horizon == horizon_first.t0
    assert horizon_first.t0 > horizon_first.t1
    assert horizon_first.t0 / horizon_first.t1 == 4

    assert period_first.horizon == period_first.t0
    assert period_first.t0 > period_first.t1
    assert period_first.t0 / period_first.t1 == 4


@pytest.fixture
def scales_one():
    m = Model()
    m.scales = TemporalScales(discretizations=[1, 365, 24], names=['y', 'd', 'h'])
    return m


@pytest.fixture
def scales_five():
    m = Model()
    m.scales = TemporalScales(discretizations=[5, 365, 24], names=['y', 'd', 'h'])
    return m


def test_scales(scales_one, scales_five):
    assert scales_one.y.howmany(scales_one.d) == 365
    assert scales_one.d.howmany(scales_one.h) == 24
    assert scales_one.y.howmany(scales_one.h) == 8760

    assert scales_five.y.howmany(scales_five.d) == 365
    assert scales_five.d.howmany(scales_five.h) == 24
    assert scales_five.y.howmany(scales_five.h) == 8760
    assert scales_five.t0.howmany(scales_five.h) == 5 * 8760
    assert scales_five.t0.howmany(scales_five.d) == 5 * 365
    assert scales_five.t0.howmany(scales_five.y) == 5
