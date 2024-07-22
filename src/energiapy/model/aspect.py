
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Tuple, Union

from pandas import DataFrame

from ..components.horizon import Horizon
from ..funcs.print import printer
from .constraint import Constraint
from .parameter import Parameter
from .parameters.dataset import DataSet
from .parameters.theta import Theta
from .parameters.unbound import BigM, Unbound
from .rulebook import rulebook
from .type.aspect import CashFlow, Emission, Land, Life, Limit, Loss
from .type.bound import Bound
from .type.certainty import Approach, Certainty
from .type.condition import Condition
from .variable import Variable

if TYPE_CHECKING:
    from ..components.linkage import Linkage
    from ..components.location import Location
    from ..components.process import Process
    from ..components.resource import Resource
    from ..components.transport import Transport


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
                               DataFrame, Dict[int, DataFrame], Dict[int, DataSet], Tuple[float], Theta], aspect: Union[Limit, CashFlow, Land, Life, Loss, Emission],
            component: Union['Resource', 'Process', 'Location', 'Transport', 'Network'],
            declared_at: Union['Resource', 'Process', 'Location', 'Transport', Tuple['Location'], 'Network'], horizon: Horizon = None):

        if not isinstance(value, dict):
            value = {horizon.scales[0]: value}

        for tempd, value_ in value.items():

            if tempd == horizon.scales[0]:
                if isinstance(value_, (DataFrame, DataSet, Theta)):
                    if len(value_) in horizon.n_indices:
                        tempd = horizon.scales[horizon.n_indices.index(
                            len(value_))]
                    else:
                        raise ValueError(
                            f'{self.name}: length of data must match atleast one scale')

            bound, certainty, approach = ([None, None] for _ in range(3))

            if isinstance(value_, (float, int, DataFrame, DataSet)) and not isinstance(value_, bool):
                bound[0] = Bound.EXACT
                if isinstance(value_, (DataFrame, dict, DataSet)):
                    certainty[0], approach[0] = Certainty.UNCERTAIN, Approach.DATA
                else:
                    certainty[0], approach[0] = Certainty.CERTAIN, None

            elif isinstance(value_, (Unbound, bool)):
                bound[0], certainty[0], approach[0] = Bound.UNBOUNDED, Certainty.CERTAIN, None
                if value_ is True:
                    value_ = BigM

            elif isinstance(value_, (tuple, Theta)):
                bound[0], certainty[0], approach[0] = Bound.PARAMETRIC, Certainty.UNCERTAIN, Approach.PARAMETRIC

                if isinstance(value_, tuple) and len(value_) == 2:
                    low_or_up = {0: Bound.LOWER, 1: Bound.UPPER}
                    value_ = tuple([DataSet(data=j, horizon=horizon, bound=low_or_up[i],
                                            aspect=aspect, declared_at=declared_at,
                                            component=component) if isinstance(
                        j, (DataSet, DataFrame)) else j for i, j in enumerate(value_)])
                else:
                    raise ValueError(
                        f'{self.name}: tuple must be of length 2')

            elif isinstance(value_, list):

                if len(value_) > 2:
                    raise ValueError(
                        f'{self.name}: list can be of length 2 [lb, ub] or 1 [ub]')

                if len(value_) == 1:
                    value_ = [0] + value_

                low_or_up = {0: Bound.LOWER, 1: Bound.UPPER}
                value_ = [BigM if i is True else i for i in value_]
                value_ = [DataSet(data=j, horizon=horizon, bound=low_or_up[i]) if isinstance(
                    j, (DataFrame, DataSet)) else j for i, j in enumerate(value_)]
                value_ = sorted(value_)

                for i in range(2):
                    if isinstance(value_[i], (float, int)):
                        bound[i], certainty[i], approach[i] = low_or_up[i], Certainty.CERTAIN, None
                    elif isinstance(value_[i], Unbound):
                        bound[i], certainty[i], approach[i] = Bound.UNBOUNDED, Certainty.CERTAIN, None
                    elif isinstance(value_[i], DataSet):
                        bound[i], certainty[i], approach[i] = low_or_up[i], Certainty.UNCERTAIN, Approach.DATA

            if not isinstance(value_, list):
                value_ = [value_]

            for i, j in enumerate(list(value_)):

                for rule in rulebook.find(aspect):
                    parameter_, associated_, bound_ = (None for _ in range(3))

                    parameter = Parameter(value=j, aspect=aspect, component=component, declared_at=declared_at, horizon=horizon,
                                          bound=bound[i], certainty=certainty[i], approach=approach[i], temporal=tempd)

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
                    if rule.declared_at and declared_at.cname() != rule.declared_at:
                        continue
                    else:
                        constraint = Constraint(condition=rule.condition, variable=variable,
                                                associated=associated_, parameter=parameter_, bound=bound_, rhs=rule.rhs)
                        self.constraints = sorted(list(
                            set(self.constraints) | {constraint}))

    def params(self):
        printer(component=self, print_collection='parameters')

    def vars(self):
        printer(component=self, print_collection='variables')

    def cons(self):
        printer(component=self, print_collection='constraints')

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
