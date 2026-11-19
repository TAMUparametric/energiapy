from energia import Currency, Location, Model, Periods, Process, Resource


def test_operate_samples_key_by_period_and_location():
    m = Model()
    m.q = Periods()
    m.y = 4 * m.q
    m.wf = Process()
    m.north, m.south = Location(), Location()

    quarterly = m.wf.operate(m.north, m.q)
    yearly = m.wf.operate(m.north, m.y)
    southern = m.wf.operate(m.south, m.q)
    values = {quarterly: 10, yearly: 40, southern: 20}

    repeated = m.wf.operate(m.q, m.north)
    assert repeated == quarterly
    assert hash(repeated) == hash(quarterly)
    assert values[repeated] == 10
    assert values[m.wf.operate(m.north, m.y)] == 40
    assert values[m.wf.operate(m.south, m.q)] == 20
    assert len({quarterly, repeated, yearly, southern}) == 3


def test_consume_samples_distinguish_resources_aspects_and_models():
    m = Model()
    m.wind, m.power = Resource(), Resource()
    other = Model()
    other.wind = Resource()

    assert m.wind.consume != m.power.consume
    assert m.wind.consume != m.wind.release
    assert m.wind.consume != other.wind.consume
    assert {m.wind.consume, m.power.consume} == {m.consume(m.wind), m.consume(m.power)}
    assert not m.program.constraint_sets


def test_spend_samples_include_the_domain_of_the_consumption():
    m = Model()
    m.q = Periods()
    m.y = 4 * m.q
    m.power = Resource()
    m.cash = Currency()

    quarterly = m.cash.spend(m.power.consume(m.q))
    yearly = m.cash.spend(m.power.consume(m.y))

    prices = {quarterly: 2, yearly: 8}
    assert prices[m.cash.spend(m.consume(m.power, m.q))] == 2
    assert prices[m.cash.spend(m.consume(m.power, m.y))] == 8


def test_binding_uses_each_aspect_and_primary_index_once():
    m = Model()
    m.q = Periods()
    m.wf, m.pv = Process(), Process()
    m.power = Resource()

    wind = m.wf.operate
    quarterly_wind = wind(m.q)
    solar = m.pv.operate
    selection = m.power.produce(wind, quarterly_wind, solar, wind)

    assert selection.domain.samples == [wind, quarterly_wind, solar]
    assert selection.domain.index_binds == [m.operate, m.wf, m.operate, m.pv]


def test_repeated_period_slices_and_lags():
    m = Model()
    m.q = Periods()
    m.y = 4 * m.q
    m.wf = Process()
    operate = m.wf.operate
    values = {operate(m.q[0:4:2]): 2, operate(m.q[0:4]): 4, operate(-m.q): -1}

    assert values[operate(m.q[0:4:2])] == 2
    assert values[operate(m.q[0:4])] == 4
    assert values[operate(-m.q)] == -1
    assert operate(m.q) not in values


def test_numeric_equality_binds_without_changing_the_sample_key():
    m = Model()
    m.power = Resource(take=True)
    selected = m.power.release
    values = {selected: 7}

    selected == 7

    assert selected.domain.periods is m.horizon
    assert selected.domain.location is m.network
    assert values[m.power.release] == values[selected] == 7
    m.power.consume.opt()
    assert m.consume.output(aslist=True) == [7]
