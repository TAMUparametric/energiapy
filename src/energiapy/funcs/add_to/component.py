from __future__ import annotations

from typing import TYPE_CHECKING
from warnings import warn

if TYPE_CHECKING:
    from ...types.alias import IsComponent, IsScenario


def add_component(to: IsComponent, list_attr: str, add: IsComponent):
    """Updates the lists of components in the scenario.

    Args:
        to (IsComponent): The scenario to which the component is added.
        list_attr (str): The name of the attribute representing the list of components.
        add (IsComponent): The component to be added to the list.
    """
    list_curr = getattr(to, list_attr)
    if add in list_curr:
        warn(f'{add} is being replaced in Scenario')
    # add component to list
    setattr(to, list_attr, sorted(set(list_curr) | {add}))
