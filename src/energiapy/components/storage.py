from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Tuple, Union

from ..funcs.aspect import aspecter, is_aspect_ready
from ..model.specialparams.conversion import Conversion
from ..model.specialparams.dataset import DataSet
from ..model.specialparams.theta import Theta
from ..model.specialparams.unbound import BigM
from ..model.type.aspect import AspectType

if TYPE_CHECKING:
    from pandas import DataFrame

    from .horizon import Horizon
    from .material import Material
    from .resource import Resource


@dataclass
class Storage:
    store: Resource
    requires: List[Resource]
# Design parameters
    capacity: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                    DataFrame, Tuple[Union[float, DataFrame, DataSet]], Theta]
    produce: Union[float, bool, 'BigM',
                   List[Union[float, 'BigM']]] = None
    land_use: float = None  # Union[float, Tuple[float], Theta]
    material_cons: Union[Dict[Union[int, str],
                              Dict[Material, float]], Dict[Material, float]] = None
    # Expenditure
    capex: Union[float, dict, Tuple[float], Theta] = None
    pwl: dict = None  # piece wise linear capex
    fopex: Union[float, Tuple[float], Theta] = None
    vopex: Union[float, Tuple[float], Theta] = None
    incidental: Union[float, Tuple[float], Theta] = None
    # Emission
    gwp: Union[float, Tuple[float], Theta] = None
    odp: Union[float, Tuple[float], Theta] = None
    acid: Union[float, Tuple[float], Theta] = None
    eutt: Union[float, Tuple[float], Theta] = None
    eutf: Union[float, Tuple[float], Theta] = None
    eutm: Union[float, Tuple[float], Theta] = None
    # Readiness
    introduce: Union[float, Tuple[float], Theta] = None
    retire: Union[float, Tuple[float], Theta] = None
    lifetime: Union[float, Tuple[float], Theta] = None
    pfail: Union[float, Tuple[float], Theta] = None
    # These go to storage_resource defined in STORAGE Process
    # LimitType
    discharge: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                     DataFrame, Tuple[Union[float, DataFrame, DataSet]], Theta] = None
    consume: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                   DataFrame, Tuple[Union[float, DataFrame, DataSet]], Theta] = None
    store: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                 DataFrame, Tuple[Union[float, DataFrame, DataSet]], Theta] = None
    produce: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                   DataFrame, Tuple[Union[float, DataFrame, DataSet]], Theta] = None
    # LossType
    store_loss: Union[float, Tuple[float], Theta] = None
    # CashFlowType
    sell_cost: Union[float, Theta, DataFrame,
                     Tuple[Union[float, DataFrame, DataSet]]] = None
    purchase_cost: Union[float, Theta, DataFrame,
                         Tuple[Union[float, DataFrame, DataSet]]] = None
    store_cost: Union[float, Theta, DataFrame,
                      Tuple[Union[float, DataFrame, DataSet]]] = None
    credit: Union[float, Theta, DataFrame,
                  Tuple[Union[float, DataFrame, DataSet]]] = None
    penalty: Union[float, Theta, DataFrame,
                   Tuple[Union[float, DataFrame, DataSet]]] = None
    # Details
    basis: str = None
    block: str = None
    citation: str = None
    label: str = None
    trl: str = None

    def __post_init__(self):

        self.named, self.name, self.horizon = (None for _ in range(3))

        self.parameters, self.variables, self.constraints = (
            list() for _ in range(3))

        self.declared_at = self

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if is_aspect_ready(component=self, attr_name=name, attr_value=value):
            if AspectType.match(name) in self.aspects():
                aspecter(component=self, attr_name=name, attr_value=value)

    # *----------------- Class Methods --------------------------------------

    @staticmethod
    def cname() -> str:
        """Returns class name"""
        return 'Process'

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
