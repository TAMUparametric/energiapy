import pytest

from energia.library.examples.energy import design_scheduling


@pytest.fixture
def m():
    _m = design_scheduling()
    _m.usd.spend.opt()
    return _m


def test_small_1L_mT_mO_MILP(m):
    assert m.storages == [m.lii]
    assert m.release.sol(aslist=True) == pytest.approx(
        [135.0, 157.5, 180.0, 67.5], rel=1e-9
    )
    assert m.consume.sol(aslist=True) == pytest.approx(
        [41.88271604938263, 88.88888888888889, 100.0, 0.0, 311.94444444444446], rel=1e-9
    )
    assert m.capacity.sol(aslist=True) == pytest.approx(
        [100.0, 100.0, 27.160493827160423, 24.444444444444443], rel=1e-9
    )
    assert m.invcapacity.sol(aslist=True) == pytest.approx(
        [27.160493827160423], rel=1e-9
    )
    assert m.capacity.reporting.sol(aslist=True) == pytest.approx([1.0, 1.0], rel=1e-9)
    assert m.invcapacity.reporting.sol(aslist=True) == pytest.approx([1.0], rel=1e-9)
    assert m.operate.sol(aslist=True) == pytest.approx(
        [
            100.0,
            88.88888888888889,
            55.55555555555556,
            67.5,
            311.94444444444446,
            41.882716049382566,
            88.88888888888889,
            100.0,
            0.0,
            230.77160493827148,
            27.160493827160423,
            6.882716049382594,
            20.27777777777778,
            0.0,
            0.0,
            24.444444444444443,
            0.0,
            0.0,
            24.444444444444443,
            0.0,
        ],
        rel=1e-9,
    )
    assert m.spend.sol(aslist=True) == pytest.approx(
        [
            99399100.0,
            15285.277777777777,
            143904600.0,
            20769444.444444437,
            36493219.75308641,
            68086.41975308629,
            300649735.89506173,
        ],
        rel=1e-9,
    )
    assert m.produce(m.power.lii, m.lii.charge.operate, m.q).sol(
        aslist=True
    ) == pytest.approx([6.882716049382594, 20.27777777777778, 0.0, 0.0], rel=1e-9)
    assert m.produce(m.power, m.lii.discharge.operate, m.q).sol(
        aslist=True
    ) == pytest.approx([0.0, 0.0, 24.444444444444443, 0.0], rel=1e-9)
    assert m.produce(m.power, m.wf.operate, m.q).sol(aslist=True) == pytest.approx(
        [100.0, 88.88888888888889, 55.55555555555556, 67.5], rel=1e-9
    )
    assert m.produce(m.power, m.pv.operate, m.q).sol(aslist=True) == pytest.approx(
        [41.882716049382566, 88.88888888888889, 100.0, 0.0], rel=1e-9
    )
    assert m.expend(m.power, m.lii.charge.operate, m.q).sol(
        aslist=True
    ) == pytest.approx([6.882716049382594, 20.27777777777778, 0.0, 0.0], rel=1e-9)
    assert m.expend(m.power.lii, m.lii.discharge.operate, m.q).sol(
        True
    ) == pytest.approx([0.0, 0.0, 27.160493827160423, 0.0], rel=1e-9)
    assert m.expend(m.wind, m.wf.operate, m.y).sol(aslist=True) == pytest.approx(
        [311.94444444444446], rel=1e-9
    )
    assert m.expend(m.solar, m.pv.operate, m.q).sol(aslist=True) == pytest.approx(
        [41.882716049382566, 88.88888888888889, 100.0, 0.0], rel=1e-9
    )
    assert m.inventory.sol(aslist=True) == pytest.approx(
        [34.04320987654302, 6.882716049382594, 27.160493827160423, 0.0, 0.0], rel=1e-9
    )
