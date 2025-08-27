"""DecisionSpace of the Model"""

from dataclasses import dataclass

from ..components.commodity.misc import Cash, Material
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

    def __post_init__(self):

        # ------Capacity Sizing-------#
        # increases the capacity of an operation
        self.setup = Control(
            Operation=(Process, Transport),
            label='Capacitate Operation',
            latex=r'{cap}^{P+}',
        )
        # decreases the capacity of an operation
        self.dismantle = -self.setup
        self.dismantle.latex = r'{cap}^{P-}'

        # operating capacity state variable
        self.capacity = State(
            Operation=(Process, Transport),
            label='Operational Capacity',
            latex=r'{cap}^{P}',
        )
        self.capacity.add = self.setup
        self.capacity.sub = self.dismantle

        # increases the inventory capacity of an operation
        self.invsetup = Control(
            Operation=(Storage,),
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
            Resource=Resource,
            Operation=Storage,
            label='Inventory Capacity',
            latex=r'{cap}^{S}',
        )
        self.invcapacity.add = self.invsetup
        self.invcapacity.sub = self.invdismantle

        # -------Operational Scheduling-------#

        # Increases the operating level
        self.rampup = Control(
            Operation=(Process, Storage, Transport),
            label='Ramp Capacity Utilization',
            latex=r'{opr}^{+}',
        )
        # Decreases the operating level
        self.rampdown = -self.rampup
        self.rampdown.latex = r'{opr}^{-}'

        # Operating Level
        self.operate = State(
            Operation=(Process, Storage, Transport),
            label='Capacity Utilization',
            latex=r'{opr}',
        )
        self.operate.bound = self.capacity
        self.operate.add = self.rampup
        self.operate.sub = self.rampdown

        # ------Trade-------#

        ## Buy - Positive trade which brings in resource
        # increases the amount of resource being bought
        self.buy_more = Control(
            Resource=Resource,
            label='Buy More Resource',
            latex=r'{buy}^{+}',
        )

        # decreases the amount of resource being sold
        self.buy_less = -self.buy_more
        self.buy_less.latex = r'{buy}^{-}'

        self.buy = Stream(
            Resource=Resource, label='Exchange Resource with other player'
        )
        self.buy.add = self.buy_more
        self.buy.sub = self.buy_less

        ## Sell - Negative trade which takes out resource
        # increases the amount of resource being sold
        self.sell_more = Control(
            Resource=Resource,
            label='Sell More Resource',
            latex=r'{sell}^{+}',
        )
        # decreases the amount of resource being bought
        self.sell_less = -self.sell_more
        self.sell_less.latex = r'{sell}^{-}'

        self.sell = -self.buy
        self.sell.add = self.sell_more
        self.sell.sub = self.sell_less

        # ------Streams-------#

        ## Flow

        # going into inventory
        # Inventory Levels
        self.inventory = Stream(
            Resource=Resource,
            Operation=Storage,
            label='Store Resource',
            latex=r'{inv}',
        )
        self.inventory.ispos = False
        self.inventory.bound = self.invcapacity

        # Production
        self.produce = Stream(
            Resource=Resource,
            Operation=(Process, Storage, Transport),
            label='Resource Stream caused by Operation',
            latex=r'{prod}',
            create_grb=False,
        )
        self.expend = -self.produce
        self.expend.latex = r'{expd}'

        ##  Free Movements of goods
        self.consume = Stream(
            Resource=Resource,
            label='Free Resource Stream',
            latex=r'{cons}',
        )

        self.release = -self.consume
        self.release.latex = r'{rlse}'

        # Monetary
        self.earn = Impact(
            Resource=Cash,
            DResource=Resource,
            Operation=(Process, Storage, Transport),
            label='Transact',
        )
        self.spend = -self.earn

        # Freight
        self.ship_in = Stream(
            Resource=Resource,
            Operation=Transport,
            label='Resource Stream between Locations',
            create_grb=False,
        )
        self.ship_in.latex = r'{impt}'
        self.ship_out = -self.ship_in
        self.ship_out.latex = r'{expt}'

        # Utilization
        self.dispose = Stream(
            Resource=Resource,
            Operation=(Process, Storage, Transport),
            label='Utilize Resource',
            latex=r'{disp}',
            create_grb=False,
        )
        self.use = -self.dispose

        # ------Consequences-------#

        # Environmental
        self.emit = Impact(
            Resource=Environ,
            DResource=(Resource, Material),
            Operation=(Process, Storage, Transport),
            label='Emit',
        )
        self.abate = -self.emit
        # change is the balance of emit and abate
        self.change = Impact(
            Indicator=(Environ),
            label='Environmental Change',
            latex=r'{chng}',
        )
        self.change.add = self.emit
        self.change.sub = self.abate

        # Social
        self.detriment = Impact(
            Indicator=Social, Resource=Resource, label='Detriment', latex=r'{detr}'
        )
        self.benefit = -self.detriment
        self.benefit.latex = r'{benf}'

        # social success is a balance of benefit and detriment
        self.success = Impact(
            Indicator=(Social),
            label='Social Success',
            latex=r'{succ}',
        )
        self.success.add = self.benefit
        self.success.sub = self.detriment

        # Economic revenue is a balance of earn and spend
        self.revenue = Impact(
            Resource=Cash,
            label='Revenue',
            latex=r'{rev}',
        )
        self.revenue.add = self.earn
        self.revenue.sub = self.spend
