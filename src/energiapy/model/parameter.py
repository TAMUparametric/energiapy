from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Tuple, Union

from pandas import DataFrame

# from ..components.temporal_scale import TemporalScale
from ..components.horizon import Horizon
from ..funcs.birth import birth_theta
from .index import Index
from .specialparams.dataset import DataSet
from .specialparams.theta import Theta
from .type.bound import Bound
from .type.certainty import Approach, Certainty

if TYPE_CHECKING:
    from .type.aliases import (IsAspect, IsComponent, IsDeclaredAt,
                               IsParameter, IsTemporal)


@dataclass
class Parameter:
    value: IsParameter
    aspect: IsAspect
    component: IsComponent
    declared_at: IsDeclaredAt
    temporal: IsTemporal = None
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
            for i in ['name', 'index', 'temporal']:
                setattr(self, i, getattr(theta_, i))

        if isinstance(self.value, (DataFrame, DataSet)):
            data_ = DataSet(data=self.value, horizon=self.horizon, component=self.component, declared_at=self.declared_at,
                            aspect=self.aspect, bound=self.bound)
            self.value = data_
            for i in ['temporal', 'name', 'index']:
                setattr(self, i, getattr(data_, i))

        if not hasattr(self, 'index'):
            self.index = Index(
                component=self.component, declared_at=self.declared_at, temporal=self.temporal)

        if not hasattr(self, 'name'):
            self.name = f'{self.aspect.pnamer()}{self.bound.namer()}{self.index.name}'

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
