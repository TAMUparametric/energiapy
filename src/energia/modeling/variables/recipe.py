"""Recipes to create Aspects"""

from dataclasses import asdict, dataclass
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
    kind: Type[Aspect]
    label: str = ''
    add: str = ''
    sub: str = ''
    bound: str = ''
    ctrl: str = ''
    ispos: bool = True
    nn: bool = True
    types_opr: tuple[Type[Process | Storage | Transport]] = None
    types_res: Type[_Commodity] = None
    types_dres: Type[_Commodity] = None
    types_idc: Type[Indicator] = None
    latex: str = ''

    def __post_init__(self):
        self.args = {
            k: v
            for k, v in asdict(self).items()
            if k not in ('name', 'kind') and (isinstance(v, bool) or v)
        }

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
