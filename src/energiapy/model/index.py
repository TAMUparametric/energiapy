from dataclasses import dataclass
from .type.disposition import SpatialDisp, TemporalDisp
from typing import Tuple, Union


@dataclass
class Index:
    component: Union['Resource', 'Process', 'Location', 'Transport', 'Network']
    declared_at: Union['Resource', 'Process',
                       'Location', 'Transport', 'Network']
    temporal: TemporalDisp
    spatial: SpatialDisp
    disposition: Tuple[SpatialDisp, TemporalDisp]
    length: int

    def __post_init__(self):

        comp = f'{self.component.name}'
        dec_at = f'{self.declared_at.name}'
        temp = f'{self.temporal.name.lower()}'
        self.name = f'{tuple(dict.fromkeys([comp, dec_at, temp]).keys())}'

    def __len__(self):
        return self.length

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
