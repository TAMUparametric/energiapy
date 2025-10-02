import pytest

from energia import Model, Location


@pytest.fixture
def m():
    m_ = Model()
    m_.htown = Location()
    m_.cstat = Location()
    m_.tx = m_.htown + m_.cstat
    m_.sd = Location()
    m_.la = Location()
    m_.cali = m_.sd + m_.la
    m_.usa = m_.tx + m_.cali
    m_.ath = Location()
    m_.amd = Location()
    m_.eu = m_.ath + m_.amd
    m_.pune = Location()
    m_.goa = Location()
    m_.ind = m_.pune + m_.goa
    m_.earth = m_.usa + m_.eu + m_.ind
    return m_


def test_loc(m):
    assert m.space.locations == [
        m.htown,
        m.cstat,
        m.tx,
        m.sd,
        m.la,
        m.cali,
        m.usa,
        m.ath,
        m.amd,
        m.eu,
        m.pune,
        m.goa,
        m.ind,
        m.earth,
    ]
    assert m.htown.space == m.space
    assert not set(m.htown.has)
    assert not set(m.cstat.has)
    assert set(m.tx.has) == {m.htown, m.cstat}
    assert not set(m.sd.has)
    assert not set(m.la.has)
    assert set(m.cali.has) == {m.la, m.sd}
    assert set(m.usa.has) == {m.tx, m.cali}
    assert not set(m.ath.has)
    assert not set(m.amd.has)
    assert set(m.eu.has) == {m.ath, m.amd}
    assert not set(m.pune.has)
    assert not set(m.goa.has)
    assert set(m.ind.has) == {m.pune, m.goa}
    assert set(m.earth.has) == {m.usa, m.eu, m.ind}

    assert m.htown.isin == m.tx
    assert m.cstat.isin == m.tx
    assert m.tx.isin == m.usa
    assert m.sd.isin == m.cali
    assert m.la.isin == m.cali
    assert m.cali.isin == m.usa
    assert m.usa.isin == m.earth
    assert m.ath.isin == m.eu
    assert m.amd.isin == m.eu
    assert m.eu.isin == m.earth
    assert m.pune.isin == m.ind
    assert m.goa.isin == m.ind
    assert m.ind.isin == m.earth
    assert not m.earth.isin

    assert list(m.usa.all()) == [m.cali, m.la, m.sd, m.tx, m.cstat, m.htown]
