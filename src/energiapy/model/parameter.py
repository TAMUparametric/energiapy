from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from pandas import DataFrame

from ..components.temporal_scale import TemporalScale
from .bound import Big, BigM
from .factor import Factor
from .theta import Theta, birth_theta
from .type.disposition import SpatialDisp, TemporalDisp
from .type.aspect import Limit, CashFlow, Land, Life, Loss, Emission
from .type.special import SpecialParameter
from .type.variability import Variability, Uncertain
from .type.bound import Bound


@dataclass
class Parameter:
    value: Union[float, bool, 'BigM', List[float], List[Union[float, 'BigM']],
                 DataFrame, Dict[float, DataFrame], Dict[float, Factor], Tuple[float], Theta]
    aspect: Union[Limit, CashFlow,
                  Land, Life, Loss, Emission]
    component: Union['Resource', 'Process', 'Location', 'Transport', 'Network']
    declared_at: Union['Resource', 'Process',
                       'Location', 'Transport', Tuple['Location'], 'Network']
    temporal: Union[TemporalDisp, int] = 0
    scales: TemporalScale = None

    def __post_init__(self):

        if self.temporal is None:
            self.temporal = 0

        if self.declared_at.class_name() in ['Process', 'Location', 'Linkage']:
            if self.declared_at.class_name() != self.component.class_name():
                self.spatial = (getattr(SpatialDisp, self.component.class_name(
                ).upper()), getattr(SpatialDisp, self.declared_at.class_name().upper()))
            else:
                self.spatial = getattr(
                    SpatialDisp, self.declared_at.class_name().upper())
        else:
            self.spatial = SpatialDisp.NETWORK

        if isinstance(self.temporal, int) and self.temporal < 11:
            self.temporal = TemporalDisp.all()[self.temporal]
        else:
            self.temporal = TemporalDisp.T10PLUS

        self.disposition = ((self.spatial), self.temporal)

        if isinstance(self.value, (float, int)):
            self.vtype = Variability.CERTAIN
            self.bound = Bound.EXACT
            self.lb, self.ub = self.value, self.value

        if isinstance(self.value, Big) or self.value is True:
            self.vtype = Variability.CERTAIN
            self.bound = Bound.UPPER
            if self.value is True:
                self.value = BigM
            self.special = SpecialParameter.BIGM
            self.lb, self.ub = 0, BigM

        if isinstance(self.value, list):
            self.vtype = Variability.CERTAIN
            if all(isinstance(i, (float, int)) for i in self.value):
                self.bound = Bound.BOTH
                self.value = sorted(self.value)
            if any(isinstance(i, Big) for i in self.value):
                self.bound = Bound.LOWER
            self.lb, self.ub = self.value

        if isinstance(self.value, (tuple, Theta)):
            self.vtype = Variability.UNCERTAIN
            self.vsubtype = Uncertain.PARAMETRIC
            theta_ = birth_theta(
                value=self.value, component=self.component, declared_at=self.declared_at, aspect=self.aspect,
                temporal=self.temporal)
            self.bound = Bound.EXACT
            self.value = theta_
            self.lb, self.ub = self.value, self.value
            self.theta_bounds = theta_.bounds
            for i in ['special', 'name', 'index']:
                setattr(self, i, getattr(theta_, i))
            
            

        if isinstance(self.value, (dict, DataFrame, Factor)):
            self.vtype = Variability.UNCERTAIN
            self.vsubtype = Uncertain.DATA
            factor_ = Factor(data=self.value, scales=self.scales, component=self.component, declared_at=self.declared_at,
                             aspect=self.aspect)
            self.value = factor_
            for i in ['special', 'temporal', 'name', 'nominal', 'index', 'disposition']:
                setattr(self, i, getattr(factor_, i))
            
        
        if not hasattr(self, 'bound'):
            if isinstance(self.aspect, Limit):
                if self.aspect == Limit.DISCHARGE:
                    self.bound = Bound.LOWER
                    self.lb, self.ub = self.value, BigM
                else:
                    self.bound = Bound.UPPER
                    self.lb, self.ub = 0, self.value
            elif self.aspect in [Land.LAND, Life.LIFETIME]:
                self.bound = Bound.UPPER
                self.lb, self.ub = 0, self.value
            else:
                self.bound = Bound.EXACT
                self.lb, self.ub = self.value, self.value

        par = f'{self.aspect.name.lower().capitalize()}'
        comp = f'{self.component.name}'
        dec_at = f'{self.declared_at.name}'
        temp = f'{self.temporal.name.lower()}'

        if not hasattr(self, 'name'):
            self.index = tuple(dict.fromkeys([comp, dec_at, temp]).keys())
            self.name = f'{par}{self.index}'

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
