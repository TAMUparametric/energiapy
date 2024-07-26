from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pandas import DataFrame

from ..core.general import ClassName, Dunders, Magics
from ..core.onset import ElementCols
from ..type.element.bound import Bound
from ..type.element.certainty import Approach, Certainty
from ..type.element.condition import Condition
from .constraint import Constraint
from .parameter import Parameter
from .rulebook import rulebook
from .specialparams.dataset import DataSet
from .specialparams.theta import Theta
from .specialparams.unbound import BigM, Unbound
from .variable import Variable

if TYPE_CHECKING:
    from ..components.horizon import Horizon
    from ..type.alias import (IsAspect, IsAspectDict, IsComponent,
                              IsDeclaredAt, IsTemporal, IsValue)


@dataclass
class Aspect(ElementCols, ClassName, Dunders, Magics):
    aspect: IsAspect
    component: IsComponent

    def __post_init__(self):
        super().__post_init__()
        self.name = f'{self.aspect.name.lower()}({self.component.name})'

    def add(self, value: IsValue, aspect: IsAspect, component: IsComponent, declared_at: IsDeclaredAt, horizon: Horizon = None):
        """Add a value to an already existing Aspect

        Args:
            value (IsValue): the value to be made into Aspect
            aspect (IsAspect): Component attribute 
            component (IsComponent): energiapy Component
            declared_at (IsDeclaredAt): energiapy Component
            horizon (Horizon, optional): declared planning Horizon. Defaults to None.

        Raises:
            ValueError: length of data must match one of the scales
            ValueError: tuple must be of length 2
            ValueError: list can be of length 2 [lb, ub] or 1 [ub]
        """
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

                    variable = Variable(aspect=aspect, component=component,
                                        declared_at=declared_at, temporal=parameter.temporal)

                    self.parameters = sorted(
                        set(self.parameters) | {parameter})
                    self.variables = sorted(set(self.variables) | {variable})

                    # setattr(self, 'parameters', getattr(
                    #     self, 'parameters').append(parameter))
                    # setattr(self, 'variables', getattr(
                    #     self, 'variables').append(variable))

                    if rule.associated:
                        associated_ = Variable(
                            aspect=rule.associated, component=component, declared_at=declared_at, temporal=parameter.temporal)

                    if rule.parameter:
                        parameter_ = parameter

                    if rule.condition == Condition.BIND:
                        bound_ = parameter.bound
                    if rule.declared_at and declared_at.cname() != rule.declared_at:
                        continue
                    else:
                        constraint = Constraint(condition=rule.condition, variable=variable,
                                                associated=associated_, declared_at=declared_at, parameter=parameter_, bound=bound_, rhs=rule.rhs)
                        self.constraints = sorted(
                            set(self.constraints) | {constraint})
                        # setattr(self, 'constraints', getattr(
                        #     self, 'constraints').append(constraint))


@dataclass
class AspectDict(ElementCols, Dunders, Magics, ClassName):
    aspect: IsAspect
    component: IsComponent
    aspects: IsAspectDict

    def __post_init__(self):

        self.name = f'{self.aspect.name.lower()}({self.component.name})'

        for i in ['parameters', 'variables', 'constraints']:
            setattr(
                self, i, [mod for comp in self.aspects for mod in getattr(comp, i) if mod.declared_at == self.component])
