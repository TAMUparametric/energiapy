import pytest

from energia import Model, Unit


@pytest.fixture
def m():
    m_ = Model()
    m_.mw = Unit(label='Megawatt')
    m_.kw = m_.mw / 1000
    m_.g = Unit(label='Gram')
    m_.kg = 1000 * m_.g
    m_.ton = m_.kg * 1000
    m_.mton = m_.ton * 1000
    m_.mile = Unit(label='Mile')
    m_.km = m_.mile * 1.60934
    m_.acre = Unit(label='Acre')
    return m_


def test_basis(m):
    assert m.kw.basis == m.mw
    assert m.kw.times == 1 / 1000
    assert m.mw.basis == m.kw
    assert m.mw.times == 1000
    assert m.g.basis == m.kg
    assert m.g.times == 0.001
    assert m.kg.basis == m.g
    assert m.kg.times == 1000
    assert m.ton.basis == m.g
    assert m.ton.times == 1000000
    assert m.mton.basis == m.g
    assert m.mton.times == 1000000000
    assert m.ton.howmany(m.g) == 1000000
    assert m.g.howmany(m.ton) == 1000000
    assert m.kg.howmany(m.g) == 1000
    assert m.kg.howmany(m.ton) == 0.001
    assert m.ton.howmany(m.kg) == 1000.0
    assert m.ton.howmany(m.g) == 1000000
    assert m.g.howmany(m.kg) == 0.001
    assert m.g.howmany(m.ton) == 1000000
    assert m.g.howmany(m.mton) == 1000000000
    assert m.kg.howmany(m.ton) == 0.001
    assert m.km.howmany(m.mile) == 1.60934
    assert m.mile.howmany(m.km) == 1 / 1.60934

    with pytest.raises(ValueError):
        m.g.howmany(m.acre)

    assert m.mw / m.kw == 1000

    b = m.mw / 5
    assert b.__dict__ == {
        'basis': m.kw,
        'times': 0.0002,
        'label': 'Megawatt/5000',
        'name': '',
    }

    with pytest.raises(TypeError):
        m.mw * "1111"
