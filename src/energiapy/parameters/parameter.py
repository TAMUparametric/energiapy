from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from pandas import DataFrame

from ..components.temporal_scale import TemporalScale
from .bound import Big, BigM
from .factor import Factor
from .mpvar import Theta, create_mpvar
# from .type.parameter import (CashFlow, Bound, Land, Life, Limit, Loss,
#                              ParameterType, SpatialDisp, TemporalDisp,
#                              Uncertain, Variability)

from .type.disposition import *
from .type.property import *
from .type.special import SpecialParameter
from .type.variability import *


@dataclass
class Parameter:
    value: Union[float, bool, 'BigM', List[float], List[Union[float, 'BigM']],
                 DataFrame, Dict[float, DataFrame], Dict[float, Factor], Tuple[float], Theta]
    ptype: Property
    spatial: Union[SpatialDisp, Tuple[SpatialDisp]]
    temporal: TemporalDisp
    component: Union['Resource', 'Process', 'Location', 'Transport', 'Network']
    declared_at: Union['Resource', 'Process',
                       'Location', 'Transport', 'Network']
    psubtype: Union[Limit, CashFlow,
                    Land, Life, Loss]
    scales: TemporalScale = None
    special: SpecialParameter = None

    def __post_init__(self):

        if not self.spatial:
            self.spatial = SpatialDisp.NETWORK

        if not self.temporal:
            self.temporal = TemporalDisp.T0
        else:
            temporal_disps = TemporalDisp.all()
            if self.temporal < 11:
                self.temporal = temporal_disps[self.temporal]
            else:
                self.temporal = TemporalDisp.T10PLUS

        if isinstance(self.psubtype, Limit):
            if self.psubtype == Limit.DISCHARGE:
                self.btype = Bound.LOWER
            else:
                self.btype = Bound.UPPER
        elif self.psubtype in [Land.LAND, Life.LIFETIME]:
            self.btype = Bound.UPPER
        else:
            self.btype = Bound.EXACT

        if isinstance(self.value, (float, int)):
            self.vtype = Variability.CERTAIN
            if self.btype == Bound.LOWER:
                self.lb, self.ub = self.value, BigM
            if self.btype == Bound.UPPER:
                self.lb, self.ub = 0, self.value
            if self.btype == Bound.EXACT:
                self.lb, self.ub = self.value, self.value

        if isinstance(self.value, Big) or self.value is True:
            self.vtype = Variability.CERTAIN
            self.btype = Bound.BIGM
            if self.value is True:
                self.value = BigM
            self.special = SpecialParameter.BIGM
            self.lb, self.ub = 0, BigM

        if isinstance(self.value, list):
            self.vtype = Variability.CERTAIN
            if all(isinstance(i, float) for i in self.value):
                self.btype = Bound.BOTH
                self.value = sorted(self.value)

            if any(isinstance(i, Big) for i in self.value):
                self.btype = Bound.LOWER

            self.lb, self.ub = self.value

        th = None
        if isinstance(self.value, (tuple, Theta)):
            self.vtype = Variability.UNCERTAIN
            self.vsubtype = Uncertain.PARAMETRIC
            mpvar_ = create_mpvar(
                value=self.value, component=self.component, declared_at=self.declared_at, psubtype=self.psubtype,
                spatial=self.spatial, temporal=self.temporal)
            self.value = mpvar_
            self.special = SpecialParameter.MPVar
            self.lb, self.ub = mpvar_.bounds
            th = ['Th[', ']']

        nml = ''
        if isinstance(self.value, (dict, DataFrame, Factor)):
            self.vtype = Variability.UNCERTAIN
            self.vsubtype = Uncertain.DATA
            factor_ = Factor(data=self.value, scales=self.scales, component=self.component, declared_at=self.declared_at,
                             ptype=self.ptype, psubtype=self.psubtype, spatial=self.spatial)
            self.value = factor_
            self.special = SpecialParameter.FACTOR
            self.temporal = factor_.temporal
            if self.btype == Bound.LOWER:
                self.lb, self.ub = self.value, BigM
            if self.btype == Bound.UPPER:
                self.lb, self.ub = 0, self.value
            if self.btype == Bound.EXACT:
                self.lb, self.ub = self.value, self.value
            if factor_.nominal != 1:
                nml = f'{factor_.nominal}*'

        comp, dec_at, pst, temp = ('' for _ in range(4))

        if self.component:
            comp = f'{self.component.name}'

        if isinstance(self.declared_at, tuple):
            dec_at = (f'{i.name},' for i in self.declared_at)

        else:
            dec_at = f'{self.declared_at.name}'

        pst = f'{self.psubtype.name.lower()}'

        if self.temporal:
            temp = f'{self.temporal.name.lower()}'

        if comp == dec_at:
            index = f'({comp},{temp})'
            self.index = (comp, temp)
        else:
            index = f'({comp},{dec_at},{temp})'
            self.index = (comp, dec_at, temp)
        
        var2, dom = ('' for _ in range(2))

        var = f'{pst}{index}'

        if self.psubtype in self.limits_capacity_bounds():
            if self.declared_at != self.component:
                # if limited by capacity at Process or Transport 
                capacity_index = [i.temporal.name.lower() for i in self.declared_at.capacity.params if i.component == self.declared_at][0]
                nml = f'capacity({dec_at},{capacity_index})*'
                
        if isinstance(self.psubtype, CashFlow):
            var = var.replace('_cost', '_exp')
            var2 = self.variables_cash()[self.psubtype.name]
            if var2 is not None:
                var2 = f'*{var2.lower()}{index}'
            else:
                var2 = ''

        if isinstance(self.psubtype, Land):
            var2 = self.variables_land()[self.psubtype.name]
            var2 = f'*{var2.lower()}{index}'

        if th:
            par = 'Th'
            dom = f', Th in ({self.lb},{self.ub})'
            bnd = ['', '<=']
        else:
            bnd = [f'{self.lb}<=', f'<={nml}{self.ub}']
            par = f'{nml}{self.ub}'

        if self.btype == Bound.EXACT:
            self.eqn = f'{var}={par}{var2}{dom}'
        else:
            self.eqn = f'{bnd[0]}{var}{bnd[1]}{dom}'

        self.disposition = ((self.spatial), self.temporal)



        self.name = f'{pst.capitalize()}{index}'

    @classmethod
    def variables_cash_res(cls) -> List[str]:
        return CashFlow.variables_res()

    @classmethod
    def variables_cash_pro(cls) -> List[str]:
        return CashFlow.variables_pro()

    @classmethod
    def variables_cash(cls) -> List[str]:
        return {**cls.variables_cash_res(), **cls.variables_cash_pro()}

    @classmethod
    def variables_land(cls) -> List[str]:
        return {**Land.variables_pro(), **Land.variables_loc()}

    @classmethod
    def limits_capacity_bounds(cls) -> List[str]:
        return Limit.capacity_bound()

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


@dataclass
class Parameters:
    params: Parameter

    def __post_init__(self):

        self.declared_at = self.params.declared_at
        self.ptye = self.params.ptype
        self.psubtype = self.params.psubtype
        self.name = f'{self.psubtype.name.lower().capitalize()}({self.declared_at.name})'
        self.dispositions = [self.params.disposition]
        self.indices = [self.params.index]
        self.eqn_list = [self.params.eqn]
        self.params = [self.params]
        
    def add(self, parameter):
        self.params.append(parameter)
        self.dispositions.append(parameter.disposition)
        self.indices.append(parameter.index)
        self.eqn_list.append(parameter.eqn)

    def eqns(self):
        for eqn in self.eqn_list:
            print(eqn)

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
