import pytest

from energia import Model, Location, Currency
from operator import is_


@pytest.fixture
def m():
    m_ = Model()
    m_.ny = Location()
    m_.cs = Location()
    m_.ht = Location()
    m_.tx = m_.cs + m_.ht
    m_.usa = m_.ny + m_.tx
    m_.eu = Location()
    m_.ind = Location()
    m_.maitri = Location()
    m_.usd = Currency(locs=[m_.usa])
    m_.eur = Currency(locs=[m_.eu])
    m_.inr = Currency(locs=[m_.ind, m_.maitri])
    m_.eur == m_.usd * 0.8
    m_.inr == m_.usd / 80
    return m_


def test_cash(m):
    assert m.currencies == [m.usd, m.eur, m.inr]
    assert m.usd.exchange == {m.eur: 1.25, m.inr: 80.0}
    assert m.eur.exchange == {m.usd: 0.8, m.inr: 64.0}
    assert m.inr.exchange == {m.usd: 0.0125, m.eur: 0.01}
    assert is_(m.usa.currency, m.usd)
    assert is_(m.ny.currency, m.usd)
    assert is_(m.tx.currency, m.usd)
    assert is_(m.cs.currency, m.usd)
    assert is_(m.ht.currency, m.usd)
    assert is_(m.eu.currency, m.eur)
    assert is_(m.ind.currency, m.inr)
    assert is_(m.maitri.currency, m.inr)
    assert set(m.inr.locs) == {m.ind, m.maitri}
    assert m.usd.howmany(m.eur) == 1.25
    assert m.usd.howmany(m.inr) == 80
    assert m.eur.howmany(m.usd) == 0.8
    assert m.eur.howmany(m.inr) == 64
    assert m.inr.howmany(m.usd) == 0.0125
    assert m.inr.howmany(m.eur) == 0.01
