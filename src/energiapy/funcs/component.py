"""functions for Components 
"""

from __future__ import annotations

from dataclasses import fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..components.horizon import Horizon
    from ..model.type.alias import IsComponent, IsValue, IsAspect


def initializer(component: IsComponent):
    """sets some common attributes of a component to None or empty list

    Args:
        component (IsComponent): energiapy Component
    """

    for i in ['_named', 'name', 'horizon']:
        setattr(component, i, None)

    setattr(component, 'declared_at', component)

    if not hasattr(component, 'ctypes'):
        setattr(component, 'ctypes', list())



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
    setattr(component, '_named', True)

    for i in fields(component):
        attr = i.name.lower()
        if hasattr(component, attr) and getattr(component, attr) is not None:
            setattr(component, attr, getattr(component, attr))



