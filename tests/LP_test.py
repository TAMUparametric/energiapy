import pytest
from energia import Cash, Model, Period, Process, Resource


@pytest.fixture
def m():
    _m = Model()
    _m.q = Period()
    _m.y = 4 * _m.q
    _m.usd = Cash()
    _m.power, _m.wind = Resource(), Resource()
    _m.wind.consume <= 400
    _m.power.release.preprocess(100) >= [0.6, 0.7, 1, 0.3]

    _m.wf = Process()
    _m.wf(_m.power) == -1 * _m.wind
    _m.wf.operate.preprocess(200, norm=False) <= [0.9, 0.8, 0.5, 0.7]

    _m.wf.operate[_m.usd.spend] == [4000, 4200, 4300, 3900]
    _m.network.operations(_m.wf)
    _m.usd.spend.opt()
    return _m


def test_small_1L_1T_1O_LP(m):
    assert m.periods == [m.q, m.y]
    assert m.locs == [m.network]
    assert m.resources == [m.usd, m.power, m.wind]
    assert m.processes == [m.wf]
    assert m.consume.sol(True) == pytest.approx([260.0], rel=1e-9)
    assert m.release.sol(True) == pytest.approx([60.0, 70.0, 100.0, 30.0], rel=1e-9)
    assert m.operate.sol(True) == pytest.approx(
        [60.0, 70.0, 100.0, 30.0, 260.0], rel=1e-9
    )
    assert m.spend.sol(True) == pytest.approx(
        [240000.0, 294000.0, 430000.0, 117000.0, 1081000.0], rel=1e-9
    )
    assert m.produce.sol(True) == pytest.approx([60.0, 70.0, 100.0, 30.0], rel=1e-9)
