from dataclasses import dataclass
from typing import Union, Tuple, List, Set, Dict
from .parameters.mpvar import Theta, create_mpvar
from .parameters.factor import Factor
from pandas import DataFrame
from .parameters.paramtype import *
from .parameters.special import Big, BigM
from .temporal_scale import TemporalScale 

@dataclass
class Parameter:
    value: Union[float, bool, 'BigM', List[float], List[Union[float, 'BigM']],
                 DataFrame, Dict[float, DataFrame], Dict[float, Factor], Tuple[float], Theta]
    ptype: ParameterType
    spatial: SpatialDisp
    temporal: TemporalDisp
    component: Union['Resource', 'Process', 'Location', 'Transport', 'Network']
    psubtype: Union[Limit, CashFlow,
                    Land, Life, Loss] = None
    declared_at: Union['Process', 'Location', 'Transport', 'Network'] = None
    scales: TemporalScale = None

    def __post_init__(self):

        if not self.spatial:
            self.spatial = SpatialDisp.NETWORK

        if not self.temporal:
            self.temporal = TemporalDisp.HORIZON

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

        if isinstance(self.value, (dict, DataFrame)):
            self.vtype = VariabilityType.UNCERTAIN
            self.vsubstype = UncertaintyType.DETERMINISTIC
            if isinstance(self.value, dict):
                self.nominal = list(self.value)[0]
                self.value = self.value.values()[0]

            factor_ = Factor(data=self.value, scales=self.scales, component=self.component, declared_at=self.declared_at, psubtype=self.psubtype,
                             spatial=self.spatial, temporal=self.temporal)
            self.value = factor_
            #TODO Set temporal disposition 

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
