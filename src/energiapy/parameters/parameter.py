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
    psubtype: Union[Limit, CashFlow,
                    Land, Life, Loss]
    declared_at: Union['Process', 'Location', 'Transport', 'Network'] = None
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
                nml = f'{factor_.nominal}.'

        comp, dec_at, pst, temp = ('' for _ in range(4))

        if self.component:
            comp = f'{self.component.name}'

        if self.declared_at:
            if isinstance(self.declared_at, tuple):
                dec_at = (f'{i.name}' for i in self.declared_at)
            else:
                dec_at = f'{self.declared_at.name}'

        else:
            dec_at = f'{self.spatial.name.lower()}'

        pst = f'{self.psubtype.name.lower().capitalize()}'

        if self.temporal:
            temp = f'{self.temporal.name.lower()}'

        index = f'({comp},{dec_at},{temp})'

        self.name = f'{pst}{index}'

        var2, dom, res = ('' for _ in range(3))

        if hasattr(self.component, 'base'):
            res = getattr(self.component, 'base').name
            index = f'({res},{comp},{dec_at},{temp})'

        var = f'{pst.lower()}{index}'

        if isinstance(self.psubtype, CashFlow):
            var2 = self.variables()[self.psubtype.name]
            var2 = f'.{var2.lower()}{index}'
            var = var.replace('_cost ', '_exp')

        if th:
            par = f'Th'
            dom = f', Th in ({self.lb},{self.ub})'
            bnd = ['', '<=']
        else:
            bnd = [f'{self.lb}<=', f'<={nml}{self.ub}']
            par = f'{nml}{self.ub}'

        if self.btype == Bound.EXACT:
            self.eqn = f'{var}={par}{var2}{dom}'
        else:
            self.eqn = f'{bnd[0]}{var}{bnd[1]}{dom}'

        # self.eqn = f'{bnd[0]}<={pst}({res}{comp},{dec_at},{temp})<={bnd[1]}'

        # if th:
        #     self.eqn = f'{pst}({res}{comp},{dec_at},{temp}) = Th[{pst.capitalize}]({res}{comp},{dec_at},{temp}).{var.lower()}({res}{comp},{dec_at},{temp}), Th in ({bnd[0]},{bnd[1]})'
        # else:
        #     self.eqn = f'{pst}({res}{comp},{dec_at},{temp})={par}.{var.lower()}({res}{comp},{dec_at},{temp})'

        # else:
        #     if par:
        #         self.eqn = f'{pst}({comp},{dec_at},{temp})={par}'
        #     else:
        #         self.eqn = f'{bnd[0]}<={pst}({comp},{dec_at},{temp})<={bnd[1]}'

        self.disposition = ((self.spatial), self.temporal)
        self.index = (comp, dec_at, temp)

    @classmethod
    def variables_res(cls) -> List[str]:
        return CashFlow.variables_res()

    @classmethod
    def variables_res_pro(cls) -> List[str]:
        return CashFlow.variables_res_pro()

    @classmethod
    def variables_pro(cls) -> List[str]:
        return CashFlow.variables_res_pro()

    @classmethod
    def variables(cls) -> List[str]:
        return {**cls.variables_res(), **cls.variables_res_pro(), **cls.variables_pro()}

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

        self.component = self.params.component
        self.ptye = self.params.ptype
        self.psubtype = self.params.psubtype
        self.name = f'{self.psubtype.name.lower().capitalize()}({self.component.name})'

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
