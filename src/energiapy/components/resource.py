"""energiapy.Resource - Resource as refined in the RT(M)N framework  
"""
from dataclasses import dataclass
from typing import Union
from ..model.aspect import Aspect
from ..model.type.aspect import CashFlow, Emission, Limit, AspectType
from .type.resource import ResourceType


@dataclass
class Resource:
    # Limit Aspect
    discharge: Limit.types() = None
    consume: Limit.types() = None
    # CashFlowType
    sell_cost: CashFlow.types() = None
    purchase_cost: CashFlow.types() = None
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
    # Depreciated
    sell: bool = None
    varying: bool = None
    price: bool = None
    revenue: bool = None
    cons_max: bool = None
    store_max: bool = None
    store_min: bool = None

    def __post_init__(self):

        self.named, self.name, self.horizon = (None for _ in range(3))

        self.parameters, self.variables, self.constraints = (
            list() for _ in range(3))

        self.declared_at = self

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

        if not hasattr(self, 'ctype'):
            self.ctype = list()

        if self.sell_cost is not None:
            self.ctype.append(ResourceType.SELL)
            if self.discharge is None:
                self.discharge = True

        if self.discharge is not None:
            self.ctype.append(ResourceType.DISCHARGE)

        if self.consume is not None:
            self.ctype.append(ResourceType.CONSUME)

        if self.purchase_cost:
            self.ctype.append(ResourceType.PURCHASE)
            if self.consume is None:
                self.consume = True
        # TODO update store, produce, transport

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
        if hasattr(self, 'named') and self.named and name in AspectType.aspects() and value is not None:
            current_value = getattr(self, name)

            if not isinstance(current_value, Aspect):
                new_value = Aspect(
                    aspect=AspectType.match(name), component=self)
            else:
                new_value = current_value

            if not isinstance(value, Aspect):
                new_value.add(value=value, aspect=AspectType.match(name), component=self,
                              horizon=self.horizon, declared_at=self.declared_at)
                setattr(self, name, new_value)

                for i in ['parameters', 'variables', 'constraints']:
                    if hasattr(new_value, i):
                        getattr(self, i).extend(getattr(new_value, i))

    def namer(self, name, horizon):
        self.name = name
        self.horizon = horizon
        self.named = True

        for i in AspectType.aspects():
            if hasattr(self, i) and getattr(self, i) is not None:
                setattr(self, i, getattr(self, i))

    def params(self):
        """prints parameters
        """
        for i in self.parameters:
            print(i)

    def vars(self):
        """prints variables
        """
        for i in self.variables:
            print(i)

    def cons(self):
        """prints constraints
        """
        for i in self.constraints:
            print(i)

    # *-----------------Methods--------------------

    @staticmethod
    def cname() -> str:
        """Returns class name"""
        return 'Resource'

    @staticmethod
    def aspects() -> list:
        """Returns Resource aspects"""
        return Limit.resource() + CashFlow.resource() + Emission.all()

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
