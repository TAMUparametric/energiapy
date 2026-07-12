import pytest

from energia.library.examples.supply_chain import seattle_topeka


@pytest.fixture
def m():
    _m = seattle_topeka()
    _m.usd.spend.opt()
    return _m


def _wrap_with_approx(expected, rel=1e-6, _abs=1e-9):
    """
    Recursively wrap lists/floats in pytest.approx.
    """
    if isinstance(expected, dict):
        return {k: _wrap_with_approx(v, rel, _abs) for k, v in expected.items()}
    elif isinstance(expected, (list, tuple)):
        return pytest.approx(expected, rel=rel, abs=_abs)
    elif isinstance(expected, (int, float)):
        return pytest.approx(expected, rel=rel, abs=_abs)
    else:
        return expected


def test_seattle_topeka(m):

    expected = {
        'consume': [350.0, 550.0],
        'release': [325.0, 300.0, 275.0],
        'operate': [
            900.0,
            900.0,
            350.0,
            550.0,
            325.0,
            300.0,
            275.0,
            50.0,
            300.0,
            0.0,
            275.0,
            0.0,
            275.0,
        ],
        'capacity': [
            350.0,
            550.0,
            325.0,
            300.0,
            275.0,
            50.0,
            300.0,
            0.0,
            275.0,
            0.0,
            275.0,
        ],
        'produce': [350.0, 550.0, 325.0, 300.0, 275.0],
        'expend': [350.0, 550.0, 325.0, 300.0, 275.0],
        'spend': [11250.0, 45900.0, 0.0, 61875.0, 0.0, 34649.99999999999, 153675.0],
        'ship_in': [50.0, 300.0, 0.0, 275.0, 0.0, 275.0],
        'ship_out': [50.0, 300.0, 0.0, 275.0, 0.0, 275.0],
    }

    assert m.solutions[0].asdict() == _wrap_with_approx(expected)

    assert m.purchase.spaces == [m.seattle, m.sandiego]

    assert [m.seattle - m.newyork] == m.seattle.links(m.newyork, show=False)

    assert m.sandiego.connected(m.newyork)
