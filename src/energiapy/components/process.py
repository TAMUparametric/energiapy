"""energiapy.Process - converts one Resource to another Resource, Or stores Resource  
"""

from __future__ import annotations

import operator
from dataclasses import dataclass
from functools import reduce
from typing import TYPE_CHECKING

from ..funcs.aspect import aspecter, is_aspect_ready
from ..funcs.name import namer
from ..funcs.print import printer
from ..model.specialparams.conversion import Conversion
from ..model.type.aspect import (AspectType, CapBound, CashFlow, Emission,
                                 Land, Life, Limit, Loss)
from ..utils.data_utils import get_depth
from .type.process import ProcessType

if TYPE_CHECKING:
    from ..model.type.aliases import (IsCapBound, IsCashFlow, IsConversion,
                                      IsEmission, IsLand, IsLife, IsLimit,
                                      IsLoss, IsMatCons)
    from .horizon import Horizon
    from .material import Material
    from .resource import Resource


@dataclass
class Process:

    conversion: IsConversion
    # Design parameters
    capacity: IsLimit
    produce: IsCapBound
    land_use: IsLand = None
    material_cons: IsMatCons = None
    # Expenditure
    capex: IsCashFlow = None
    pwl: dict = None  # piece wise linear capex
    fopex: IsCashFlow = None
    vopex: IsCashFlow = None
    incidental: IsCashFlow = None
    # Emission
    gwp: IsEmission = None
    odp: IsEmission = None
    acid: IsEmission = None
    eutt: IsEmission = None
    eutf: IsEmission = None
    eutm: IsEmission = None
    # Readiness
    introduce: IsLife = None
    retire: IsLife = None
    lifetime: IsLife = None
    pfail: IsLife = None
    # These go to storage_resource defined in STORAGE Process
    # LimitType
    discharge: IsLimit = None
    consume: IsLimit = None
    store: IsCapBound = None
    produce: IsCapBound = None
    # LossType
    store_loss: IsLoss = None
    # CashFlowType
    sell_cost: IsCashFlow = None
    purchase_cost: IsCashFlow = None
    store_cost: IsCashFlow = None
    credit: IsCashFlow = None
    penalty: IsCashFlow = None
    # Details
    basis: str = None
    block: str = None
    citation: str = None
    label: str = None
    trl: str = None
    # Depreciated
    varying: list = None
    prod_max: float = None
    prod_min: float = None

    def __post_init__(self):

        self.named, self.name, self.horizon = (None for _ in range(3))

        self.parameters, self.variables, self.constraints = (
            list() for _ in range(3))

        self.declared_at = self

        for i in ['produce', 'store', 'transport', 'transport_loss', 'transport_cost']:
            setattr(self, i, None)

        # *-----------------Set ctype (ProcessType)---------------------------------

        if not hasattr(self, 'ctype'):
            self.ctype = list()

        # conversion can be single mode (SINGLE_PRODMODE) or multimode (MULTI_PRODMODE)
        # For MULTI_PRODMODE, a dict of type {'mode' (str, int) : {Resource: float}} needs to be provided

        self.conversion = Conversion(
            conversion=self.conversion, process=self)
        self.involve = self.conversion.involve

        if not self.produce:
            self.produce = {self.conversion.produce: 1}

        if hasattr(self.conversion, 'stored_resource'):
            self.stored_resource = self.conversion.stored_resource
            for i in ['store', 'store_loss', 'store_cost']:
                setattr(
                    self, i, {self.conversion.stored_resource: getattr(self, i)})

        for i in ['discharge', 'consume']:
            if not getattr(self, i):
                setattr(
                    self, i, {r: True for r in getattr(self.conversion, i)})
            elif getattr(self, i) and isinstance(getattr(self, i), dict):
                dict_ = getattr(self, i)
                setattr(self, i, {r: dict_.get(r, True)
                        for r in getattr(self.conversion, i)})
            else:
                raise ValueError(
                    f'{i} should be a dictionary of some or all resources in conversion.{i}')

        self.modes = self.conversion.modes
        self.n_modes = self.conversion.n_modes

        if self.n_modes > 1:
            self.ctype.append(ProcessType.MULTI_PRODMODE)
        elif self.n_modes == 1:
            self.ctype.append(ProcessType.SINGLE_PRODMODE)
        elif self.n_modes == 0:
            self.ctype.append(ProcessType.STORAGE)

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

        if self.pwl:
            self.ctype.append(ProcessType.PWL_CAPEX)
            self.capacity_segments = list(self.pwl)
            self.capex_segments = list(self.pwl.values())
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
        if is_aspect_ready(component=self, attr_name=name, attr_value=value):
            if AspectType.match(name) in self.aspects():
                aspecter(component=self, attr_name=name, attr_value=value)

            elif AspectType.match(name) in self.resource_aspects():
                current_value = getattr(self, name)
                for j in current_value:
                    j.declared_at = self
                    setattr(j, name, current_value[j])

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
        """Returns class name"""
        return 'Process'

    @staticmethod
    def aspects() -> list:
        """Returns Process aspects"""
        return CashFlow.process() + Land.process() + Limit.process() + Life.all() + Emission.all()

    @staticmethod
    def resource_aspects() -> list:
        """Returns Resource aspects at Process level"""
        return CashFlow.resource() + Limit.resource() + Loss.process() + CapBound.process()

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
