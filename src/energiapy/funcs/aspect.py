from __future__ import annotations

from typing import TYPE_CHECKING

from ..model.aspect import Aspect, AspectDict
from ..model.type.input import Input

if TYPE_CHECKING:
    from ..model.type.alias import IsAspectDict, IsComponent, IsValue


def aspecter(component: IsComponent, attr_name: str, attr_value: IsValue):
    """updates the attribute as an Aspect

    Args:
        component: energiapy component
        attr_name (str): name of the attribute
        attr_value: value of the attribute 
    """
    current_value = getattr(component, attr_name)

    if not isinstance(current_value, Aspect):
        new_value = Aspect(
            aspect=Input.match(attr_name), component=component)
    else:
        new_value = current_value

    if not isinstance(attr_value, Aspect):
        new_value.add(value=attr_value, aspect=Input.match(attr_name), component=component,
                      horizon=component.horizon, declared_at=component.declared_at)
        setattr(component, attr_name, new_value)

        for i in ['parameters', 'variables', 'constraints']:
            if hasattr(new_value, i):
                setattr(component, i, getattr(component, i)
                        + getattr(new_value, i))


def aspectdicter(component: IsComponent, attr_name: str, attr_value: IsAspectDict):
    """updates the attribute as an Aspect

    Args:
        component: energiapy component
        attr_name (str): name of the attribute
        attr_value: value of the attribute 
    """

    new_value = AspectDict(
        aspect=Input.match(attr_name), component=component,  aspects=attr_value)
    setattr(component, attr_name, new_value)

    for i in ['parameters', 'variables', 'constraints']:
        setattr(component, i, getattr(component, i) + getattr(new_value, i))
