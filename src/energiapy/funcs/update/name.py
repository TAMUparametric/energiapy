from __future__ import annotations

from dataclasses import fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...types.alias import IsComponent, IsHorizon


def update_name(component: IsComponent, name: str, horizon: IsHorizon):
    """names and adds horizon to the Resource

    Args:
        component(IsComponent): component to be named
        name (str): name given as Scenario.name = Resource(...)
        horizon (Horizon): temporal horizon
    """

    setattr(component, 'name', name)
    setattr(component, 'horizon', horizon)
    setattr(component, '_named', True)

    for i in fields(component):
        attr = i.name.lower()
        if hasattr(component, attr) and getattr(component, attr) is not None:
            setattr(component, attr, getattr(component, attr))
