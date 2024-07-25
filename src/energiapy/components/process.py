"""energiapy.Process - converts one Resource to another Resource, Or stores Resource  
"""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from functools import reduce
from typing import TYPE_CHECKING

from ..funcs.aspect import aspectdicter, aspecter
from ..funcs.conversion import conversioner
from ..funcs.name import is_named, namer
from ..funcs.print import printer
from ..model.type.aspect import Aspects, CapBound, CashFlow, Limit
from ..model.type.input import Input
from ..utils.data_utils import get_depth
from .type.process import ProcessType

if TYPE_CHECKING:
    from ..model.type.alias import (IsCapBound, IsCashFlow, IsConv,
                                    IsDepreciated, IsDetail, IsEmission,
                                    IsLand, IsLife, IsLimit, IsLoss, IsMatCons,
                                    IsPWL)
    from .horizon import Horizon
    from .material import Material
    from .resource import Resource


@dataclass
class Process:

    conversion: IsConv
    # Design parameters
    capacity: IsLimit
    land_use: IsLand = field(default=None)
    material_cons: IsMatCons = field(default=None)
    # CapBoundType
    produce: IsCapBound = field(default=None)
    # Expenditure
    capex: IsCashFlow = field(default=None)
    fopex: IsCashFlow = field(default=None)
    vopex: IsCashFlow = field(default=None)
    incidental: IsCashFlow = field(default=None)
    # piece wise linear capex
    capex_pwl: IsPWL = field(default=None)
    # Emission
    gwp: IsEmission = field(default=None)
    odp: IsEmission = field(default=None)
    acid: IsEmission = field(default=None)
    eutt: IsEmission = field(default=None)
    eutf: IsEmission = field(default=None)
    eutm: IsEmission = field(default=None)
    # Readiness
    introduce: IsLife = field(default=None)
    retire: IsLife = field(default=None)
    lifetime: IsLife = field(default=None)
    pfail: IsLife = field(default=None)
    trl: IsLife = field(default=None)
    # These go to storage_resource defined in STORAGE Process
    # LimitType
    discharge: IsLimit = field(default=None)
    consume: IsLimit = field(default=None)
    # LossType
    store_loss: IsLoss = field(default=None)
    # CashFlowType
    sell_cost: IsCashFlow = field(default=None)
    purchase_cost: IsCashFlow = field(default=None)
    store_cost: IsCashFlow = field(default=None)
    credit: IsCashFlow = field(default=None)
    penalty: IsCashFlow = field(default=None)
    # Details
    basis: IsDetail = field(default=None)
    block: IsDetail = field(default=None)
    citation: IsDetail = field(default=None)
    label: IsDetail = field(default=None)
    # Depreciated
    varying: IsDepreciated = field(default=None)
    prod_max: IsDepreciated = field(default=None)
    prod_min: IsDepreciated = field(default=None)

    def __post_init__(self):

        self.named, self.name, self.horizon = (None for _ in range(3))

        self.parameters, self.variables, self.constraints = (
            list() for _ in range(3))

        self.declared_at = self

        # *-----------------Set ctype (ProcessType)---------------------------------

        if not hasattr(self, 'ctype'):
            self.ctype = list()

        # Materials are not necessarily consumed (NO_MATMODE), if material_cons is None
        # If consumed, there could be multiple modes of consumption (MULTI_MATMODE) or one (SINGLE_MATMODE)
        # for MULTI_MATMODE, provide a dict of type ('material_mode' (str, int): {Material: float})

        if self.material_cons is None:
            self.ctype.append(ProcessType.NO_MATMODE)
            self.materials = set()

        else:
            if get_depth(self.material_cons) > 1:
                self.ctype.append(ProcessType.MULTI_MATMODE)
                self.material_modes = set(self.material_cons)
                self.materials = reduce(
                    operator.or_, (set(self.material_cons[i]) for i in self.material_modes), set())
            else:
                self.ctype.append(ProcessType.SINGLE_MATMODE)
                self.materials = set(self.material_cons)

        if self.capex_pwl:
            self.ctype.append(ProcessType.PWL_CAPEX)
            self.capacity_segments = list(self.capex_pwl)
            self.capex_segments = list(self.capex_pwl.values())
        else:
            self.ctype.append(ProcessType.LINEAR_CAPEX)

        # if any expenditure is incurred
        if any([self.capex, self.fopex, self.vopex, self.incidental]):
            self.ctype.append(ProcessType.EXPENDITURE)

        # if it requires land to set up
        if self.land_use:
            self.ctype.append(ProcessType.LAND)

        # if this process fails
        if self.pfail:
            self.ctype.append(ProcessType.FAILURE)

        # if this process has some readiness aspects defined
        if any([self.introduce, self.retire, self.lifetime]):
            self.ctype.append(ProcessType.READINESS)

        # *----------------- Depreciation Warnings------------------------------------

        if self.prod_max:
            raise ValueError(
                f'{self.name}: prod_max has been depreciated. Please use cap_max instead')
        if self.prod_min:
            raise ValueError(
                f'{self.name}: prod_min has been depreciated. Please use cap_min instead')
        if self.varying:
            raise ValueError(
                f'{self.name}: varying has been depreciated. Variability will be intepreted based on data provided to energiapy.Location factors')

    def __setattr__(self, name, value):

        super().__setattr__(name, value)

        if is_named(component=self, attr_value=value):
            if name == 'conversion':
                conversioner(process=self)
            elif Input.match(name) in self.process_aspects():
                aspecter(component=self, attr_name=name, attr_value=value)

            elif Input.match(name) in self.resource_aspects():
                current_value = getattr(self, name)
                print(current_value)
                if isinstance(current_value, dict):
                    for j in current_value:
                        j.declared_at = self
                        setattr(j, name, current_value[j])

                    aspectdicter(component=self, attr_name=name, attr_value={
                        j: getattr(j, name)for j in getattr(self, name)})

    # *----------------- Methods --------------------------------------

    def make_named(self, name: str, horizon: Horizon):
        """names and adds horizon to the Process

        Args:
            name (str): name given as Scenario.name = Process(...)
            horizon (Horizon): temporal horizon
        """
        namer(component=self, name=name, horizon=horizon)

    def params(self):
        """prints parameters of the Process
        """
        printer(component=self, print_collection='parameters')

    def vars(self):
        """prints variables of the Process
        """
        printer(component=self, print_collection='variables')

    def cons(self):
        """prints constraints of the Process
        """
        printer(component=self, print_collection='constraints')

    # *----------------- Class Methods --------------------------------------

    @staticmethod
    def cname() -> str:
        """Returns class name
        """
        return 'Process'

    @staticmethod
    def process_aspects() -> list:
        """Returns Process aspects
        """
        return Aspects.process

    @staticmethod
    def resource_aspects() -> list:
        """Returns Resource aspects at Process level
        """
        return Limit.resource() + CashFlow.resource() + CapBound.process()

    @classmethod
    def aspects(cls) -> list:
        """Returns all aspects at Process level
        """
        return cls.process_aspects() + cls.resource_aspects()

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
