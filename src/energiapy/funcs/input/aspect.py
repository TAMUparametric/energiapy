from __future__ import annotations

from typing import TYPE_CHECKING

from ...inputs.aspect import Aspect
from ...inputs.aspect_shared import AspectShared
from ...inputs.input_map import input_map
from ..component.update import update_element

if TYPE_CHECKING:
    from ...type.alias import IsAspect, IsAspectShared, IsComponent, IsInput


def aspecter(component: IsComponent, attr_name: str, attr_value: IsInput) -> IsAspect:
    """updates the attribute to make an Aspect

    Args:
        component: energiapy component
        attr_name (str): name of the attribute
        attr_value: value of the attribute

    Returns:
        IsAspect: Aspect
    """
    current_value = getattr(component, attr_name)

    # Checks if attribute is already an Aspect
    if hasattr(current_value, '_aspected'):
        aspect = current_value
    # if not make an Aspect
    else:
        aspect = aspect_map[attr_name](component=component)

    # TODO - see if needs if not isinstance(attr_value, Aspect):
    # add value to the aspect and update it in the component
    aspect.add(
        value=attr_value,
        aspect=input_map.find_aspect(attr_name),
        component=component,
        horizon=component.horizon,
        declared_at=component.declared_at,
    )
    setattr(component, attr_name, aspect)

    # update the model elements in the component
    update_element(component=component, aspect=aspect)


def aspectshareder(component: IsComponent, attr_name: str) -> IsAspectShared:
    """updates the attribute as an Aspect

    Args:
        component: energiapy component
        attr_name (str): name of the attribute
        attr_value: value of the attribute

    Returns:
        IsAspectShared: AspectShared (a dictionary of AspectMap)
    """

    current_value = getattr(component, attr_name)

    if isinstance(current_value, dict):
        for j in current_value:
            j.declared_at = component
            aspecter(component=j, attr_name=attr_name, attr_value=current_value[j])
            # setattr(j, attr_name, current_value[j])

        new_value = AspectShared(
            aspect=input_map.find_aspect(attr_name),
            component=component,
            aspects={j: getattr(j, attr_name) for j in current_value},
        )
        setattr(component, attr_name, new_value)

        update_element(component=component, aspect=new_value)
