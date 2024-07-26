from __future__ import annotations

from typing import TYPE_CHECKING

from ..funcs.model import model_updater
from ..model.aspect import Aspect, AspectDict
from ..model.type.input import Input

if TYPE_CHECKING:
    from ..model.type.alias import IsAspect, IsAspectDict, IsComponent, IsValue


def aspecter(component: IsComponent, attr_name: str, attr_value: IsValue) -> IsAspect:
    """updates the attribute as an Aspect

    Args:
        component: energiapy component
        attr_name (str): name of the attribute
        attr_value: value of the attribute 

    Returns:
        IsAspect: Aspect
    """
    current_value = getattr(component, attr_name)

    if not isinstance(current_value, Aspect):  # if Aspect has not been created
        new_value = Aspect(
            aspect=Input.match(attr_name), component=component)
    else:
        new_value = current_value

    if not isinstance(attr_value, Aspect):  # if not passing an Aspect
        new_value.add(value=attr_value, aspect=Input.match(attr_name), component=component,
                      horizon=component.horizon, declared_at=component.declared_at)
        setattr(component, attr_name, new_value)

        model_updater(component=component, aspect=new_value)


def aspectdicter(component: IsComponent, attr_name: str) -> IsAspectDict:
    """updates the attribute as an Aspect

    Args:
        component: energiapy component
        attr_name (str): name of the attribute
        attr_value: value of the attribute 

    Returns:
        IsAspectDict: AspectDict (a dictionary of Aspects)
    """

    current_value = getattr(component, attr_name)

    if isinstance(current_value, dict):
        for j in current_value:
            j.declared_at = component
            aspecter(component=j, attr_name=attr_name,
                     attr_value=current_value[j])
            # setattr(j, attr_name, current_value[j])

        new_value = AspectDict(
            aspect=Input.match(attr_name), component=component,  aspects={
                j: getattr(j, attr_name) for j in current_value})
        setattr(component, attr_name, new_value)

        model_updater(component=component, aspect=new_value)
