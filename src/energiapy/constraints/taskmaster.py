"""The Task action associated with Components attrs
Each attribute is trated as a Task basically
Which is defined using a Variable 
The Variable has a Constraint generation rule (see rulebook.py)
The Constraint may need a Parent Variable or a Parameter

"""

from ..components.analytical.player import Player
from ..components.commodity.cash import Cash
from ..components.commodity.emission import Emission
from ..components.commodity.land import Land
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit
from ..variables.action import Give, Take
from ..variables.capacitate import Capacity
from ..variables.emit import EmitBuy, EmitSetUp, EmitLoss, EmitSell, Emit, EmitUse
from ..variables.expense import (
    Credit,
    Earn,
    ExpBuy,
    ExpSetUp,
    ExpSetUpI,
    ExpOpr,
    ExpOprI,
    ExpSell,
    ExpUsage,
    Penalty,
    Spend,
)
from ..variables.loss import Loss
from ..variables.operate import Operate
from ..variables.trade import Buy, Sell, Ship
from ..variables.use import Use, Usage

cmd_use = {'use': Use, 'cost': ExpUsage, 'emission': EmitUse}

opn = {
    'capex_i': ExpSetUpI,
    'opex_i': ExpOprI,
    'capex': ExpSetUp,
    'opex': ExpOpr,
    'capacity': Capacity,
    'operate': Operate,
    'land': Usage,
    'material': Usage,
    'emission': EmitSetUp,
    'buy': Buy,
    'sell': Sell,
    'price_buy': ExpBuy,
    'price_sell': ExpSell,
    'credit': Credit,
    'penalty': Penalty,
    'loss': Loss,
    'ship': Ship,
}


taskmaster = {
    Player: {'has': Give, 'needs': Take},
    Emission: {'emit': Emit},
    Cash: {'spend': Spend, 'earn': Earn},
    Land: cmd_use,
    Material: cmd_use,
    Resource: {
        'buy': Buy,
        'sell': Sell,
        'ship': Ship,
        'price_buy': ExpBuy,
        'price_sell': ExpSell,
        'credit': Credit,
        'penalty': Penalty,
        'emission_buy': EmitBuy,
        'emission_sell': EmitSell,
        'emission_loss': EmitLoss,
    },
    Process: opn,
    Storage: opn,
    Transit: opn,
}
