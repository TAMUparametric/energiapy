import pytest
from energia import Cash, Model, Period, Process, Resource, Storage


@pytest.fixture
def m():
    _m = Model()
    _m.q = Period()
    _m.y = 4 * _m.q
    _m.usd = Cash()
    _m.declare(Resource, ['power', 'wind', 'solar'])
    _m.solar.consume(_m.q) <= 100
    _m.wind.consume <= 400
    _m.power.release.preprocess(180) >= [0.6, 0.7, 0.8, 0.3]

    _m.wf = Process()
    _m.wf(_m.power) == -1 * _m.wind
    _m.wf.capacity.x <= 100
    _m.wf.capacity.x >= 10
    _m.wf.operate.preprocess(norm=True) <= [0.9, 0.8, 0.5, 0.7]
    _m.wf.capacity[_m.usd.spend] == 990637 + 3354
    _m.wf.operate[_m.usd.spend] == 49

    _m.pv = Process()
    _m.pv(_m.power) == -1 * _m.solar
    _m.pv.capacity.x <= 100
    _m.pv.capacity.x >= 10
    _m.pv.operate.preprocess(norm=True) <= [0.6, 0.8, 0.9, 0.7]
    _m.pv.capacity[_m.usd.spend] == 567000 + 872046
    _m.pv.operate[_m.usd.spend] == 90000

    _m.lii = Storage()
    _m.lii(_m.power) == 0.9
    _m.lii.invcapacity.x <= 100
    _m.lii.invcapacity.x >= 10
    _m.lii.inventory(_m.q) <= 1
    _m.lii.invcapacity[_m.usd.spend] == 1302182 + 41432
    _m.lii.inventory[_m.usd.spend] == 2000
    _m.lii.charge.capacity <= 100
    _m.lii.charge.operate <= 1
    _m.lii.discharge.capacity <= 100
    _m.lii.discharge.operate <= 1

    _m.network.operations(_m.wf, _m.pv, _m.lii)

    _m.usd.spend.opt()

    return _m


def test_small_1L_mT_mO_MILP(m):
    assert m.storages == [m.lii]
    assert m.release.sol(True) == pytest.approx([135.0, 157.5, 180.0, 67.5], rel=1e-9)
    assert m.consume.sol(True) == pytest.approx(
        [41.88271604938263, 88.88888888888889, 100.0, 0.0, 311.94444444444446], rel=1e-9
    )
    assert m.capacity.sol(True) == pytest.approx(
        [100.0, 100.0, 27.160493827160487, 100.0, 100.0], rel=1e-9
    )
    assert m.capacity.reporting.sol(True) == pytest.approx([1.0, 1.0, 1.0], rel=1e-9)
    assert m.operate.sol(True) == pytest.approx(
        [
            100.0,
            88.88888888888889,
            55.55555555555556,
            67.5,
            311.94444444444446,
            41.88271604938263,
            88.88888888888889,
            100.0,
            0.0,
            230.77160493827154,
            6.882716049382658,
            27.160493827160487,
            0.0,
            0.0,
            34.043209876543145,
            27.160493827160487,
            24.444444444444443,
            6.882716049382658,
            20.27777777777778,
            0.0,
            0.0,
            0.0,
            0.0,
            24.444444444444443,
            0.0,
        ],
        rel=1e-9,
    )
    assert m.spend.sol(True) == pytest.approx(
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
    assert m.produce(m.power.lii, m.lii.charge, m.q).sol(True) == pytest.approx(
        [6.882716049382658, 20.27777777777778, 0.0, 0.0], rel=1e-9
    )
    assert m.produce(m.power, m.lii.discharge, m.q).sol(True) == pytest.approx(
        [0.0, 0.0, 24.444444444444443, 0.0], rel=1e-9
    )
    assert m.produce(m.power, m.wf, m.q).sol(True) == pytest.approx(
        [100.0, 88.88888888888889, 55.55555555555556, 67.5], rel=1e-9
    )
    assert m.produce(m.power, m.pv, m.q).sol(True) == pytest.approx(
        [41.88271604938263, 88.88888888888889, 100.0, 0.0], rel=1e-9
    )
    assert m.expend(m.power, m.lii.charge, m.q).sol(True) == pytest.approx(
        [6.882716049382658, 20.27777777777778, 0.0, 0.0], rel=1e-9
    )
    assert m.expend(m.power.lii, m.lii.discharge, m.q).sol(True) == pytest.approx(
        [0.0, 0.0, 27.160493827160487, 0.0], rel=1e-9
    )
    assert m.expend(m.wind, m.wf, m.y).sol(True) == pytest.approx(
        [311.94444444444446], rel=1e-9
    )
    assert m.expend(m.solar, m.pv, m.q).sol(True) == pytest.approx(
        [41.88271604938263, 88.88888888888889, 100.0, 0.0], rel=1e-9
    )
    assert m.inventory.sol(True) == pytest.approx(
        [6.882716049382658, 27.160493827160487, 0.0, 0.0], rel=1e-9
    )
