from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from pandas import DataFrame

from ..components.temporal_scale import TemporalScale
from .data import Data
from .theta import Theta, birth_theta
from .type.disposition import SpatialDisp, TemporalDisp
from .type.aspect import Limit, CashFlow, Land, Life, Loss, Emission
from .type.variability import Certainty, Approach
from .type.bound import Bound


@dataclass
class Parameter:
    value: Union[float, bool, 'BigM', List[float], List[Union[float, 'BigM']],
                 DataFrame, Dict[float, DataFrame], Dict[float, Data], Tuple[float], Theta]
    aspect: Union[Limit, CashFlow,
                  Land, Life, Loss, Emission]
    component: Union['Resource', 'Process', 'Location', 'Transport', 'Network']
    declared_at: Union['Resource', 'Process',
                       'Location', 'Transport', Tuple['Location'], 'Network']
    temporal: TemporalDisp = None
    bound: Bound = None
    certainty: Certainty = None
    approach: Approach = None
    scales: TemporalScale = None

    def __post_init__(self):
        
        if isinstance(self.value, (tuple, Theta)):
            theta_ = birth_theta(
                value=self.value, component=self.component, declared_at=self.declared_at, aspect=self.aspect,
                temporal=self.temporal)
            self.value = theta_
            self.theta_bounds = theta_.bounds
            for i in ['name', 'index']:
                setattr(self, i, getattr(theta_, i))

        if isinstance(self.value, (DataFrame, Data)):
            data_ = Data(data=self.value, scales=self.scales, component=self.component, declared_at=self.declared_at,
                             aspect=self.aspect)
            self.value = data_
            for i in ['temporal', 'name', 'nominal', 'index', 'disposition']:
                setattr(self, i, getattr(data_, i))
        
        if self.declared_at.class_name() in ['Process', 'Location', 'Linkage']:
            if self.declared_at.class_name()!= self.component.class_name():
                self.spatial = (getattr(SpatialDisp, self.component.class_name(
                ).upper()), getattr(SpatialDisp, self.declared_at.class_name().upper()))
            else:
                self.spatial = getattr(
                    SpatialDisp, self.declared_at.class_name().upper())
        else:
            self.spatial = SpatialDisp.NETWORK

        self.disposition = ((self.spatial), self.temporal)

        par = f'{self.aspect.name.lower().capitalize()}'
        comp = f'{self.component.name}'
        dec_at = f'{self.declared_at.name}'
        temp = f'{self.temporal.name.lower()}'
        
        if self.bound == Bound.LOWER:
            bnd = '_lb'
        elif self.bound == Bound.UPPER:
            bnd = '_ub'
        else:
            bnd = ''
            
        if not hasattr(self, 'name'):
            self.index = tuple(dict.fromkeys([comp, dec_at, temp]).keys())
            self.name = f'{par}{bnd}{self.index}'

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
