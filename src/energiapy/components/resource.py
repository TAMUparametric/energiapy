"""energiapy.Resource - Resource as refined in the RT(M)N framework  
"""
import uuid
from dataclasses import dataclass
from typing import List, Union
from ..model.aspect import Aspect
from ..model.type.aspect import CashFlow, Emission, Limit, Loss
from .temporal_scale import TemporalScale
from .type.resource import ResourceType


@dataclass
class Resource:
    # Limit Aspect
    discharge: Limit.types() = None
    consume: Limit.types() = None
    store: Limit.types() = None
    transport:  Limit.types() = None
    # LossType
    store_loss: Loss.types() = None
    # CashFlowType
    sell_cost: CashFlow.types() = None
    purchase_cost: CashFlow.types() = None
    store_cost: CashFlow.types() = None
    credit: CashFlow.types() = None
    penalty: CashFlow.types() = None
    # EmissionType
    gwp: Emission.types() = None
    odp: Emission.types() = None
    acid: Emission.types() = None
    eutt: Emission.types() = None
    eutf: Emission.types() = None
    eutm: Emission.types() = None
    # Details
    basis: str = None
    block: Union[str, list, dict] = None
    label: str = None
    citation: str = None
    # Types
    ctype: List[ResourceType] = None
    # Depreciated
    sell: bool = None
    varying: bool = None
    price: bool = None
    revenue: bool = None
    cons_max: bool = None
    store_max: bool = None
    store_min: bool = None

    def __post_init__(self):

        self.name, self.horizon = None, None

        for i in ['parameters', 'variables', 'constraints']:
            setattr(self, i, list())

        # *-----------------Set ctype (ResourceType)---------------------------------
        # .DISCHARGE allows the resource to be discharged (consume > 0)
        # .SELL is when a Resource generated revenue (has a sell_cost)
        # .CONSUME is when a Resource can be consumed
        # .PURCHASE is when a consumed Resource has a purchase_cost
        # .IMPLICIT is when a Resource only exists insitu (not discharged or consumed)
        # .PRODUCED is when a Resource is produced by a Process
        # .SELL and .DEMAND imply that .DISCHARGE is True
        # .STORE is set if a store_max is given
        # .DEMAND is set if a specific demand for resource is declared at Location
        # .TRANSPORT is set if a Resource is in the set Transport.resources
        # storage resources are also generated implicitly if a Resource is provided to a Process as storage

        if not self.ctype:
            self.ctype = list()

        if self.sell_cost is not None:
            self.ctype.append(ResourceType.SELL)
            if self.discharge is None:
                self.discharge = True

        if self.discharge is not None:
            self.ctype.append(ResourceType.DISCHARGE)

        if self.consume is not None:
            self.ctype.append(ResourceType.CONSUME)
        else:
            # if it is not consumed from outside the system, it has to be made in the system
            self.ctype.append(ResourceType.PRODUCE)
            if self.discharge is None:
                # is not discharged or consumed. Produced and used within the system captively
                self.ctype.append(ResourceType.IMPLICIT)

        if self.purchase_cost:
            self.ctype.append(ResourceType.PURCHASE)
            if self.consume is None:
                self.consume = True

        if self.store is not None:
            self.ctype.append(ResourceType.STORE)

        # *----------------- Update Aspect ---------------------------------

        # for i in self.aspects():  # iter over all aspects
        #     if self.name:
        #         asp_ = i.name.lower()  # get name of aspect
        #         if getattr(self, asp_) is not None:
        #             attr = getattr(self, asp_)
        #             aspect = Aspect(aspect=i, component=self)
        #             aspect.add(value=attr, aspect=i, component=self,
        #                         horizon=self.horizon, declared_at=self)
        #             setattr(self, asp_, aspect)

        # *----------------- Depreciation Warnings---------------------------------

        if self.store_max:
            raise ValueError(
                f'{self.name}: store_max is depreciated. Please use store instead')
        if self.store_min:
            raise ValueError(
                f'{self.name}: store_min is depreciated. Please use store instead')
        if self.cons_max:
            raise ValueError(
                f'{self.name}: cons_max is depreciated. Please use consume instead')
        if self.sell:
            raise ValueError(
                f'{self.name}: sell has been depreciated. set discharge = True and specify selling_price if needed')
        if self.varying:
            raise ValueError(
                f'{self.name}: varying has been depreciated. Variability will be intepreted based on data provided to energiapy.Location factors')
        if self.price:
            raise ValueError(
                f'{self.name}: price has been depreciated. Please use purchase_cost instead')
        if self.revenue:
            raise ValueError(
                f'{self.name}: revenue has been depreciated. Please use sell_cost instead')
        if self.revenue:
            raise ValueError(
                f'{self.name}: cons_max has been depreciated. Please use consume instead')

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

        if hasattr(self, 'name') and self.name and hasattr(self, 'horizon') and self.horizon:
            for i in self.aspects():  # iter over all aspects
                asp_ = i.name.lower()  # get name of aspect
                attr = getattr(self, asp_)
                if attr is not None and not isinstance(attr, Aspect):
                    aspect = Aspect(aspect=i, component=self)
                    aspect.add(value=attr, aspect=i, component=self,
                                horizon=self.horizon, declared_at=self)
                    setattr(self, asp_, aspect)

        for i in ['parameters', 'variables', 'constraints']:
            if hasattr(getattr(self, name), i):
                getattr(self, i).extend(getattr(getattr(self, name), i))

    def params(self):
        """prints parameters
        """
        for i in getattr(self, 'parameters'):
            print(i)

    def vars(self):
        """prints variables
        """
        for i in getattr(self, 'variables'):
            print(i)

    def cons(self):
        """prints constraints
        """
        for i in getattr(self, 'constraints'):
            print(i)

    # *-----------------Methods--------------------

    @staticmethod
    def aspects() -> list:
        """Returns Resource aspects"""
        return Limit.resource() + CashFlow.resource() + Emission.all() + Loss.resource()

    @staticmethod
    def cname() -> str:
        """Returns class name"""
        return 'Resource'

    # *-----------------Magics--------------------

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    # *----------- Dunders------------------------

    def __repr__(self):
        return str(self.name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
