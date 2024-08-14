"""The Task action associated with the attributes that feature in Components of the System model
"""

from ..variables.action import Gives, Takes
from ..variables.capacitate import Capacity
from ..variables.emit import (EmitBuy, EmitCap, EmitLoss, EmitSell, EmitSys,
                              EmitUse)
from ..variables.expense import (Credit, ExpBuy, ExpBuyBnd, ExpCap, ExpOp,
                                 ExpSell, ExpSellBnd, ExpUse, Penalty)
from ..variables.loss import Loss
from ..variables.operate import Operate
from ..variables.trade import Buy, Sell, Ship
from ..variables.use import Use

cmd_use = {'use': Use, 'cost': ExpUse, 'emission': EmitUse}

opn = {
    'capex': ExpCap,
    'opex': ExpOp,
    'capacity': Capacity,
    'operate': Operate,
    'land': Use,
    'material': Use,
    'emission': EmitCap,
}

res_loss = {'loss': Loss}


task = {
    'players': {'has': Gives, 'needs': Takes},
    'emissions': {'emit': EmitSys},
    'cash': {'spend': ExpBuyBnd, 'earn': ExpSellBnd},
    'land': cmd_use,
    'materials': cmd_use,
    'resources': {
        'buy': Buy,
        'sell': Sell,
        'ship': Ship,
        'buy_price': ExpBuy,
        'sell_price': ExpSell,
        'credit': Credit,
        'penalty': Penalty,
        'buy_emission': EmitBuy,
        'sell_emission': EmitSell,
        'loss_emission': EmitLoss,
    },
    'processes': opn,
    'storages': {**opn, **res_loss},
    'transits': {**opn, **res_loss},
}
