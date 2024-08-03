from __future__ import annotations

from dataclasses import fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..._core._aliases._component import IsComponent, IsHorizon, IsNetwork


def update_name(component: IsComponent, name: str, horizon: IsHorizon, network: IsNetwork):
    """names and adds horizon to the Resource

    Args:
        component(IsComponent): component to be named
        name (str): name given as Scenario.name = Resource(...)
        horizon (Horizon): temporal horizon
    """

    setattr(component, 'name', name)

    if horizon:
        setattr(component, '_horizon', horizon)
    if network:
        setattr(component, '_network', network)

    for i in fields(component):
        attr = i.name.lower()
        if hasattr(component, attr) and getattr(component, attr) is not None:
            setattr(component, attr, getattr(component, attr))
