"""energiapy.Process - converts one Resource to another Resource, Or stores Resource
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from ...parameters.data.conversion import Conversion
from ._operational import _Operational

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsLocation
    from ..._core._aliases._is_input import (IsBoundInput, IsConvInput,
                                             IsExactInput)


@dataclass
class Process(_Operational):
    """Process converts one Resource to another Resource"""

    # These are all from Resource
    buy: IsBoundInput = field(default=None)
    sell: IsBoundInput = field(default=None)
    buy_price: IsExactInput = field(default=None)
    sell_price: IsExactInput = field(default=None)
    credit: IsExactInput = field(default=None)
    penalty: IsExactInput = field(default=None)
    conversion: IsConvInput = field(default=None)
    produce: IsBoundInput = field(default=None)
    locations: List[IsLocation] = field(default=None)

    locations: IsLocation = field(default=None)
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
                raise ValueError(f'{_name}: {i} is depreciated. Please use {j} instead')

    @property
    def base(self):
        """The base resource"""
        return self.conversion.base

    @property
    def sold(self):
        """The resources sold"""
        return self.conversion.sold

    @property
    def bought(self):
        """The resources bought"""
        return self.conversion.bought

    @property
    def modes(self):
        """The modes of conversion"""
        return self.conversion.modes

    @property
    def x_conv(self):
        """The number of modes"""
        return self.conversion.n_modes

    @property
    def balance(self):
        """The balance of resources"""
        return self.conversion.balance

    @property
    def _operate(self):
        """Returns attribute value that signifies operating bounds"""
        return self.produce

    @staticmethod
    def _spatials():
        """Spatial Components where the Operation is located"""
        return 'locations'

    @staticmethod
    def resourcebnds():
        """Attrs that quantify the bounds of the Component"""
        return ['buy', 'sell']

    @staticmethod
    def resourceexps():
        """Attrs that determine resource expenses of the component"""
        return ['buy_price', 'sell_price', 'credit', 'penalty']

    @staticmethod
    def resourceloss():
        """Attrs that determine resource loss of the component"""
        return []

    @property
    def resources(self):
        """Resources in Inventory"""
        return self.conversion.involve

    def conversionize(self):
        """Makes the conversion"""

        if not isinstance(self.conversion, Conversion):
            self.conversion = Conversion(conversion=self.conversion, process=self)
