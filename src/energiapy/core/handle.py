"""General class with functions for handling aspects
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..funcs.input.aspect import aspecter, aspectshareder


if TYPE_CHECKING:
    from ..type.alias import IsAspect, IsInput


def make_value(name: str, value: IsInput, index: IsIndex, bound: Bound, derived: IsDerived = None,
               commodity: IsCommodity = None, operation: IsOperation = None,
               spatial: IsSpatial = None) -> IsValue:
    """Converts a value to a Value object

    Args:
        name (str): name of the value
        value (IsInput): input value
        index (IsIndex): index of the value
        bound (Bound): bound of the value [UPPER, LOWER, EXACT]
        derived (IsDerived, optional): Derived Commodity. Defaults to None.
        commodity (IsCommmodity, optional): Commodity. Defaults to None.
        operation (IsOperation, optional): Operation. Defaults to None.
        spatial (IsSpatial, optional): Spatial. Defaults to None.

    Returns:
        IsValue: Value object
    """

    args = {'name': name, 'index': index, 'bound': bound, 'derived': derived, 'commodity': commodity,
            'operation': operation, 'spatial': spatial}

    if isinstance(value, (float, int)):
        return Number(number=value, **args)

    if isinstance(value, bool):
        return M(big=value, **args)

    if isinstance(value, DataFrame):
        return DataSet(data=value, **args)

    if isinstance(value, tuple):
        return Theta(space=value, **args)

    # if passing a BigM or Th, update
    if hasattr(value, 'big') or hasattr(value, 'space'):
        for i, j in args.items():
            setattr(value, i, j)
        return value


def make_aspect(self, attr_name: str, attr_value: IsInput) -> IsAspect:
    """Makes Aspect from component attribute

    Args:
        attr_name (str): name of the attribute
        attr_value (IsInput): value of the attribute

    Returns:
        IsAspect: Aspect subclass
    """
    current_value = getattr(self, attr_name)

    # Checks if attribute is already an Aspect
    if hasattr(current_value, '_aspected'):
        aspect = current_value
    # if not make an Aspect
    else:
        aspect = aspect_map[attr_name](component=self)

    # TODO - see if needs if not isinstance(attr_value, Aspect):
    # add value to the aspect and update it in the component
    aspect.add_value()
    setattr(self, attr_name, aspect)

    # update the model elements in the component
    update_element(component=self, aspect=aspect)


def make_aspectshared(self, attr_name: str):
    """Makes AspectShared

    Args:
        attr_name (str): name of the attribute
    """
    aspectshareder(component=self, attr_name=attr_name)


def add_value(self, value: IsInput, aspect: IsAspect, component: IsComponent, declared_at: IsDeclaredAt, horizon: Horizon = None):
    """Add a value to an already existing Aspect

    Args:
        value (IsInput): the value to be made into Aspect
        aspect (IsAspect): Component attribute 
        component (IsComponent): energiapy Component
        declared_at (IsDeclaredAt): energiapy Component
        horizon (Horizon, optional): declared planning Horizon. Defaults to None.

    Raises:
        ValueError: length of data must match one of the scales
        ValueError: tuple must be of length 2
        ValueError: list can be of length 2 [lb, ub] or 1 [ub]
    """
    # The native form of a value is {IsScale: IsInput}
    # if no temporal scale attached, set to parent scale t0 for now
    # if DataSet, DataFrame, or Theta the length is used to assign appropriate Scale

    if not isinstance(value, dict):
        tempval = {horizon.scales[0]: make_value(value)}

    for scale_, value_ in tempval.items():

        # if on parent scale, and value has non unity length, find a scale that matches
        if is_(scale_, horizon.scales[0]):
            if isinstance(value_, (DataFrame, Theta)):
                if len(value_) in horizon.n_indices:
                    scale_ = horizon.scales[horizon.n_indices.index(
                        len(value_))]
                else:
                    raise ValueError(
                        f'{self.name}: length of data must match atleast one scale')
        # [lower, upper] bound value, certainty of the bound, and approach to tackle uncertainty

        if isinstance(value_, Number):
            bound, certainty, approach = Bound.EXACT, Certainty.CERTAIN, None
            
        if isinstance(value_, DataSet):
            bound, certainty, approach = Bound.EXACT, Certainty.UNCERTAIN, Approach.DATA

        elif isinstance(value_, M):
            bound, certainty, approach = Bound.UNBOUNDED, Certainty.CERTAIN, None

        elif isinstance(value_, Theta):
            bound, certainty, approach = Bound.PARAMETRIC, Certainty.UNCERTAIN, Approach.PARAMETRIC

        elif isinstance(value_, list):
            bound, certainty, approach = ([None, None] for _ in range(3))

            if len(value_) > 2:
                raise ValueError(
                    f'{self.name}: list can be of length 2 [lb, ub] or 1 [ub]')
            # if only one value, then it is an upper bound
            if len(value_) == 1:
                value_ = [0] + value_

            low_or_up = {0: Bound.LOWER, 1: Bound.UPPER}
            # if true then make BigM
            value_ = [BigM if i is True else i for i in value_]
            # if DataSet or DataFrame, make local DataSet or else keep numeric values
            value_ = [DataSet(data=j, horizon=horizon, bound=low_or_up[i]) if isinstance(
                j, (DataFrame, DataSet)) else j for i, j in enumerate(value_)]
            # sorting is done by looking at the bound type
            value_ = sorted(value_)

            for i in range(2):
                # if numeric, the exact value is known
                if isinstance(value_[i], (float, int)):
                    bound[i], certainty[i], approach[i] = low_or_up[i], Certainty.CERTAIN, None
                # if BigM, then it is unbounded but certain
                elif isinstance(value_[i], M):
                    bound[i], certainty[i], approach[i] = Bound.UNBOUNDED, Certainty.CERTAIN, None
                # if DataSet, then it is uncertain but there is deterministic data to model it
                elif isinstance(value_[i], DataSet):
                    bound[i], certainty[i], approach[i] = low_or_up[i], Certainty.UNCERTAIN, Approach.DATA
            tempval[scale_] = value_
    return tempval, bound, certainty, approach


def update_element(self, value: Dict[IsScale, IsInput]: component: IsComponent, aspect: IsAspect, horizon: IsHorizon, bound: Bound, certainty: Certainty, approach: Approach):
    for scale_, value_ in value.items():
        for i, j in enumerate(list(value_)):
            for rule in rulebook.find(aspect):
                parameter_, associated_, bound_ = (None for _ in range(3))

                parameter = Parameter(value=j, aspect=aspect, component=component, declared_at=declared_at, horizon=horizon,
                                      bound=bound[i], certainty=certainty[i], approach=approach[i], temporal=scale_)

                variable = Variable(aspect=aspect, component=component,
                                    declared_at=declared_at, temporal=parameter.temporal)

                self.parameters = sorted(
                    set(self.parameters) | {parameter})
                self.variables = sorted(set(self.variables) | {variable})

                if rule.associated:
                    associated_ = Variable(
                        aspect=rule.associated, component=component, declared_at=declared_at, temporal=parameter.temporal)

                if rule.parameter:
                    parameter_ = parameter

                if is_(rule.condition, Condition.BIND):
                    bound_ = parameter.bound
                if rule.declared_at and is_not(declared_at.cname(), rule.declared_at):
                    continue
                else:
                    constraint = Constraint(condition=rule.condition, variable=variable,
                                            associated=associated_, declared_at=declared_at, parameter=parameter_, bound=bound_, rhs=rule.rhs)
                    self.constraints = sorted(
                        set(self.constraints) | {constraint})
