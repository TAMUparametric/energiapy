"""energiapy.Process - converts one Resource to another Resource, Or stores Resource  
"""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from functools import reduce
from typing import TYPE_CHECKING

from ...funcs.utils.data_utils import get_depth
from ...types.component.process import ProcessType
from .._component import _Component
from ..component import Operation

if TYPE_CHECKING:
    from ...type.alias import (
        IsCapBound,
        IsCashFlow,
        IsConv,
        IsDepreciated,
        IsDetail,
        IsEmission,
        IsLand,
        IsLife,
        IsLimit,
        IsLoss,
        IsMatUse,
        IsPWL,
    )
    from ..commodity.material import Material
    from ..commodity.resource import Resource
    from ..temporal.horizon import Horizon


@dataclass
class Process(CmpInit):

    # Depreciated
    varying: IsDepreciated = field(default=None)
    prod_max: IsDepreciated = field(default=None)
    prod_min: IsDepreciated = field(default=None)

    def __post_init__(self):
        Operation.__post_init__(self)

        # *-----------------Set ctype (ProcessType)---------------------------------

        # Materials are not necessarily consumed (NO_MATMODE), if use is None
        # If consumed, there could be multiple modes of consumption (MULTI_MATMODE) or one (SINGLE_MATMODE)
        # for MULTI_MATMODE, provide a dict of type ('material_mode' (str, int): {Material: float})

        if self.material_use is None:
            getattr(self, 'ctypes').append(ProcessType.NO_MATMODE)

        else:
            if get_depth(self.material_use) > 1:
                getattr(self, 'ctypes').append(ProcessType.MULTI_MATMODE)
                self.material_modes = list(self.material_use)
                self.materials = list(
                    reduce(
                        operator.or_,
                        (set(self.material_use[i]) for i in self.material_modes),
                        set(),
                    )
                )
            else:
                getattr(self, 'ctypes').append(ProcessType.SINGLE_MATMODE)
                self.materials = list(self.material_use)

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
                raise ValueError(f'{_name}: {i} is depreciated. Please use {j} instead')

    def __setattr__(self, name, value):

        super().__setattr__(name, value)

        if self.is_ready(attr_value=value):

            if input_map.is_conv('conversion'):
                self.make_conversion()

            elif input_map.is_component_aspect(attr=name, component='process'):
                self.make_aspect(attr_name=name, attr_value=value)

            elif input_map.is_component_aspect(
                attr=name, component='resource', at='process'
            ):
                self.make_aspectshared(attr_name=name)

    @staticmethod
    def _spatial():
        return Location

    @property
    def collection(self):
        """The collection in scenario"""
        return 'processes'
