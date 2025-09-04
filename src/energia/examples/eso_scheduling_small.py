"""Small Energy Scheduling Optimization (ESO) Scheduling Example"""

from ..represent.model import Model
from ..components.commodity.resource import Resource
from ..components.commodity.misc import Cash
from ..components.operation.process import Process
from ..components.temporal.period import Period


def scheduling_small(model: Model):
    """Small example of energy scheduling with wind farm, power and cash."""
    model.q = Period()
    model.y = 4 * model.q
    model.usd = Cash()
    model.power, model.wind = Resource(), Resource()
    model.wind.consume <= 400
    model.power.release.preprocess(100) >= [0.6, 0.7, 1, 0.3]

    model.wf = Process()
    model.wf(model.power) == -1 * model.wind
    model.wf.operate.preprocess(200, norm=False) <= [0.9, 0.8, 0.5, 0.7]

    model.wf.operate[model.usd.spend] == [4000, 4200, 4300, 3900]
    model.network.operations(model.wf)
    model.usd.spend.opt()
    return model
