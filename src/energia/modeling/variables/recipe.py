"""Recipes to create Aspects"""

from dataclasses import dataclass
from typing import Type

from ...components.commodity._commodity import _Commodity
from ...components.impact.indicator import Indicator
from ...components.operation.process import Process
from ...components.operation.storage import Storage
from ...components.operation.transport import Transport
from .aspect import Aspect


@dataclass
class Recipe:
    """Recipe to create Aspects"""

    name: str
    aspect_type: Type[Aspect]
    label: str = ''
    add: str = ''
    sub: str = ''
    nn: bool = True
    types_opr: tuple[Type[Process | Storage | Transport]] = None
    types_res: Type[_Commodity] = None
    types_dres: Type[_Commodity] = None
    types_idc: Type[Indicator] = None
    latex: str = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
