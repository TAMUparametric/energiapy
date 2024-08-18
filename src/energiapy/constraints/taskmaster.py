"""The Task action associated with the attributes that feature in Components of the System model
"""

from ..components.analytical.player import Player
from ..components.commodity.cash import Cash
from ..components.commodity.land import Land
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.impact.emission import Emission
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit
from ..variables.action import Gives, Takes
from ..variables.capacitate import Capacity
from ..variables.emit import (EmitBuy, EmitCap, EmitLoss, EmitSell, EmitSys,
                              EmitUse)
from ..variables.expense import (Credit, Earn, ExpBuy, ExpCap, ExpCapI, ExpOp,
                                 ExpOpI, ExpSell, ExpUse, Penalty, Spend)
from ..variables.loss import Loss
from ..variables.operate import Operate
from ..variables.trade import Buy, Recieve, Sell, Ship
from ..variables.use import Use, UseLnd, UseMat

cmd_use = {'use': Use, 'cost': ExpUse, 'emission': EmitUse}

opn = {
    'capex_i': ExpCapI,
    'opex_i': ExpOpI,
    'capex': ExpCap,
    'opex': ExpOp,
    'capacity': Capacity,
    'operate': Operate,
    'land': UseLnd,
    'material': UseMat,
    'emission': EmitCap,
    'buy': Buy,
    'sell': Sell,
    'buy_price': ExpBuy,
    'sell_price': ExpSell,
    'credit': Credit,
    'penalty': Penalty,
}

res_loss = {'loss': Loss}


taskmaster = {
    Player: {'has': Gives, 'needs': Takes},
    Emission: {'emit': EmitSys},
    Cash: {'spend': Spend, 'earn': Earn},
    Land: cmd_use,
    Material: cmd_use,
    Resource: {
        'buy': Buy,
        'sell': Sell,
        'ship': Ship,
        'receive': Recieve,
        'buy_price': ExpBuy,
        'sell_price': ExpSell,
        'credit': Credit,
        'penalty': Penalty,
        'buy_emission': EmitBuy,
        'sell_emission': EmitSell,
        'loss_emission': EmitLoss,
    },
    Process: opn,
    Storage: {**opn, **res_loss},
    Transit: {**opn, **res_loss},
}
