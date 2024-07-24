"""energiapy.Resource - Resource as refined in the RT(M)N framework
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from ..model.type.input import Input
from ..funcs.aspect import aspecter
from ..funcs.name import namer, is_named
from ..funcs.print import printer
from ..model.type.aspect import CashFlow, Emission, Limit, Aspects
from .type.resource import ResourceType

if TYPE_CHECKING:
    from ..model.type.alias import IsCashFlow, IsEmission, IsLimit, IsDepreciated, IsDetail
    from .horizon import Horizon


@dataclass
class Resource:
    # Limit Aspect
    discharge: IsLimit = None
    consume: IsLimit = None
    # CashFlowType
    sell_cost: IsCashFlow = None
    purchase_cost: IsCashFlow = None
    credit: IsCashFlow = None
    penalty: IsCashFlow = None
    # EmissionType
    gwp: IsEmission = None
    odp: IsEmission = None
    acid: IsEmission = None
    eutt: IsEmission = None
    eutf: IsEmission = None
    eutm: IsEmission = None
    # Details
    basis: IsDetail = None
    block: IsDetail = None
    label: IsDetail = None
    citation: IsDetail = None
    # Depreciated
    sell: IsDepreciated = None
    varying: IsDepreciated = None
    price: IsDepreciated = None
    revenue: IsDepreciated = None
    cons_max: IsDepreciated = None
    store_max: IsDepreciated = None
    store_min: IsDepreciated = None

    def __post_init__(self):

        self.named, self.name, self.horizon = (None for _ in range(3))

        self.parameters, self.variables, self.constraints = (
            list() for _ in range(3))

        self.declared_at = self

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
        if is_named(component=self, attr_value=value):
            if Input.match(name) in Aspects.resource:
                aspecter(component=self, attr_name=name, attr_value=value)

    # *----------------- Methods --------------------------------------

    def make_named(self, name: str, horizon: Horizon):
        """names and adds horizon to the Resource

        Args:
            name (str): name given as Scenario.name = Resource(...)
            horizon (Horizon): temporal horizon
        """
        namer(component=self, name=name, horizon=horizon)

    def params(self):
        """prints parameters of the Resource
        """
        printer(component=self, print_collection='parameters')

    def vars(self):
        """prints variables of the Resource
        """
        printer(component=self, print_collection='variables')

    def cons(self):
        """prints constraints of the Resource
        """
        printer(component=self, print_collection='constraints')

    # *-----------------Methods--------------------

    @ staticmethod
    def cname() -> str:
        """Returns class name"""
        return 'Resource'

    @ staticmethod
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
