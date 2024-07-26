"""energiapy.Resource - Resource as refined in the RT(M)N framework
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..funcs.aspect import aspecter
from ..funcs.name import is_named, namer
from ..funcs.component import initializer
from ..funcs.print import printer
from .component import Component
from ..model.type.aspect import Aspects
from ..model.type.input import Input
from .type.resource import ResourceType

if TYPE_CHECKING:
    from ..model.type.alias import (IsCashFlow, IsDepreciated, IsDetail,
                                    IsEmission, IsLimit)
    from .horizon import Horizon


@dataclass
class Resource(Component):
    # Limit Aspect
    discharge: IsLimit = field(default=None)
    consume: IsLimit = field(default=None)
    # CashFlowType
    sell_cost: IsCashFlow = field(default=None)
    purchase_cost: IsCashFlow = field(default=None)
    credit: IsCashFlow = field(default=None)
    penalty: IsCashFlow = field(default=None)
    # EmissionType
    gwp: IsEmission = field(default=None)
    odp: IsEmission = field(default=None)
    acid: IsEmission = field(default=None)
    eutt: IsEmission = field(default=None)
    eutf: IsEmission = field(default=None)
    eutm: IsEmission = field(default=None)
    # Details
    basis: IsDetail = field(default=None)
    block: IsDetail = field(default=None)
    label: IsDetail = field(default=None)
    citation: IsDetail = field(default=None)
    # Depreciated
    sell: IsDepreciated = field(default=None)
    varying: IsDepreciated = field(default=None)
    price: IsDepreciated = field(default=None)
    revenue: IsDepreciated = field(default=None)
    cons_max: IsDepreciated = field(default=None)
    store_max: IsDepreciated = field(default=None)
    store_min: IsDepreciated = field(default=None)

    def __post_init__(self):

        initializer(component=self)

        # set at Process, Storage, Transport respectively
        self.produce, self.store, self.transport = (None for _ in range(3))

        # *-----------------Set ctype (ResourceType)---------------------------------

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
        _name = getattr(self, 'name', None)
        _changed = {'store_max': 'store', 'store_min': 'store', 'cons_max': 'consume',
                    'sell': 'discharge and sell_cost', 'price': 'purchase_cost', 'revenue': 'sell_cost'}

        for i, j in _changed.items():
            if getattr(self, i):
                raise ValueError(
                    f'{_name}: {i} is depreciated. Please use {j} instead')

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if is_named(component=self, attr_value=value):
            if Input.match(name) in self.aspects():
                aspecter(component=self, attr_name=name, attr_value=value)

    # # *----------------- Methods --------------------------------------

    # def make_named(self, name: str, horizon: Horizon):
    #     """names and adds horizon to the Resource

    #     Args:
    #         name (str): name given as Scenario.name = Resource(...)
    #         horizon (Horizon): temporal horizon
    #     """
    #     namer(component=self, name=name, horizon=horizon)

    # def params(self):
    #     """prints parameters of the Resource
    #     """
    #     printer(component=self, print_collection='parameters')

    # def vars(self):
    #     """prints variables of the Resource
    #     """
    #     printer(component=self, print_collection='variables')

    # def cons(self):
    #     """prints constraints of the Resource
    #     """
    #     printer(component=self, print_collection='constraints')

    # *-----------------Methods--------------------

    # @ staticmethod
    # def cname() -> str:
    #     """Returns class name
    #     """
    #     return 'Resource'

    @ staticmethod
    def aspects() -> list:
        """Returns Resource aspects
        """
        return Aspects.resource

    # __hash__ = Component.__hash__
    # __eq__ = Component.__eq__
    # __repr__ = Component.__repr__

    # # *-----------------Magics--------------------

    # def __lt__(self, other):
    #     return getattr(self, 'name') < other.name

    # def __gt__(self, other):
    #     return getattr(self, 'name') > other.name

    # # *----------- Dunders------------------------

    # def __repr__(self):
    #     return str(getattr(self, 'name'))

    # def __hash__(self):
    #     return hash(getattr(self, 'name'))

    # def __eq__(self, other):
    #     return getattr(self, 'name') == other.name

# @dataclass
# class ResourceStored(Resource):
#     capacity: float
#     land_use: float = None  # Union[float, Tuple[float], Theta]
#     material_cons: Union[Dict[Union[int, str],
#                               Dict[Material, float]], Dict[Material, float]] = None
#     # Expenditure
#     capex: Union[float, dict, Tuple[float], Theta] = None
#     pwl: dict = None  # piece wise linear capex
#     fopex: Union[float, Tuple[float], Theta] = None
#     vopex: Union[float, Tuple[float], Theta] = None
#     incidental: Union[float, Tuple[float], Theta] = None
#     # Emission
#     gwp: Union[float, Tuple[float], Theta] = None
#     odp: Union[float, Tuple[float], Theta] = None
#     acid: Union[float, Tuple[float], Theta] = None
#     eutt: Union[float, Tuple[float], Theta] = None
#     eutf: Union[float, Tuple[float], Theta] = None
#     eutm: Union[float, Tuple[float], Theta] = None
#     # Readiness
#     introduce: Union[float, Tuple[float], Theta] = None
#     retire: Union[float, Tuple[float], Theta] = None
#     lifetime: Union[float, Tuple[float], Theta] = None
#     pfail: Union[float, Tuple[float], Theta] = None
