"""Task Master relates attributes to Elements
"""

from ...information.dimension import Component
from ...game.decision import Decision


class Chanakya(Component):
    """Taskmaster, collects decisions"""

    def __init__(self, name: str, default: bool = True):
        super().__init__(name)
        self.default = default
        # collect decision objects
        self.decisions: list[Decision] = []

        if self.default:
            # ------The Default Setup-----
            # There is a Player taking some decisions
            # The player maintains some level of ownership
            # if + own the player has some resource
            # if -own the player needs some resource
            # Players owns and needs can change over time
            # Space is represented through Locations and Linkages
            # Time is represented through Scales
            self.own = Decision()
            #
            # Need to be taken before production
            # setup and operation an operation - Cap^lb(opn,l,t0) <= cap(opn, l, min(|t0|,|t1|)) <= Cap^ub(opn,l,t1)
            self.capacitate = Decision()

            #
            self.trade = Decision()
            # operate an operation - opr includes, prd, inv, exp (levels of Production, Storage, Transit)
            # process prd(res,pro,spt,t0) <= cap(pro,l,t2)
            # storage inv(res,stg,spt,t0) <= cap(stg,l,t2)
            # transit exp(res,trn,spt,t0) <= cap(trn,l,t2)
            self.operate = Decision()

            # hold resource for certain time
            # Cnv(res, opn)*opr(opn,l,t0) <= Cap^f(opn,l,t1).cap(opn,l,t2)
            self.hold = Decision(self.operate)
            # send resource elsewhere
            self.ship = Decision(self.operate)
            # exchange of resource as a commodity between players
            self.trade = Decision()

            self.transact = Decision(self.trade, self.setup, self.operate)
            self.permeate = Decision(self.store, self.ship, self.operate)
            self.pollute = Decision(self.trade, self.setup, self.permeate)
            self.impact = Decision(self.trade, self.setup, self.pollute, self.permeate)

    def __setattr__(self, name: str, decision: Decision):
        if isinstance(decision, Decision):
            decision.name = name
            decision.pos = +decision
            decision.neg = -decision
            self.decisions.append(decision)

        super().__setattr__(name, decision)
