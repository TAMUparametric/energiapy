import pytest

from energia import Unit, Linkage, Location, Model


@pytest.fixture
def m():
    m_ = Model()
    m_.mile = Unit(label='Mile')
    m_.km = m_.mile * 1.60934
    m_.htown = Location()
    m_.sd = Location()
    m_.mum = Location()
    m_.ny = Location()
    m_.grid = Linkage(source=m_.htown, sink=m_.sd, dist=1400)
    m_.sea = Linkage(source=m_.ny, sink=m_.mum, dist=10000, bi=True)
    return m_


def test_link(m):
    assert m.space.linkages == [m.grid, m.sea, -m.sea]
    assert m.space.sources == [m.htown, m.ny, m.mum]
    assert m.space.sinks == [m.sd, m.mum, m.ny]

    assert m.grid.space == m.space
    assert not m.sea.bi
    assert not (-m.sea).bi
    assert m.sea.sib == -m.sea
    assert (-m.sea).sib == m.sea
    assert m.sea.source == m.ny
    assert m.sea.sink == m.mum
    assert (-m.sea).source == m.mum
    assert (-m.sea).sink == m.ny
    assert m.htown.source()
    assert not m.sd.source()
    assert m.mum.source()
    assert m.ny.source()
    assert not m.htown.sink()
    assert m.sd.sink()
    assert m.mum.sink()
    assert m.ny.sink()
    assert m.ny.links(m.mum) == m.mum.links(m.ny) == [m.sea, -m.sea]
    assert m.htown.links(m.sd) == m.sd.links(m.htown) == [m.grid]
    assert m.htown.connected(m.sd)
    assert not m.htown.connected(m.mum)

    with pytest.raises(ValueError):
        Linkage(source=m.htown, sink=m.htown)

    assert m.grid.network == m.network

    assert not m.htown.isnetwork
    assert m.network.isnetwork
    assert not m.grid.isnetwork


@pytest.mark.parametrize("nested", [False, True])
def test_parent_lookup_registers_link_once(nested):
    """Reading a link's parent must not duplicate spatial aggregation terms."""
    model = Model()
    model.source = Location()
    model.sink = Location()
    if nested:
        model.region = model.source + model.sink
        model.other = Location()
    model.route = Linkage(source=model.source, sink=model.sink)
    expected_parent = model.region if nested else model.network

    for _ in range(5):
        assert model.route.isin is expected_parent

    assert sum(member is model.route for member in expected_parent.has) == 1
