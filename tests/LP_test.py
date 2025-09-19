import pytest

# from energia import Currency, Model, Periods, Process, Resource

from energia.examples.energy.scheduling import scheduling


@pytest.fixture
def m():
    _m = scheduling()
    _m.usd.spend.opt()
    return _m


def test_small_1L_1T_1O_LP(m):
    assert m.periods == [m.q, m.y]
    assert m.locs == [m.network]
    assert m.resources == [m.usd, m.power, m.wind]
    assert m.processes == [m.wf]
    assert m.consume.sol(aslist=True) == pytest.approx([260.0], rel=1e-9)
    assert m.release.sol(aslist=True) == pytest.approx(
        [60.0, 70.0, 100.0, 30.0], rel=1e-9
    )
    assert m.operate.sol(aslist=True) == pytest.approx(
        [60.0, 70.0, 100.0, 30.0, 260.0], rel=1e-9
    )
    assert m.spend.sol(aslist=True) == pytest.approx(
        [240000.0, 294000.0, 430000.0, 117000.0, 1081000.0], rel=1e-9
    )
    assert m.produce.sol(aslist=True) == pytest.approx(
        [60.0, 70.0, 100.0, 30.0], rel=1e-9
    )
