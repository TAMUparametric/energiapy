"""Small Energy Scheduling Optimization (ESO) Scheduling Example"""
from ..represent.model import Model
from ..components.commodity.resource import Resource
from ..components.commodity.misc import Cash
from ..components.operation.process import Process
from ..components.temporal.period import Period




def scheduling_small():
    """Small example of energy scheduling with wind farm, power and cash."""

    _m = Model()
    _m.q = Period()
    _m.y = 4 * _m.q
    _m.usd = Cash()
    _m.power, _m.wind = Resource(), Resource()
    _m.wind.consume <= 400
    _m.power.release.preprocess(100) >= [0.6, 0.7, 1, 0.3]

    _m.wf = Process()
    _m.wf(_m.power) == -1 * _m.wind
    _m.wf.operate.preprocess(200, norm=False) <= [0.9, 0.8, 0.5, 0.7]

    _m.wf.operate[_m.usd.spend] == [4000, 4200, 4300, 3900]
    _m.network.operations(_m.wf)
    _m.usd.spend.opt()
    return _m
