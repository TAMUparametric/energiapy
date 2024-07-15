from dataclasses import dataclass
from typing import Tuple, Union

from ..components.temporal_scale import TemporalScale
from .type.aspect import CashFlow, Land, Life, Limit, Loss
from .type.bound import Bound
from .type.certainty import Approach, Certainty
from .type.disposition import SpatialDisp, TemporalDisp
from .type.special import SpecialParameter


@dataclass
class Variable:
    aspect: Union[Limit, CashFlow, Land, Life, Loss]
    component: Union['Resource', 'Process', 'Location', 'Transport', 'Network']
    declared_at: Union['Resource', 'Process',
                       'Location', 'Transport', 'Network']
    spatial: Union[SpatialDisp, Tuple[SpatialDisp]]
    temporal: TemporalDisp
    disposition: Tuple[SpatialDisp, TemporalDisp]
    index: Tuple[str]

    def __post_init__(self):
        var = f'{self.aspect.name.lower()}'
        comp = f'{self.component.name}'
        dec_at = f'{self.declared_at.name}'
        temp = f'{self.temporal.name.lower()}'

        # capacity has no resource index and is a Process or Transport property
        if self.declared_at.cname() in ['Process', 'Transport'] and self.aspect == Limit.CAPACITY:
            comp = ''

        self.index = tuple(dict.fromkeys([comp, dec_at, temp]).keys())
        self.name = f'{var}{self.index}'

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
