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


@pytest.fixture
def m():
    m_ = Model()
    m_.h = Periods()
    m_.d = m_.h * 24
    m_.y = m_.d * 365
    m_.w = m_.d * 7
    m_.s = Periods()
    return m_


def test_period(m):
    assert m.time.periods == [m.h, m.d, m.y, m.w, m.s]
    assert m.h.howmany(m.d) == 0.041666666666666664
    assert m.h.howmany(m.w) == 0.005952380952380952
    assert m.h.howmany(m.y) == 0.00011415525114155251
    assert m.d.howmany(m.h) == 24
    assert m.d.howmany(m.w) == 0.14285714285714285
    assert m.d.howmany(m.y) == 0.0027397260273972603
    assert m.w.howmany(m.h) == 168
    assert m.w.howmany(m.d) == 7
    assert m.w.howmany(m.y) == 0.019178082191780823
    assert m.y.howmany(m.h) == 8760
    assert m.y.howmany(m.d) == 365
    assert m.y.howmany(m.w) == 52.142857142857146
    assert m.time.horizon == m.y
    assert m.h.periods == 1
    assert m.d.periods == 24
    assert m.y.periods == 8760
    assert m.w.periods == 168

    with pytest.raises(AttributeError):
        m.fail = m.h * m.y

    with pytest.raises(ValueError):
        m.h.howmany(m.s)

    with pytest.raises(ValueError):
        m.y.howmany(m.s)
