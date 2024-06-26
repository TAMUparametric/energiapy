"""Localization of parameters declared at Resource or Process level
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple, Union

from .paramtype import LocalizationType


@dataclass
class Localization:
    """Localizes parameters declared at the Resource or Process level
    limited to purchase_price, cons_max, sell_price for Resource
    and cap_max, cap_min, capex, fopex, vopex, incidental for Process

    Args:
        value (Tuple[float, int]): numeric value to be multiplied by Resource or Process parameter
        component (Union['Process', 'Resource']): self explanatory
        ltype (LocalizationType): type of localization. see energiapy.components.parameters.paramtype
        location (Location): provide the Location
    """

    value: Tuple[float, int]
    component: Union['Process', 'Resource']
    ltype: LocalizationType
    location: Optional['Location']

    def __post_init__(self):
        self.name = f'{self.location.name}_{self.component.name}_{str(self.ltype).lower()}'.replace(
            'localizationtype.', '')

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name