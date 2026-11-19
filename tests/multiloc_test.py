import pytest

from energia.library.examples.supply_chain import seattle_topeka


def test_repeated_purchase_mapping_preserves_constraint_matrix():
    m = seattle_topeka()
    seattle = m.purchase.operate(m.seattle, m.horizon)
    san_diego = m.purchase.operate(m.sandiego, m.horizon)
    network = m.purchase.operate(m.network, m.horizon)
    matrix = m.program.A
    for source in (seattle, san_diego):
        m.operate.Map(source.domain)
        assert m.program.A == matrix

    # The network total includes each city's purchases exactly once.
    row = getattr(m.program, f"operate{network.domain.idxname}_map")[0]
    expected = {network.V()[0].n: 1, seattle.V()[0].n: -1, san_diego.V()[0].n: -1}
    assert len(row.P) == len(expected)
    assert dict(zip(row.P, row.A, strict=True)) == expected
    assert m.operate.maps["space"][network.domain] == [seattle.domain, san_diego.domain]


def test_ordinary_and_reporting_maps_track_the_same_domains_independently():
    m = seattle_topeka()
    seattle = m.purchase.operate(m.seattle, m.horizon)
    san_diego = m.purchase.operate(m.sandiego, m.horizon)
    network = m.purchase.operate(m.network, m.horizon)
    sources = [seattle.domain, san_diego.domain]
    assert m.operate.maps["space"][network.domain] == sources
    assert network.domain not in m.operate.maps_report["space"]

    for sample in (seattle, san_diego):
        sample.X()
        m.operate.Map(sample.domain, reporting=True)
    assert m.operate.maps_report["space"][network.domain] == sources
    matrix = m.program.A
    m.operate.Map(seattle.domain, reporting=True)
    assert m.program.A == matrix
    assert m.operate.maps_report["space"][network.domain] == sources
    assert m.operate.maps["space"][network.domain] == sources


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
