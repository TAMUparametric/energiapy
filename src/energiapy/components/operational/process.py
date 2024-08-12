"""energiapy.Process - converts one Resource to another Resource, Or stores Resource
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._defined import _Operational

# import operator
# from functools import reduce


if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class Process(_Operational):

    # Depreciated
    varying: str = field(default=None)
    prod_max: str = field(default=None)
    prod_min: str = field(default=None)

    def __post_init__(self):
        _Operational.__post_init__(self)

        # *-----------------Set ctype (ProcessType)----------------------------

        # Materials are not necessarily consumed (NO_MATMODE), if use is None
        # If consumed, there could be multiple modes of consumption (MULTI_MATMODE) or one (SINGLE_MATMODE)
        # for MULTI_MATMODE, provide a dict of type ('material_mode' (str,
        # int): {Material: float})

        # if self.material_use is None:
        #     getattr(self, 'ctypes').append(ProcessType.NO_MATMODE)

        # else:
        #     if get_depth(self.material_use) > 1:
        #         getattr(self, 'ctypes').append(ProcessType.MULTI_MATMODE)
        #         self.material_modes = list(self.material_use)
        #         self.materials = list(
        #             reduce(
        #                 operator.or_,
        #                 (set(self.material_use[i]) for i in self.material_modes),
        #                 set(),
        #             )
        #         )
        #     else:
        #         getattr(self, 'ctypes').append(ProcessType.SINGLE_MATMODE)
        #         self.materials = list(self.material_use)

        # if self.capex_pwl:
        #     getattr(self, 'ctypes').append(ProcessType.PWL_CAPEX)
        #     self.capacity_segments = list(self.capex_pwl)
        #     self.capex_segments = list(self.capex_pwl.values())
        # else:
        #     getattr(self, 'ctypes').append(ProcessType.LINEAR_CAPEX)

        # # if any expenditure is incurred
        # if any([self.capex, self.fopex, self.vopex, self.incidental]):
        #     getattr(self, 'ctypes').append(ProcessType.EXPENDITURE)

        # # if it requires land to set up
        # if self.land_use:
        #     getattr(self, 'ctypes').append(ProcessType.LAND)

        # # if this process fails
        # if self.pfail:
        #     getattr(self, 'ctypes').append(ProcessType.FAILURE)

        # # if this process has some readiness aspects defined
        # if any([self.introduce, self.retire, self.lifetime]):
        #     getattr(self, 'ctypes').append(ProcessType.READINESS)

        # *----------------- Depreciation Warnings-----------------------------

        _name = getattr(self, 'name', None)

        _changed = {'prod_max': 'cap_max', 'prod_min': 'cap_min'}

        for i, j in _changed.items():
            if getattr(self, i):
                raise ValueError(
                    f'{_name}: {i} is depreciated. Please use {j} instead')

    @staticmethod
    def quantify():
        """The quantified data inputs to the component"""
        return ['capacity', 'operate', 'use']

    @staticmethod
    def expenses():
        """The quantified costs of the component"""
        return ['capex', 'opex']

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'processes'
