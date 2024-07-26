"""energiapy.Process - converts one Resource to another Resource, Or stores Resource  
"""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from functools import reduce
from typing import TYPE_CHECKING

from ..model.type.aspect import Aspects, CapBound, CashFlow, Limit
from ..model.type.input import Input
from ..utils.data_utils import get_depth
from .type.process import ProcessType
from .component import Component, ProcessChotu

if TYPE_CHECKING:
    from ..model.type.alias import (IsCapBound, IsCashFlow, IsConv,
                                    IsDepreciated, IsDetail, IsEmission,
                                    IsLand, IsLife, IsLimit, IsLoss, IsMatCons,
                                    IsPWL)
    from .horizon import Horizon
    from .material import Material
    from .resource import Resource


@dataclass
class Process(Component, ProcessChotu):

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
        super().__post_init__()

        # *-----------------Set ctype (ProcessType)---------------------------------

        # Materials are not necessarily consumed (NO_MATMODE), if material_cons is None
        # If consumed, there could be multiple modes of consumption (MULTI_MATMODE) or one (SINGLE_MATMODE)
        # for MULTI_MATMODE, provide a dict of type ('material_mode' (str, int): {Material: float})

        if self.material_cons is None:
            getattr(self, 'ctypes').append(ProcessType.NO_MATMODE)

        else:
            if get_depth(self.material_cons) > 1:
                getattr(self, 'ctypes').append(ProcessType.MULTI_MATMODE)
                self.material_modes = list(self.material_cons)
                self.materials = list(reduce(
                    operator.or_, (set(self.material_cons[i]) for i in self.material_modes), set()))
            else:
                getattr(self, 'ctypes').append(ProcessType.SINGLE_MATMODE)
                self.materials = list(self.material_cons)

        if self.capex_pwl:
            getattr(self, 'ctypes').append(ProcessType.PWL_CAPEX)
            self.capacity_segments = list(self.capex_pwl)
            self.capex_segments = list(self.capex_pwl.values())
        else:
            getattr(self, 'ctypes').append(ProcessType.LINEAR_CAPEX)

        # if any expenditure is incurred
        if any([self.capex, self.fopex, self.vopex, self.incidental]):
            getattr(self, 'ctypes').append(ProcessType.EXPENDITURE)

        # if it requires land to set up
        if self.land_use:
            getattr(self, 'ctypes').append(ProcessType.LAND)

        # if this process fails
        if self.pfail:
            getattr(self, 'ctypes').append(ProcessType.FAILURE)

        # if this process has some readiness aspects defined
        if any([self.introduce, self.retire, self.lifetime]):
            getattr(self, 'ctypes').append(ProcessType.READINESS)

        # *----------------- Depreciation Warnings------------------------------------

        _name = getattr(self, 'name', None)

        _changed = {'prod_max': 'cap_max', 'prod_min': 'cap_min'}

        for i, j in _changed.items():
            if getattr(self, i):
                raise ValueError(
                    f'{_name}: {i} is depreciated. Please use {j} instead')

    def __setattr__(self, name, value):

        super().__setattr__(name, value)

        if self.is_ready(attr_value=value):

            if name == 'conversion':
                self.make_conversion()

            elif Input.match(name) in self.process_aspects():
                self.make_aspect(attr_name=name, attr_value=value)

            elif Input.match(name) in self.resource_aspects():
                self.make_aspectdict(attr_name=name)

    # *----------------- Class Methods --------------------------------------

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
