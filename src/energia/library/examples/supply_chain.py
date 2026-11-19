from itertools import product

from energia import Currency, Location, Model, Process, Resource, Transport


def seattle_topeka():
    """The Famous Seattle to Topeka Supply Chain Example"""
    m = Model()
    m.declare(Location, ["seattle", "sandiego", "newyork", "chicago", "topeka"])
    m.usd = Currency()

    m.r_consume = Resource()
    for origin, capacity in ((m.seattle, 350), (m.sandiego, 600)):
        _ = m.r_consume.consume(origin) <= capacity

    m.r_release = Resource()
    for market, demand in ((m.newyork, 325), (m.chicago, 300), (m.topeka, 275)):
        _ = m.r_release.release(market) >= demand

    m.r = Resource()

    m.purchase = Process()
    _ = m.purchase(m.r) == -m.r_consume
    m.purchase.operate.V()

    m.dispatch = Process()
    _ = m.dispatch(-m.r) == m.r_release
    m.dispatch.operate.V()

    m.purchase.locate(m.seattle, m.sandiego)
    m.dispatch.locate(m.newyork, m.chicago, m.topeka)

    dist_dict = {
        m.seattle: {m.newyork: 2.5, m.chicago: 1.7, m.topeka: 1.8},
        m.sandiego: {m.newyork: 2.5, m.chicago: 1.8, m.topeka: 1.4},
    }

    for i, j in product([m.seattle, m.sandiego], [m.newyork, m.chicago, m.topeka]):
        m.Link(i, j, dist=dist_dict[i][j])

    m.channel = Transport()
    _ = m.channel(m.r) == 1.0  # 100% efficient

    freight_rate = 90
    for i, destinations in dist_dict.items():
        for j in destinations:
            _ = m.usd.spend(m.channel.operate, i - j) == freight_rate
            m.channel.locate(i - j)

    return m
