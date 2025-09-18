"""DecisionSpace of the Model"""

from dataclasses import dataclass
from typing import Type

from ..components.commodity.misc import Currency, Material
from ..components.commodity.resource import Resource
from ..components.impact.categories import Environ, Social
from ..components.operation.process import Process
from ..components.operation.storage import Storage
from ..components.operation.transport import Transport
from ..modeling.variables.control import Control
from ..modeling.variables.impact import Impact
from ..modeling.variables.state import State
from ..modeling.variables.stream import Stream


@dataclass
class DecisionSpace:
    """DecisionSpace of the Model which include aspects that describe:
        - State: the state of the system (e.g. inventory, emissions)
        - Control: the decision aspects (e.g. production, consumption)
        - Stream: the flow of resources (e.g. production, consumption, exchange)
        - Impact: the consequences of the decisions (e.g. emissions, benefits)

    Note:
        - Decisions, positive and negative together, grant 1 degree of freedom
    """

    def birth_state(
        self,
        types_idc: Type[Environ | Social] = None,
        types_res: Type[Resource] = None,
        types_opr: tuple[Type[Process | Storage | Transport]] = None,
        types_dres: Type[Resource] = None,
        label: str = '',
    ):
        """ "Defines an state"""
        # create the state
        state = State(
            types_idc=types_idc,
            types_res=types_res,
            types_opr=types_opr,
            types_dres=types_dres,
            label=label,
        )
        # create the control to add to the state
        state.add = Control(
            types_idc=types_idc,
            types_res=types_res,
            types_opr=types_opr,
            types_dres=types_dres,
        )
        # create the control to subtract from the state
        state.sub = -state.add

        return state

    def __post_init__(self):

        # ------Capacity Sizing-------#
        ############################################

        # self.capacity = self.birth_state(
        #     types_opr=(Process, Transport),
        #     label='Capacity',
        # )
        # self.capacity.latex = r'{cap}^{P}'
        # self.capacity.add.latex = r'{cap}^{P+}'
        # self.capacity.sub.latex = r'{cap}^{P-}'

        # increases the capacity of an operation
        self.setup = Control(
            types_opr=(Process, Transport),
            label='Capacitate Operation',
            latex=r'{cap}^{P+}',
        )
        # decreases the capacity of an operation
        self.dismantle = -self.setup
        self.dismantle.latex = r'{cap}^{P-}'

        # operating capacity state variable
        self.capacity = State(
            types_opr=(Process, Transport),
            label='Operational Capacity',
            latex=r'{cap}^{P}',
        )
        self.capacity.add = self.setup
        self.capacity.sub = self.dismantle

        ############################################

        # increases the inventory capacity of an operation
        self.invsetup = Control(
            types_res=Resource,
            # types_opr=(Storage,),
            label='Capacitate Inventory',
            latex=r'{cap}^{S+}',
        )
        # decreases the capacity of an operation
        self.invdismantle = -self.invsetup
        self.invdismantle.latex = r'{cap}^{S-}'

        # Inventory Capacity
        # for storage the charging and discharging processes
        # will have capacity, while the storage itself wil have
        # inventory capacity
        self.invcapacity = State(
            types_res=Resource,
            # types_opr=Storage,
            label='Inventory Capacity',
            latex=r'{cap}^{S}',
        )
        self.invcapacity.add = self.invsetup
        self.invcapacity.sub = self.invdismantle

        ############################################

        # -------Operational Scheduling-------#

        # Increases the operating level
        self.rampup = Control(
            types_opr=(Process, Storage, Transport),
            label='Ramp Capacity Utilization',
            latex=r'{opr}^{+}',
        )
        # Decreases the operating level
        self.rampdown = -self.rampup
        self.rampdown.latex = r'{opr}^{-}'

        # Operating Level
        self.operate = State(
            types_opr=(Process, Storage, Transport),
            label='Capacity Utilization',
            latex=r'{opr}',
        )
        self.operate.bound = self.capacity
        self.operate.add = self.rampup
        self.operate.sub = self.rampdown

        ############################################

        # ------Trade-------#

        ## Buy - Positive trade which brings in resource
        # increases the amount of resource being bought
        self.buy_more = Control(
            types_res=Resource,
            label='Buy More Resource',
            latex=r'{buy}^{+}',
        )

        # decreases the amount of resource being sold
        self.buy_less = -self.buy_more
        self.buy_less.latex = r'{buy}^{-}'

        self.buy = Stream(
            types_res=Resource, label='Exchange Resource with other player'
        )
        self.buy.add = self.buy_more
        self.buy.sub = self.buy_less

        ## Sell - Negative trade which takes out resource
        # increases the amount of resource being sold
        self.sell_more = Control(
            types_res=Resource,
            label='Sell More Resource',
            latex=r'{sell}^{+}',
        )
        # decreases the amount of resource being bought
        self.sell_less = -self.sell_more
        self.sell_less.latex = r'{sell}^{-}'

        self.sell = -self.buy
        self.sell.add = self.sell_more
        self.sell.sub = self.sell_less

        ############################################

        # ------Streams-------#

        ## Flow

        ############################################

        # going into inventory
        # Inventory Levels
        self.inventory = Stream(
            types_res=Resource,
            types_opr=Storage,
            label='Store Resource',
            latex=r'{inv}',
        )
        self.inventory.ispos = False
        self.inventory.bound = self.invcapacity

        ############################################

        # Production
        self.produce = Stream(
            types_res=Resource,
            types_opr=(Process, Storage, Transport),
            label='Resource Stream caused by Operation',
            latex=r'{prod}',
        )
        self.expend = -self.produce
        self.expend.latex = r'{expd}'

        ############################################

        ##  Free Movements of goods
        self.consume = Stream(
            types_res=Resource,
            label='Free Resource Stream',
            latex=r'{cons}',
        )

        self.release = -self.consume
        self.release.latex = r'{rlse}'

        ############################################

        # Freight
        self.ship_in = Stream(
            types_res=Resource,
            types_opr=Transport,
            label='Resource Stream between Locations',
        )
        self.ship_in.latex = r'{impt}'
        self.ship_out = -self.ship_in
        self.ship_out.latex = r'{expt}'

        ############################################

        # Utilization
        self.dispose = Stream(
            types_res=Resource,
            types_opr=(Process, Storage, Transport),
            label='Utilize Resource',
            latex=r'{disp}',
        )
        self.use = -self.dispose
        ############################################

        # ------Consequences-------#

        # Environmental
        self.emit = Impact(
            types_res=Environ,
            types_dres=(Resource, Material),
            types_opr=(Process, Storage, Transport),
            label='Emit',
        )
        self.abate = -self.emit
        # change is the balance of emit and abate

        self.change = State(
            types_idc=(Environ),
            label='Environmental Change',
            latex=r'{chng}',
        )
        self.change.add = self.emit
        self.change.sub = self.abate

        ############################################

        # Social
        self.detriment = Impact(
            types_idc=Social,
            types_res=Resource,
            label='Detriment',
            latex=r'{detr}',
        )
        self.benefit = -self.detriment
        self.benefit.latex = r'{benf}'

        # social success is a balance of benefit and detriment
        self.success = State(
            types_idc=(Social),
            label='Social Success',
            latex=r'{succ}',
        )
        self.success.add = self.benefit
        self.success.sub = self.detriment

        ############################################

        # Monetary
        self.earn = Impact(
            types_res=Currency,
            types_dres=Resource,
            types_opr=(Process, Storage, Transport),
            label='Transact',
        )
        self.spend = -self.earn

        # Economic revenue is a balance of earn and spend
        self.revenue = State(
            types_res=Currency,
            label='Revenue',
            latex=r'{rev}',
        )
        self.revenue.add = self.earn
        self.revenue.sub = self.spend
