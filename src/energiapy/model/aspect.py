
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union
from .parameter import Parameter
from .variable import Variable
from .constraint import Constraint
from .type.aspect import Limit, CashFlow, Land, Life, Loss, Emission
from ..components.temporal_scale import TemporalScale
from pandas import DataFrame
from .data import Data
from .theta import Theta
from .type.disposition import SpatialDisp, TemporalDisp
from .type.variability import Certainty, Approach
from .type.match import matches
from .type.bound import Bound
from .unbound import Unbound, BigM, smallm


@dataclass
class Aspect:

    aspect: Union[Limit, CashFlow, Land, Life, Loss, Emission]
    component: Union['Resource', 'Process', 'Location', 'Transport', 'Network']

    def __post_init__(self):
        self.name = f'{self.aspect.name.lower().capitalize()}({self.component.name})'
        self.parameters = list()
        self.variables = list()
        self.constraints = list()

    def add(self, value: Union[float, bool, 'BigM', List[float], List[Union[float, 'BigM']],
                               DataFrame, Dict[int, DataFrame], Dict[int, Data], Tuple[float], Theta], aspect: Union[Limit, CashFlow, Land, Life, Loss, Emission],
            component: Union['Resource', 'Process', 'Location', 'Transport', 'Network'],
            declared_at: Union['Resource', 'Process', 'Location', 'Transport', Tuple['Location'], 'Network'], scales: TemporalScale = None):

        if isinstance(value, dict):
            for i in list(value):
                if i not in [j.name.lower() for j in TemporalDisp.all()]:
                    raise ValueError(
                        f'{self.name}: keys for dict must be a TemporalScale.scales')
        else:
            value = {'t0': value}

        for tempd_, value_ in value.items():

            bound, certainty, approach = ([None, None] for _ in range(3))

            if isinstance(value_, (float, int, DataFrame, Data)) and not isinstance(value_, bool):
                bound[0] = Bound.EXACT
                if isinstance(value_, (DataFrame, dict, Data)):
                    certainty[0], approach[0] = Certainty.UNCERTAIN, Approach.DATA
                else:
                    certainty[0], approach[0] = Certainty.CERTAIN, None
                value_ = [value_]

            elif isinstance(value_, (Unbound, bool)):
                bound[0], certainty[0], approach[0] = Bound.UNBOUNDED, Certainty.CERTAIN, None
                if value_ is True:
                    value_ = BigM
                value_ = [value_]
                
            elif isinstance(value_, (tuple, Theta)):
                bound[0], certainty[0], approach[0] = Bound.PARAMETRIC, Certainty.UNCERTAIN, Approach.PARAMETRIC
                value_ = [value_]

            elif isinstance(value_, list):
                if len(value_) > 2:
                    raise ValueError(
                        f'{self.name}: value_s must be a scalar, a tuple, or a list of length 2 or 1')

                if len(value_) == 1:
                    value_ = [0] + value_[0]

                if len(value_) == 2:
                    low_or_up = {0: Bound.LOWER, 1: Bound.UPPER}
                    value_ = [BigM if i is True else i for i in value_]
                    value_ = [Data(data=j, scales=scales, bound=low_or_up[i]) if isinstance(
                        j, (DataFrame, dict)) else j for i, j in enumerate(value_)]
                    value_ = sorted(value_)
                    for i in range(2):
                        if isinstance(value_[i], (float, int)):
                            bound[i], certainty[i], approach[i] = low_or_up[i], Certainty.CERTAIN, None
                        elif isinstance(value_[i], Unbound):
                            bound[i], certainty[i], approach[i] = Bound.UNBOUNDED, Certainty.CERTAIN, None
                        elif isinstance(value_[i], Data):
                            bound[i], certainty[i], approach[i] = low_or_up[i], Certainty.UNCERTAIN, Approach.DATA

            for i,j in enumerate(list(value_)):
                
                parameter = Parameter(value=j, aspect=aspect, component=component, declared_at=declared_at, scales=scales,
                                      bound=bound[i], certainty=certainty[i], approach=approach[i], temporal=TemporalDisp.get_tdisp(tempd_))
                if parameter not in self.parameters:
                    self.parameters.append(parameter)
                    
    
                for i in matches.find(aspect):
                    
                    variable = Variable(aspect=aspect, component=component, declared_at=declared_at, spatial=parameter.spatial,
                                         temporal=parameter.temporal, disposition=parameter.disposition, index=parameter.index)
                
                    if variable not in self.variables:
                        self.variables.append(variable)
                        
                    if i.associated:
                        associated = Variable(aspect=i.associated, component=component, declared_at=declared_at, spatial=parameter.spatial,
                                            temporal=parameter.temporal, disposition=parameter.disposition, index=parameter.index)
                    else:
                        associated = None
                        
                    constraint = Constraint(condition=i.condition, variable=variable,
                                         associated=associated, parameter=parameter, bound=parameter.bound)
                    
                    if constraint not in self.constraints:
                        self.constraints.append(constraint)
                    
                

        # for parameter in self.parameters:
        #     aspect = parameter.aspect
        #     for i in matches.find(aspect):
        #         variable_, associated_, parameter_, bound_= (
        #             None for _ in range(4))

                # bound_ = parameter.bound
                # print(bound_)

                # if i.variable:
                #     variable_ = Variable(aspect=aspect, component=component, declared_at=declared_at, spatial=parameter.spatial,
                #                          temporal=parameter.temporal, disposition=parameter.disposition, index=parameter.index)
                #     if variable_ not in self.variables:
                #         self.variables.append(variable_)

                # if i.associated:
                #     associated_ = Variable(aspect=i.associated, component=component, declared_at=declared_at, spatial=parameter.spatial,
                #                            temporal=parameter.temporal, disposition=parameter.disposition, index=parameter.index)

                # if i.parameter:
                #     parameter_ = parameter

                # constraint_ = Constraint(condition=i.condition, variable=variable_,
                #                          associated=associated_, parameter=parameter_, bound=bound_)

                # if constraint_ not in self.constraints:
                #     self.constraints.append(constraint_)

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


@dataclass
class AspectOver:
    aspect: Union[Limit, Loss]
    temporal: TemporalDisp

    def __post_init__(self):
        self.name = f'{self.aspect.name.lower()}_over:{self.temporal.name.lower()}'

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
