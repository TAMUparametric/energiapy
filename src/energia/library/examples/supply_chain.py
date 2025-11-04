from itertools import product

from energia import Currency, Location, Model, Process, Resource, Transport


def seattle_topeka():
    """The Famous Seattle to Topeka Supply Chain Example"""
    m = Model()
    m.declare(Location, ['seattle', 'sandiego', 'newyork', 'chicago', 'topeka'])
    m.usd = Currency()

    m.r_consume = Resource()
    _ = m.r_consume.consume(m.seattle) <= 350
    _ = m.r_consume.consume(m.sandiego) <= 600

    m.r_release = Resource()
    _ = m.r_release.release(m.newyork) >= 325
    _ = m.r_release.release(m.chicago) >= 300
    _ = m.r_release.release(m.topeka) >= 275

    m.r = Resource()

    m.purchase = Process()
    _ = m.purchase(m.r) == -m.r_consume
    _ = m.purchase.operate == True

    m.dispatch = Process()
    _ = m.dispatch(-m.r) == m.r_release
    _ = m.dispatch.operate == True

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

    for i in dist_dict:
        for j in dist_dict[i]:
            _ = m.usd.spend(m.channel.operate, i - j) == 90
            m.channel.locate(i - j)

    return m
