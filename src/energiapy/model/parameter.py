from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from pandas import DataFrame

# from ..components.temporal_scale import TemporalScale
from ..components.horizon import Horizon
from .dataset import DataSet
from .theta import Theta, birth_theta
from .type.aspect import CashFlow, Emission, Land, Life, Limit, Loss
from .type.bound import Bound
from .type.certainty import Approach, Certainty
from .type.disposition import SpatialDisp, TemporalDisp


@dataclass
class Parameter:
    value: Union[float, bool, 'BigM', List[float], List[Union[float, 'BigM']],
                 DataFrame, Dict[float, DataFrame], Dict[float, DataSet], Tuple[float], Theta]
    aspect: Union[Limit, CashFlow,
                  Land, Life, Loss, Emission]
    component: Union['Resource', 'Process', 'Location', 'Transport', 'Network']
    declared_at: Union['Resource', 'Process',
                       'Location', 'Transport', Tuple['Location'], 'Network']
    temporal: TemporalDisp = None
    bound: Bound = None
    certainty: Certainty = None
    approach: Approach = None
    horizon: Horizon = None

    def __post_init__(self):

        if isinstance(self.value, (tuple, Theta)):
            theta_ = birth_theta(
                value=self.value, component=self.component, declared_at=self.declared_at, aspect=self.aspect,
                temporal=self.temporal)
            self.value = theta_
            self.theta_bounds = theta_.bounds
            for i in ['name', 'index']:
                setattr(self, i, getattr(theta_, i))

        if isinstance(self.value, (DataFrame, DataSet)):
            data_ = DataSet(data=self.value, horizon=self.horizon, component=self.component, declared_at=self.declared_at,
                            aspect=self.aspect, bound=self.bound)
            self.value = data_
            for i in ['temporal', 'name', 'index', 'disposition']:
                setattr(self, i, getattr(data_, i))

        self.spatial, self.disposition = None, (self.temporal,)
        if self.declared_at.cname() != 'Resource':
            # if self.declared_at.cname() != self.component.cname():
            #     self.spatial = (self.component, self.declared_at)
            # else:
            self.spatial = self.declared_at
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

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __repr__(self):
        return str(self.name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
