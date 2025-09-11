"""Design and scheduling example"""

from ...represent.model import Model
from ...components.commodity.misc import Cash
from ...components.temporal.period import Period
from ...components.commodity.resource import Resource
from ...components.operation.process import Process
from ...components.operation.storage import Storage


def design_scheduling():
    """A small design and scheduling example"""
    m = Model('design_scheduling')
    m.q = Period()
    m.y = 4 * m.q
    m.usd = Cash()
    m.declare(Resource, ['power', 'wind', 'solar'])
    m.solar.consume(m.q) <= 100
    m.wind.consume <= 400
    m.power.release.prep(180) >= [0.6, 0.7, 0.8, 0.3]

    m.wf = Process()
    m.wf(m.power) == -1 * m.wind
    m.wf.capacity.x <= 100
    m.wf.capacity.x >= 10
    m.wf.operate.prep(norm=True) <= [0.9, 0.8, 0.5, 0.7]
    m.wf.capacity[m.usd.spend] == 990637 + 3354
    m.wf.operate[m.usd.spend] == 49

    m.pv = Process()
    m.pv(m.power) == -1 * m.solar
    m.pv.capacity.x <= 100
    m.pv.capacity.x >= 10
    m.pv.operate.prep(norm=True) <= [0.6, 0.8, 0.9, 0.7]
    m.pv.capacity[m.usd.spend] == 567000 + 872046
    m.pv.operate[m.usd.spend] == 90000

    m.lii = Storage()
    m.lii(m.power) == 0.9
    m.lii.capacity.x <= 100
    m.lii.capacity.x >= 10
    m.lii.capacity[m.usd.spend] == 1302182 + 41432
    m.lii.inventory[m.usd.spend] == 2000

    m.network.locate(m.wf, m.pv, m.lii)

    return m
