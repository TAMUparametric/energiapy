from __future__ import annotations

from dataclasses import fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..components.horizon import Horizon
    from ..model.type.alias import IsComponent, IsValue


def namer(component: IsComponent, name: str, horizon: Horizon):
    """Updates component name and horizon 
    triggers the updating of attributes to Aspect

    Args:
        component (IsComponent): energiapy component
        name (str): name of component
        horizon (Horizon): Horizon of the problem
    """
    setattr(component, 'name', name)
    setattr(component, 'horizon', horizon)
    setattr(component, 'named', True)

    for i in fields(component):
        attr = i.name.lower()
        if hasattr(component, attr) and getattr(component, attr) is not None:
            setattr(component, attr, getattr(component, attr))


def is_named(component: IsComponent, attr_value: IsValue) -> bool:
    """Checks if attribute is ready to be made into an Aspect

    Args:
        component (IsComponent): energiapy component
        attr_value (IsValue): value assigned to aspect attribute

    Returns:
        bool: True if component is ready and value is assigned
    """
    cndtn_named = hasattr(component, 'named') and getattr(component, 'named')
    cndtn_value = attr_value is not None

    if cndtn_named and cndtn_value:
        return True
    else:
        return False
