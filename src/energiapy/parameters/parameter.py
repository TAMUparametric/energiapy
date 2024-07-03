from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from pandas import DataFrame

from ..components.temporal_scale import TemporalScale
from .bound import Big, BigM
from .factor import Factor
from .mpvar import Theta, create_mpvar
# from .type.parameter import (CashFlow, CertaintyType, Land, Life, Limit, Loss,
#                              ParameterType, SpatialDisp, TemporalDisp,
#                              UncertaintyType, VariabilityType)

from .type.disposition import *
from .type.property import *
from .type.special import SpecialParameter
from .type.variability import *


@dataclass
class Parameter:
    value: Union[float, bool, 'BigM', List[float], List[Union[float, 'BigM']],
                 DataFrame, Dict[float, DataFrame], Dict[float, Factor], Tuple[float], Theta]
    ptype: Property
    spatial: SpatialDisp
    temporal: TemporalDisp
    component: Union['Resource', 'Process', 'Location', 'Transport', 'Network']
    psubtype: Union[Limit, CashFlow,
                    Land, Life, Loss] = None
    declared_at: Union['Process', 'Location', 'Transport', 'Network'] = None
    scales: TemporalScale = None
    special: SpecialParameter = None

    def __post_init__(self):

        if not self.spatial:
            self.spatial = SpatialDisp.NETWORK

        if not self.temporal:
            self.temporal = TemporalDisp.HORIZON

        else:
            temporal_disps = TemporalDisp.all()
            if self.temporal < 11:
                self.temporal = temporal_disps[self.temporal]
            else:
                self.temporal = TemporalDisp.ABOVETEN

        if isinstance(self.value, (float, int)):
            self.vtype = VariabilityType.CERTAIN

            if isinstance(self.psubtype, Limit):
                if self.psubtype == Limit.DISCHARGE:
                    self.vsubstype = CertaintyType.LOWERBOUND
                else:
                    self.vsubstype = CertaintyType.UPPERBOUND

            elif self.psubtype in [Land.AVAILABLE, Life.LIFETIME]:
                self.vsubstype = CertaintyType.UPPERBOUND

            else:
                self.vsubstype = CertaintyType.EXACT

        if isinstance(self.value, Big) or self.value is True:
            self.vtype = VariabilityType.CERTAIN
            self.vsubstype = CertaintyType.UNBOUNDED
            if self.value is True:
                self.value = BigM
            self.special = SpecialParameter.BIGM

        if isinstance(self.value, list):
            self.vtype = VariabilityType.CERTAIN

            if all(isinstance(i, float) for i in self.value):
                self.vsubstype = CertaintyType.BOUNDED
                self.value = sorted(self.value)

            if any(isinstance(i, Big) for i in self.value):
                self.vsubstype = CertaintyType.LOWERBOUND

        if isinstance(self.value, (tuple, Theta)):
            self.vtype = VariabilityType.UNCERTAIN
            self.vsubstype = UncertaintyType.PARAMETRIC

            mpvar_ = create_mpvar(
                value=self.value, component=self.component, declared_at=self.declared_at, psubtype=self.psubtype,
                spatial=self.spatial, temporal=self.temporal)
            self.value = mpvar_
            self.special = SpecialParameter.MPVar

        if isinstance(self.value, (dict, DataFrame, Factor)):
            self.vtype = VariabilityType.UNCERTAIN
            self.vsubstype = UncertaintyType.DETERMINISTIC
            factor_ = Factor(data=self.value, scales=self.scales, component=self.component, declared_at=self.declared_at,
                             ptype=self.ptype, psubtype=self.psubtype, spatial=self.spatial)
            self.value = factor_
            self.special = SpecialParameter.FACTOR
            self.temporal = factor_.temporal
            # TODO Set temporal disposition

        dec_at = ''
        if self.declared_at:
            dec_at = f',{self.declared_at.name}'

        self.name = f'{self.psubtype.name.lower()}({self.component.name}{dec_at})'

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
        # set special parameter types
