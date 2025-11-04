import pytest

from energia.library.examples.energy import supermarket


@pytest.fixture
def m():
    _m = supermarket()
    _m.usd.spend.opt()
    _m.co2_vent.release.opt()
    _m._.lb(sum(_m._.consume))
    return _m


def test_supermarket(m):
    # obj 0
    assert m.solution[0]._['consume']['values'] == pytest.approx(
        [
            0.0,
            0.0,
            32.142600002116524,
            0.0,
            0.0,
        ]
    )
    assert m.solution[0]._['spend']['values'] == pytest.approx(
        [
            0.0,
            0.0,
            285.74771401881594,
            0.0,
            0.0,
            20000.0,
            482.13900003174786,
            0.0,
            0.0,
            0.0,
            0.0,
            1333.333333333314,
            28333.33333333292,
            1797.6190476226798,
            107857.14285736078,
            125.00000000023097,
            7500.000000013858,
            167714.31528571434,
        ]
    )
    assert m.solution[0]._['release']['values'] == pytest.approx(
        [
            1799.9856001185253,
            2516.6666666717515,
            999.9999999999854,
            100.00000000018477,
        ]
    )
    assert m.solution[0]._['capacity']['values'] == pytest.approx(
        [
            0.0,
            800.0,
            0.0,
            0.0,
            100000.0,
            333.3333333333285,
            3595.2380952453595,
            2500.0000000046193,
        ]
    )
    assert m.solution[0]._['x_capacity']['values'] == pytest.approx(
        [0.0, 1.0, 0.0, 0.0]
    )
    assert m.solution[0]._['operate']['values'] == pytest.approx(
        [
            0.0,
            32.142600002116524,
            0.0,
            0.0,
            333.3333333333285,
            3595.2380952453595,
            2500.0000000046193,
            0.0,
        ]
    )
    assert m.solution[0]._['expend']['values'] == pytest.approx(
        [
            0.0,
            32.142600002116524,
            0.0,
            0.0,
            0.0,
            333.3333333333285,
            3595.2380952453595,
            2500.0000000046193,
        ]
    )
    assert m.solution[0]._['produce']['values'] == pytest.approx(
        [
            0.0,
            0.0,
            3928.571428578688,
            2500.0000000046193,
            1799.9856001185253,
            0.0,
            0.0,
            0.0,
            0.0,
            999.9999999999854,
            2516.6666666717515,
            100.00000000018477,
        ]
    )
    # obj 1
    assert m.solution[1]._['consume']['values'] == pytest.approx(
        [
            0.0,
            0.0,
            32.14260000205713,
            0.0,
            0.0,
        ]
    )
    assert m.solution[1]._['spend']['values'] == pytest.approx(
        [
            0.0,
            0.0,
            285.7477140182879,
            0.0,
            0.0,
            25000000.0,
            482.13900003085695,
            0.0,
            0.0,
            0.0,
            0.0,
            400000.0,
            28333.333333333332,
            1797.6190476190477,
            107857.14285714286,
            125.0,
            7500.0,
            25546380.981952146,
        ]
    )
    assert m.solution[1]._['release']['values'] == pytest.approx(
        [
            1799.9856001151993,
            2516.6666666666665,
            1000.0,
            100.0,
        ]
    )
    assert m.solution[1]._['capacity']['values'] == pytest.approx(
        [
            0.0,
            1000000.0,
            0.0,
            0.0,
            100000.0,
            100000.0,
            3595.2380952380954,
            2500.0,
        ]
    )
    assert m.solution[1]._['x_capacity']['values'] == pytest.approx(
        [0.0, 1.0, 0.0, 0.0]
    )
    assert m.solution[1]._['operate']['values'] == pytest.approx(
        [
            0.0,
            32.14260000205713,
            0.0,
            0.0,
            333.3333333333333,
            3595.2380952380954,
            2500.0,
            0.0,
        ]
    )
    assert m.solution[1]._['expend']['values'] == pytest.approx(
        [
            0.0,
            32.14260000205713,
            0.0,
            0.0,
            0.0,
            333.3333333333333,
            3595.2380952380954,
            2500.0,
        ]
    )
    assert m.solution[1]._['produce']['values'] == pytest.approx(
        [
            0.0,
            0.0,
            3928.5714285714284,
            2500.0,
            1799.9856001151993,
            0.0,
            0.0,
            0.0,
            0.0,
            1000.0,
            2516.6666666666665,
            100.0,
        ]
    )
    # obj 2
    assert m.solution[2]._['consume']['values'] == pytest.approx(
        [
            0.0,
            0.0,
            32.14260000205713,
            0.0,
            0.0,
        ]
    )
    assert m.solution[2]._['spend']['values'] == pytest.approx(
        [
            0.0,
            0.0,
            285.7477140182879,
            0.0,
            0.0,
            25000000.0,
            482.13900003085695,
            0.0,
            0.0,
            0.0,
            0.0,
            400000.0,
            28333.333333333332,
            1797.6190476190477,
            107857.14285714286,
            125.0,
            7500.0,
            25546380.981952146,
        ]
    )
    assert m.solution[2]._['release']['values'] == pytest.approx(
        [
            1799.9856001151993,
            2516.6666666666665,
            1000.0,
            100.0,
        ]
    )
    assert m.solution[2]._['capacity']['values'] == pytest.approx(
        [
            0.0,
            1000000.0,
            0.0,
            0.0,
            100000.0,
            100000.0,
            3595.2380952380954,
            2500.0,
        ]
    )
    assert m.solution[2]._['x_capacity']['values'] == pytest.approx(
        [0.0, 1.0, 0.0, 0.0]
    )
    assert m.solution[2]._['operate']['values'] == pytest.approx(
        [
            0.0,
            32.14260000205713,
            0.0,
            0.0,
            333.3333333333333,
            3595.2380952380954,
            2500.0,
            0.0,
        ]
    )
    assert m.solution[2]._['expend']['values'] == pytest.approx(
        [
            0.0,
            32.14260000205713,
            0.0,
            0.0,
            0.0,
            333.3333333333333,
            3595.2380952380954,
            2500.0,
        ]
    )
    assert m.solution[2]._['produce']['values'] == pytest.approx(
        [
            0.0,
            0.0,
            3928.5714285714284,
            2500.0,
            1799.9856001151993,
            0.0,
            0.0,
            0.0,
            0.0,
            1000.0,
            2516.6666666666665,
            100.0,
        ]
    )
