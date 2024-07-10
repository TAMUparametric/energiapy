
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from pandas import DataFrame

from ..components.temporal_scale import TemporalScale
from .constraint import Constraint
from .data import Data
from .parameter import Parameter
from .rulebook import rulebook
from .theta import Theta
from .type.aspect import CashFlow, Emission, Land, Life, Limit, Loss
from .type.bound import Bound
from .type.certainty import Approach, Certainty
from .type.condition import Condition
from .type.disposition import TemporalDisp
from .unbound import BigM, Unbound
from .variable import Variable


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
            if scales is None:
                raise ValueError(
                    f'{self.name}: please provide {component}.scales = scales, where scales is a TemporalScale object')
            elif not all(i in scales.scales for i in value):
                raise ValueError(
                    f'{self.name}: keys for dict must be within scales.scales, where scales is a TemporalScale object')

        else:
            value = {'t0': value}

        for tempd, value_ in value.items():

            bound, certainty, approach = ([None, None] for _ in range(3))

            if isinstance(value_, (float, int, DataFrame, Data)) and not isinstance(value_, bool):
                bound[0] = Bound.EXACT
                if isinstance(value_, (DataFrame, dict, Data)):
                    certainty[0], approach[0] = Certainty.UNCERTAIN, Approach.DATA
                else:
                    certainty[0], approach[0] = Certainty.CERTAIN, None

            elif isinstance(value_, (Unbound, bool)):
                bound[0], certainty[0], approach[0] = Bound.UNBOUNDED, Certainty.CERTAIN, None
                if value_ is True:
                    value_ = BigM

            elif isinstance(value_, (tuple, Theta)):
                bound[0], certainty[0], approach[0] = Bound.PARAMETRIC, Certainty.UNCERTAIN, Approach.PARAMETRIC
                if len(value_) != 2:
                    raise ValueError(
                        f'{self.name}: values must a tuple of length 2')
                low_or_up = {0: Bound.LOWER, 1: Bound.UPPER}
                value_ = tuple([Data(data=j, scales=scales, bound=low_or_up[i],
                                     aspect=aspect, declared_at=declared_at,
                                     component=component) if isinstance(
                    j, (Data, DataFrame)) else j for i, j in enumerate(value_)])

            elif isinstance(value_, list):

                if len(value_) > 2:
                    raise ValueError(
                        f'{self.name}: list can be of length 2 [lb, ub] or 1 [ub]')

                if len(value_) == 1:
                    value_ = [0] + value_

                low_or_up = {0: Bound.LOWER, 1: Bound.UPPER}
                value_ = [BigM if i is True else i for i in value_]
                value_ = [Data(data=j, scales=scales, bound=low_or_up[i]) if isinstance(
                    j, (DataFrame, Data)) else j for i, j in enumerate(value_)]
                value_ = sorted(value_)

                for i in range(2):
                    if isinstance(value_[i], (float, int)):
                        bound[i], certainty[i], approach[i] = low_or_up[i], Certainty.CERTAIN, None
                    elif isinstance(value_[i], Unbound):
                        bound[i], certainty[i], approach[i] = Bound.UNBOUNDED, Certainty.CERTAIN, None
                    elif isinstance(value_[i], Data):
                        bound[i], certainty[i], approach[i] = low_or_up[i], Certainty.UNCERTAIN, Approach.DATA

            if not isinstance(value_, list):
                value_ = [value_]

            for i, j in enumerate(list(value_)):

                for rule in rulebook.find(aspect):

                    parameter_, associated_, bound_ = (None for _ in range(3))

                    parameter = Parameter(value=j, aspect=aspect, component=component, declared_at=declared_at, scales=scales,
                                          bound=bound[i], certainty=certainty[i], approach=approach[i], temporal=TemporalDisp.get_tdisp(tempd))
                    
                    if isinstance(parameter.value, (Data, Theta)) and len(parameter.value) != scales.index_n_dict[tempd]:
                        raise ValueError(
                            f'{self.name}: length of data does not match scale index')
                    
                    variable = Variable(aspect=aspect, component=component, declared_at=declared_at, spatial=parameter.spatial,
                                        temporal=parameter.temporal, disposition=parameter.disposition, index=parameter.index)

                    self.parameters = sorted(
                        list(set(self.parameters) | {parameter}))
                    self.variables = sorted(
                        list(set(self.variables) | {variable}))

                    if rule.associated:
                        associated_ = Variable(aspect=rule.associated, component=component, declared_at=declared_at, spatial=parameter.spatial,
                                               temporal=parameter.temporal, disposition=parameter.disposition, index=parameter.index)
                    if rule.parameter:
                        parameter_ = parameter

                    if rule.condition == Condition.BIND:
                        bound_ = parameter.bound

                    if rule.declared_at and declared_at.class_name() != rule.declared_at:
                        continue
                    else:
                        constraint = Constraint(condition=rule.condition, variable=variable,
                                                associated=associated_, parameter=parameter_, bound=bound_, rhs=rule.rhs)

                        self.constraints = sorted(list(
                            set(self.constraints) | {constraint}))

    def params(self):
        """prints parameters
        """
        for i in getattr(self, 'parameters'):
            print(i)

    def vars(self):
        """prints variables
        """
        for i in getattr(self, 'variables'):
            print(i)

    def cons(self):
        """prints constraints
        """
        for i in getattr(self, 'constraints'):
            print(i)

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
